"""Generate a schema-2 example from explicitly synthetic software-test agents."""
from pathlib import Path
import sys
import tempfile

REPO = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(REPO / 'tests'), str(REPO / 'scripts')]
from engine_fixture import create, drive
from shaokao.report import render

with tempfile.TemporaryDirectory(prefix='shaokao-interface-example-') as directory:
    store = create(Path(directory) / 'synthetic-research-example')
    drive(store)
    render(store)
    target = REPO / 'design-demos/research-workspace.html'
    target.write_bytes((store.root / 'final/review.html').read_bytes())
    print(target)
