"""Check static Zensical generated output; does not constitute live browser QA."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"site"
NAMES=("index","start","architecture","current-code","scientific-methods","methods","temporal-model","validation","research","status")
errors=[]
for name in NAMES:
    p=OUT/"index.html" if name=="index" else OUT/name/"index.html"
    if not p.is_file():errors.append("missing HTML "+str(p));continue
    s=p.read_text("utf-8")
    if "inm-solidification-v1.css" not in s:errors.append("no stylesheet link "+name)
    if "Meso-scale Solidification Analysis" not in s:errors.append("no site title "+name)
    if 'href="https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis"' not in s or "md-source" not in s:
        errors.append("no upper-right public GitHub link "+name)
    if "javascripts/mathjax.js" not in s or "mathjax@3.2.2" not in s:
        errors.append("missing pinned MathJax runtime/config on "+name)
    if name in ("current-code","scientific-methods","methods","temporal-model") and "arithmatex" not in s:
        errors.append("typeset math source missing in "+name)
css=OUT/"stylesheets"/"inm-solidification-v1.css"
if not css.is_file():errors.append("no built CSS")
else:
    t=css.read_text("utf-8")
    for name in ("#004b8e","#1c3854","#f47b20",".inm-hero",".md-copyright"):
        if name not in t:errors.append("no style token "+name)
home=(OUT/"index.html").read_text("utf-8")
if "assets/inm-horizontal.svg" not in home or "assets/inm-mark.svg" not in home:
    errors.append("INM header/favicons absent in output")
for logo in ("inm-horizontal.svg","inm-mark.svg","inm-square-footer.svg"):
    if not (OUT/"assets"/logo).is_file():errors.append("missing built INM artwork "+logo)
if css.is_file() and "inm-square-footer.svg" not in css.read_text("utf-8"):
    errors.append("No approved INM footer artwork CSS")
if errors:
    print("\n".join(errors));sys.exit(1)
print("STATIC_SITE_PASS: 10 content pages, CSS, MathJax links and Arithmatex HTML detected; live JS rendering and equation numbering require browser QA")
