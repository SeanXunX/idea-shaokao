#!/usr/bin/env python3
"""Run, resume, or dispatch the portable research-to-acceptance workflow."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from shaokao import contracts as C
from shaokao.conference import extract_form, fetch_sources, validate_rubric
from shaokao.engine import Store, atomic, envelope, pending


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    atomic(Path(path), json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n')


def run(store, command, max_steps=100, timeout=600):
    C.require(isinstance(command, list) and command and all(isinstance(s, str) for s in command), '--agent-command must be a JSON argv array; no shell interpolation')
    completed = 0
    for _ in range(max_steps):
        tasks = pending(store.project)
        if not tasks:
            break
        task = tasks[0]
        if task['stage'] == 'rubric':
            raise C.ContractError('official rubric is pending: fetch sources, extract/verify the rubric, then install it')
        packet = envelope(store.project, task)
        try:
            process = subprocess.run(command, input=json.dumps(packet), capture_output=True,
                                     text=True, timeout=timeout, cwd=store.root)
            C.require(process.returncode == 0, f'agent exited {process.returncode}: {process.stderr[-2000:]}')
            C.require(len(process.stdout.encode()) <= 4 * 1024 * 1024, 'agent response exceeds 4 MiB')
            response = json.loads(process.stdout)
            store.submit(response)
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            store.failure(task, str(error))
            raise C.ContractError(f'{task["id"]} remains pending: {error}') from error
        completed += 1
        print(json.dumps({'completed_task': task['id'], 'status': store.project['status']}), file=sys.stderr, flush=True)
    return {'completed_tasks': completed, 'status': store.project['status'], 'pending': pending(store.project)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init', help='create a new persistent schema-2 research project')
    init.add_argument('workspace', type=Path)
    init.add_argument('--topic', required=True)
    init.add_argument('--conference', required=True)
    init.add_argument('--year', required=True, type=int)
    init.add_argument('--track', required=True)
    init.add_argument('--max-rounds', type=int, default=4)
    init.add_argument('--max-stress-iterations', type=int, default=3)
    init.add_argument('--reviewers', type=int, choices=(3, 4), default=4)
    init.add_argument('--acceptance-rounds', type=int, default=2)
    init.add_argument('--constraints', default='')
    init.add_argument('--contribution-type', help='exact official contribution-type ID, when the venue defines categories')
    init.add_argument('--mode', choices=('independent', 'external_review', 'single_agent'), default='independent')
    for name in ('status', 'verify', 'packet', 'submit', 'install-rubric', 'run', 'render', 'change-target', 'select-contribution-type'):
        sub = commands.add_parser(name)
        sub.add_argument('workspace', type=Path)
        if name == 'packet':
            sub.add_argument('--task', help='task ID; defaults to first pending task')
            sub.add_argument('--output', type=Path)
        if name in ('submit', 'install-rubric'):
            sub.add_argument('input', type=Path)
        if name == 'run':
            sub.add_argument('--agent-command', required=True, help='JSON argv array; fresh process per role; JSON stdin/stdout')
            sub.add_argument('--max-steps', type=int, default=100)
            sub.add_argument('--timeout', type=int, default=600)
        if name == 'select-contribution-type':
            sub.add_argument('contribution_type')
        if name == 'change-target':
            sub.add_argument('--conference', required=True)
            sub.add_argument('--year', type=int, required=True)
            sub.add_argument('--track', required=True)
    fetch = commands.add_parser('fetch-sources')
    fetch.add_argument('manifest', type=Path)
    fetch.add_argument('--output', type=Path, required=True)
    extract = commands.add_parser('extract-form')
    extract.add_argument('bundle', type=Path)
    extract.add_argument('--source', required=True)
    extract.add_argument('--start', help='HTML form section heading; omit for OpenReview JSON')
    extract.add_argument('--end')
    extract.add_argument('--output', type=Path, required=True)
    compile_rubric = commands.add_parser('build-rubric')
    compile_rubric.add_argument('bundle', type=Path)
    compile_rubric.add_argument('specification', type=Path, help='evidence-linked extraction and procedural configuration')
    compile_rubric.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'fetch-sources':
            bundle = fetch_sources(read(args.manifest))
            write(args.output, bundle)
            result = {'output': str(args.output), 'sources': [{'id': s['id'], 'status': s['status'], 'error': s.get('error')} for s in bundle['sources']]}
        elif args.command == 'extract-form':
            result = extract_form(read(args.bundle), args.source, args.start, args.end)
            write(args.output, result)
            result = {'output': str(args.output), 'fields': len(result), 'status': 'candidate; verify procedures and uncertainties before installation'}
        elif args.command == 'build-rubric':
            bundle, spec = read(args.bundle), read(args.specification)
            C.require(not set(spec).intersection(('sources', 'official_domains', 'conference', 'schema_version')), 'specification cannot replace fetched identity or evidence')
            result = dict(bundle, **spec)
            extraction = result['form_extraction']
            result['fields'] = extract_form(bundle, extraction['source_id'], extraction.get('start'), extraction.get('end'))
            validate_rubric(result)
            write(args.output, result)
            result = {'output': str(args.output), 'rubric_sha256': C.digest(result), 'historical': result['historical']}
        elif args.command == 'init':
            store = Store.create(args.workspace, args.topic,
                {'name': args.conference, 'year': args.year, 'track': args.track},
                {'max_rounds': args.max_rounds, 'max_stress_iterations': args.max_stress_iterations,
                 'reviewers': args.reviewers, 'acceptance_rounds': args.acceptance_rounds,
                 'constraints': args.constraints, 'execution_mode': args.mode, 'contribution_type': args.contribution_type})
            result = {'workspace': str(store.root), 'status': store.project['status'], 'pending': pending(store.project)}
        else:
            store = Store(args.workspace)
            C.require(store.project is not None, 'not a schema-2 engine workspace; legacy reports remain supported by render_review.py')
            if args.command == 'status':
                result = {'status': store.project['status'], 'rounds': len(store.project['rounds']), 'pending': pending(store.project), 'failures': store.project['failures']}
            elif args.command == 'verify':
                store.checkpoint()
                result = {'events': store.sequence, 'head_sha256': store.head, 'status': store.project['status'], 'checkpoint_rebuilt': True}
            elif args.command == 'install-rubric':
                store.install_rubric(read(args.input))
                result = {'status': store.project['status'], 'pending': pending(store.project)}
            elif args.command == 'packet':
                task = next((t for t in pending(store.project) if args.task is None or args.task == t['id']), None)
                C.require(task is not None and task['stage'] != 'rubric', 'no matching research task; install the verified official rubric first')
                result = envelope(store.project, task)
                if args.output:
                    write(args.output, result)
                    result = {'packet': str(args.output), 'task': task}
            elif args.command == 'submit':
                result = {'pending': store.submit(read(args.input)), 'status': store.project['status']}
            elif args.command == 'select-contribution-type':
                store.select_contribution_type(args.contribution_type)
                result = {'contribution_type': args.contribution_type, 'pending': pending(store.project)}
            elif args.command == 'change-target':
                store.change_target({'name': args.conference, 'year': args.year, 'track': args.track})
                result = {'status': store.project['status'], 'pending': pending(store.project)}
            elif args.command == 'run':
                C.require(args.max_steps > 0 and args.timeout > 0, 'step and timeout budgets must be positive')
                result = run(store, json.loads(args.agent_command), args.max_steps, args.timeout)
            elif args.command == 'render':
                from shaokao.report import render
                result = render(store)
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return 0
    except (C.ContractError, OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    sys.exit(main())
