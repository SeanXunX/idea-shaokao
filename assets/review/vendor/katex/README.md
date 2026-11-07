# Bundled math renderer

KaTeX 0.19.1, MIT licensed. Source distribution:
https://registry.npmjs.org/katex/-/katex-0.19.1.tgz

Only the minified browser runtime, stylesheet, WOFF2 fonts and upstream license
are included. `render_review.py` embeds the runtime/CSS/fonts into schema-2 HTML;
legacy reports do not load it. Input uses `trust: false`, bounded size/expansion,
no shared macro state, accessible MathML plus HTML, and escaped error fallback.
There is no runtime CDN/network requirement. See the included LICENSE.
