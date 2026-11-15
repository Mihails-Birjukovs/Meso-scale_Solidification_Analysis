"""Check static Zensical generated output; does not constitute live browser QA."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"site"
NAMES=("index","start","architecture","methods","temporal-model","validation","research","status")
errors=[]
for name in NAMES:
    p=OUT/"index.html" if name=="index" else OUT/name/"index.html"
    if not p.is_file():errors.append("missing HTML "+str(p));continue
    s=p.read_text("utf-8")
    if "inm-solidification-v1.css" not in s:errors.append("no stylesheet link "+name)
    if "Meso-scale Solidification Analysis" not in s:errors.append("no site title "+name)
css=OUT/"stylesheets"/"inm-solidification-v1.css"
if not css.is_file():errors.append("no built CSS")
else:
    t=css.read_text("utf-8")
    for name in ("#004b8e","#1c3854","#f47b20",".inm-hero",".md-copyright"):
        if name not in t:errors.append("no style token "+name)
if errors:
    print("\n".join(errors));sys.exit(1)
print("STATIC_SITE_PASS 8 pages, CSS and links detected; live Pages/browser still unverified")
