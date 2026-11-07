"""Build the current UI example with explicitly synthetic, sourced test artifacts."""
import json
from pathlib import Path
import sys
import tempfile
import uuid

REPO = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(REPO / 'tests'), str(REPO / 'scripts')]
from review_fixture import make_workspace, add_research_design
from render_review import render

with tempfile.TemporaryDirectory(prefix='idea-shaokao-design-') as directory:
    workspace = Path(directory) / 'adaptive-cache'
    _, index = make_workspace(workspace)
    add_research_design(workspace, index)
    manifest = {'schema_version': 1, 'slug': 'adaptive-cache',
                'workspace_id': str(uuid.uuid5(uuid.NAMESPACE_URL, 'idea-shaokao:synthetic-workspace-demo'))}
    (workspace / 'final/review-manifest.json').write_text(json.dumps(manifest))
    render(workspace)
    target = REPO / 'design-demos/research-workspace.html'
    target.write_bytes((workspace / 'final/review.html').read_bytes())
    print(target)
