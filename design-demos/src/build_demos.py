"""Embed the shared immutable dataset, controls, and fonts into offline review prototypes."""
import base64
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
src = root/'src'
data = json.loads((src/'review-data.json').read_text())
for source in data['sources'].values():
 assert hashlib.sha256(source['text'].encode()).hexdigest() == source['sha256'], source['path']
font_css = []
for font in json.loads((root/'assets/fonts/manifest.json').read_text()):
 raw = (root/'assets/fonts'/font['file']).read_bytes()
 font_css.append("@font-face{font-family:'%s';font-style:normal;font-weight:%s;font-display:swap;src:url(data:font/woff2;base64,%s) format('woff2')}" % (font['family'],font['weight'],base64.b64encode(raw).decode()))
licenses = '\n'.join(path.read_text() for path in sorted((root/'assets/fonts').glob('*-OFL.txt')))
fonts = '\n'.join(font_css)+'\n/* Font license notices:\n'+licenses.replace('*/','* /')+'\n*/'
common = (src/'common.css').read_text()
runtime = (src/'runtime.js').read_text()
payload = json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
embedded = '<script id="review-data" type="application/json">'+payload+'</script>\n<script>'+runtime+'</script>'
for name in ('signal-desk','editorial-dossier','evidence-table','github-review'):
 template = src/(name+'.template.html')
 if not template.exists():
  print('Pending:',template.name)
  continue
 html = template.read_text()
 for marker,replacement in [('/* EMBED_FONTS */',fonts if name!='github-review' else '/* Native system fonts; no external font dependencies. */'),('<!-- EMBED_COMMON_CSS -->',common),('<!-- EMBED_RUNTIME -->',embedded)]:
  assert html.count(marker)==1, (name,marker)
  html = html.replace(marker,replacement)
 output = root/(name+'.html')
 output.write_text(html)
 print(output.name,len(html.encode()),'bytes')
