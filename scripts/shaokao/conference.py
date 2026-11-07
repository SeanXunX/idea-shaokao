"""Versioned official-source acquisition and exact, evidence-checked review forms.

No venue scores are built in. HTML extraction is a candidate: a host researcher
must supply and verify procedural evidence before the rubric can be installed.
"""
from datetime import datetime, timezone
from html.parser import HTMLParser
import ipaddress
import json
import re
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .contracts import ContractError, digest, fields, items, obj, require, text, unique, url

MAX_BYTES = 4 * 1024 * 1024


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def normalize(value):
    return ' '.join(value.split())


class SourceHTML(HTMLParser):
    """Keep heading boundaries and list items while ignoring scripts/navigation."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines, self.buf, self.skip = [], '', 0

    def flush(self):
        value = normalize(self.buf)
        if value:
            self.lines.append(value)
        self.buf = ''

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1
        if self.skip:
            return
        if re.fullmatch(r'h[1-6]', tag):
            self.flush()
            self.buf = '#' * int(tag[1]) + ' '
        elif tag in ('p', 'li', 'br', 'div', 'tr'):
            self.flush()
            if tag == 'li':
                self.buf = '- '

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip = max(0, self.skip - 1)
        if not self.skip and (re.fullmatch(r'h[1-6]', tag) or tag in ('p', 'li', 'div', 'tr')):
            self.flush()

    def handle_data(self, data):
        if not self.skip:
            self.buf += data


def source_text(raw):
    try:
        json.loads(raw)
        return raw
    except ValueError:
        parser = SourceHTML()
        parser.feed(raw)
        parser.flush()
        return '\n'.join(parser.lines)


def fetch_sources(manifest, opener=None):
    """Record successful and failed requests; no stale fallback or hidden retry."""
    fields(manifest.get('conference'), ('name', 'track'), 'conference')
    require(type(manifest['conference'].get('year')) is int, 'conference.year must be an integer')
    domains = items(manifest.get('official_domains'), 'official_domains', 1)
    for domain in domains:
        text(domain, 'official domain')
        require('/' not in domain and ':' not in domain and domain != 'localhost', 'use an exact official domain')
        try:
            ipaddress.ip_address(domain)
        except ValueError:
            pass
        else:
            raise ContractError('official_domains cannot be IP addresses')
    sources = items(manifest.get('sources'), 'sources', 1)
    unique(sources, 'sources')
    records = []
    for spec in sources:
        fields(spec, ('id', 'kind', 'track'), 'source spec')
        url(spec.get('url'), 'source.url')
        require(urlparse(spec['url']).hostname in domains, 'source domain is not in the explicit official-domain allowlist')
        row = dict(spec, retrieved_at=now(), status='failed')
        try:
            request = Request(spec['url'], headers={'User-Agent': 'IdeaShaokao/2 (official review rubric research)'})
            with (opener or urlopen)(request, timeout=30) as response:
                final_url = response.geturl()
                require(urlparse(final_url).scheme == 'https' and urlparse(final_url).hostname in domains, 'official source redirected outside its declared domains')
                raw = response.read(MAX_BYTES + 1)
                require(len(raw) <= MAX_BYTES, 'official source is larger than 4 MiB')
                content = raw.decode('utf-8')
                row.update(status='ok', final_url=final_url, text=source_text(content), raw=content)
                row['sha256'] = digest({'raw': content})
        except Exception as error:
            row['error'] = f'{type(error).__name__}: {error}'
        records.append(row)
    return {'schema_version': 2, 'conference': manifest['conference'], 'official_domains': domains,
            'retrieved_at': now(), 'sources': records}


def html_fields(source, start, end=None):
    lines = source['text'].splitlines()
    begin = next((i for i, line in enumerate(lines) if line.lstrip('# ').strip() == start and line.startswith('#')), None)
    require(begin is not None, 'form section heading was not found: ' + start)
    stop = next((i for i in range(begin + 1, len(lines)) if end and lines[i].lstrip('# ').strip() == end and lines[i].startswith('#')), len(lines))
    body = lines[begin + 1:stop]
    levels = [len(line) - len(line.lstrip('#')) for line in body if line.startswith('#')]
    require(bool(levels), 'no form field headings found')
    # Field headings are the deepest level, not sub-track section headings.
    depth = max(levels)
    positions = [i for i, line in enumerate(body) if line.startswith('#' * depth + ' ')]
    rows = []
    for n, i in enumerate(positions):
        name = body[i].lstrip('# ').strip()
        excerpt = body[i + 1:positions[n + 1] if n + 1 < len(positions) else len(body)]
        options = []
        for line in excerpt:
            match = re.fullmatch(r'-\s+(-?\d+(?:\.\d+)?):\s*(.+)', line)
            if match:
                number = float(match[1]) if '.' in match[1] else int(match[1])
                options.append({'value': number, 'label': match[2], 'description': match[2]})
        # Unnumbered items can be guidance rather than form options; never infer.
        rows.append({'id': re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_'), 'name': name,
                     'kind': 'choice' if options else 'text', 'options': options,
                     'required': True, 'requirement_scope': 'internal_completeness',
                     'official_required': None, 'phase': 'final' if 'Post-Rebuttal' in name else 'both',
                     'source_id': source['id'], 'anchor': name,
                     'description': '\n'.join(excerpt), 'extraction': 'html_headings'})
    unique(rows, 'extracted fields')
    return rows


def openreview_fields(source):
    raw = json.loads(source['raw'])
    invitation = raw.get('invitations', [raw])[0]
    content = invitation.get('edit', {}).get('note', {}).get('content') or invitation.get('reply', {}).get('content')
    require(isinstance(content, dict), 'no OpenReview invitation content schema found')
    rows = []
    for key, value in content.items():
        spec = value.get('value', value)
        if not isinstance(spec, dict):
            continue
        params = spec.get('param', spec)
        enum = params.get('enum')
        if enum is None and params.get('type') == 'boolean':
            enum = [True, False]
        kind = 'multi_choice' if params.get('type') == 'string[]' and enum else 'choice' if enum else 'text'
        rows.append({'id': key, 'name': key.replace('_', ' ').title(), 'kind': kind,
                     'options': [{'value': v, 'label': str(v), 'description': str(v)} for v in enum or []],
                     'required': not params.get('optional', False), 'official_required': not params.get('optional', False),
                     'requirement_scope': 'official_form', 'phase': 'both', 'source_id': source['id'],
                     'anchor': key, 'description': value.get('description', ''), 'extraction': 'openreview_json'})
    require(bool(rows), 'empty OpenReview form')
    return rows


def extract_form(bundle, source_id, start=None, end=None):
    source = next((s for s in bundle['sources'] if s['id'] == source_id), None)
    require(source is not None and source['status'] == 'ok', 'review form source is unavailable')
    return html_fields(source, start, end) if start else openreview_fields(source)


def evidence(record, sources, label):
    fields(record, ('source_id', 'quote'), label)
    source = sources.get(record['source_id'])
    require(source is not None and source['status'] == 'ok', label + ' cites an unavailable official source')
    require(normalize(record['quote']) in normalize(source['text']), label + ' quote is absent from official source')


def validate_rubric(rubric, target=None):
    obj(rubric, 'rubric')
    require(rubric.get('schema_version') == 2, 'unsupported rubric schema')
    conference = fields(rubric.get('conference'), ('name', 'track'), 'conference')
    require(type(conference.get('year')) is int, 'conference.year must be an integer')
    if target:
        require(conference == target, 'rubric conference/year/track does not match the project')
    text(rubric.get('version'), 'rubric.version')
    require(rubric.get('status') == 'verified', 'unverified rubric cannot launch formal review')
    require(rubric.get('form_basis') in ('openreview_form', 'official_form_instructions'), 'record the form reconstruction basis')
    sources = {row['id']: row for row in items(rubric.get('sources'), 'sources', 1)}
    require(len(sources) == len(rubric['sources']), 'duplicate official source IDs')
    domains = items(rubric.get('official_domains'), 'official_domains', 1)
    for row in sources.values():
        url(row.get('url'), 'source.url')
        require(urlparse(row['url']).hostname in domains, 'rubric source is not an approved official domain')
        text(row.get('retrieved_at'), 'source retrieval date')
        require(row.get('status') in ('ok', 'failed'), 'unknown source retrieval state')
        require(type(row.get('year')) is int, 'source year is required')
        require(row.get('track') == conference['track'], 'source track does not match rubric')
        if row['status'] == 'ok':
            require(row.get('sha256') == digest({'raw': row.get('raw')}), 'official source content hash mismatch')
            require(row['text'] == source_text(row['raw']), 'official source normalized text mismatch')
            require(row['year'] <= conference['year'], 'future-year sources cannot serve as historical fallback')
            require(str(row['year']) in row['text'], 'source does not identify its declared year')
        else:
            text(row.get('error'), 'retrieval failure')
    form = obj(rubric.get('form_extraction'), 'form_extraction')
    extracted = extract_form(rubric, form.get('source_id'), form.get('start'), form.get('end'))
    require(conference['name'].casefold() in sources[form['source_id']]['text'].casefold(), 'review form does not identify the declared conference')
    rows = items(rubric.get('fields'), 'review fields', 1)
    unique(rows, 'review fields')
    require(len(rows) == len(extracted), 'rubric omitted or added official review fields')
    for row, canonical in zip(rows, extracted):
        require(row == canonical, f'field/options differ from official source extraction: {canonical["id"]}')
    known = {f['id']: f for f in rows}
    for key in ('overall_field', 'confidence_field'):
        require(rubric.get(key) in known and known[rubric[key]]['kind'] == 'choice', f'{key} must reference an exact official choice field')
    years = {s['year'] for s in sources.values() if s['status'] == 'ok'}
    require(type(rubric.get('historical')) is bool, 'historical flag is required')
    require(rubric['historical'] == any(year != conference['year'] for year in years), 'historical fallback is mislabeled')
    if rubric['historical']:
        text(rubric.get('historical_reason'), 'historical_reason')
    items(rubric.get('uncertainties'), 'uncertainties')
    text(rubric.get('differences_previous_year'), 'differences_previous_year')
    contribution_types = items(rubric.get('contribution_types', []), 'contribution_types')
    unique(contribution_types, 'contribution_types')
    for category in contribution_types:
        fields(category, ('label', 'criteria'), 'contribution type')
        evidence(category, sources, 'contribution type')
        require(category['label'] in category['quote'], 'contribution label must appear in official source evidence')
    procedures = obj(rubric.get('procedures'), 'procedures')
    exchanges = items(procedures.get('exchanges'), 'procedural exchanges', 2)
    for row in exchanges:
        fields(row, ('role', 'label'), 'exchange')
        require(row['role'] in ('author', 'reviewers'), 'unsupported exchange role')
        if row.get('max_chars') is not None:
            require(type(row['max_chars']) is int and row['max_chars'] > 0, 'invalid response character limit')
        evidence(row, sources, 'exchange procedure')
        if row.get('max_chars'):
            require(str(row['max_chars']) in row['quote'], 'character limit is not supported by the procedure evidence')
    require(exchanges[0]['role'] == 'author' and exchanges[1]['role'] == 'reviewers', 'rebuttal then reviewer reassessment must be supported; extra stages must be labeled internal')
    for role in ('ac', 'sac'):
        row = fields(procedures.get(role), ('summary', 'scope'), role)
        require(row['scope'] in ('official_simulation', 'internal_simulation'), 'unknown chair simulation scope')
        if row['scope'] == 'official_simulation':
            evidence(row, sources, role + ' responsibility')
        options = items(row.get('decision_options'), role + ' decision_options')
        internal = items(row.get('internal_decision_options', []), role + ' internal_decision_options')
        if row['scope'] == 'internal_simulation':
            require(bool(internal), 'internal chair stages need explicitly internal decision options')
        require(set(items(row.get('acceptance_options'), role + ' acceptance_options')) <= set(options if row['scope'] == 'official_simulation' else internal), 'acceptance options must belong to the declared chair decision options')
        for option in options:
            text(option, role + ' option')
            evidence({'source_id': row.get('source_id'), 'quote': option}, sources, role + ' decision option')
    return rubric


def validate_answers(rubric, answers, phase):
    obj(answers, 'official review fields')
    known = {f['id']: f for f in rubric['fields']}
    require(set(answers) <= set(known), 'review invents an official scoring field')
    for field in rubric['fields']:
        active = field['phase'] in ('both', phase)
        if field['required'] and active:
            require(field['id'] in answers, 'missing required review field: ' + field['id'])
        if field['id'] not in answers:
            continue
        require(active, 'review field is not active in this phase: ' + field['id'])
        value = answers[field['id']]
        options = field.get('options', [])
        allowed = [x['value'] for x in options]
        # Python bool == 1; compare JSON types as well as values.
        def valid(v):
            return any(type(v) is type(a) and v == a for a in allowed)
        if field['kind'] == 'choice':
            require(valid(value), 'score/option is not in the official form: ' + field['id'])
        elif field['kind'] == 'multi_choice':
            require(isinstance(value, list) and all(valid(v) for v in value), 'invalid categorical choices: ' + field['id'])
        else:
            text(value, 'review.' + field['id'])
