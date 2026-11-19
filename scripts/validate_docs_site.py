"""Fail-closed public Markdown/CSS allowlist. Manual science/rights QA remains separate."""
from pathlib import Path
import json,re,sys,tomllib,hashlib

ROOT=Path(__file__).resolve().parents[1]
def validate(root=ROOT):
    manifest=json.loads((root/"site_publication_manifest.json").read_text("utf-8"))
    project=tomllib.loads((root/"zensical.toml").read_text("utf-8"))["project"]
    d=root/manifest["site_root"]
    allowed=manifest["allowed_relative_files"]
    expected=set(allowed)
    actual={p.relative_to(d).as_posix() for p in d.rglob("*") if p.is_file()}
    err=[]
    if len(expected)!=len(allowed):err.append("duplicated allowlist entries")
    if actual!=expected:err.append("unexpected="+str(sorted(actual-expected))+" missing="+str(sorted(expected-actual)))
    if project["site_url"]!="https://mihails-birjukovs.github.io/Meso-scale_Solidification_Analysis/":err.append("bad site_url")
    if project["docs_dir"]!="site_docs" or project["site_dir"]!="site":err.append("bad source/build root")
    expected_repo="https://github.com/Mihails-Birjukovs/Meso-scale_Solidification_Analysis"
    if project.get("repo_url")!=expected_repo:err.append("header GitHub URL is not public project repository")
    theme=project.get("theme",{})
    if theme.get("logo")!="assets/inm-horizontal.svg" or theme.get("favicon")!="assets/inm-mark.svg":
        err.append("approved INM header logo/mark not configured")
    approved_logos={"assets/inm-horizontal.svg":"33938b2a9a6ae442b3ede153fb79187a31040a68",
                    "assets/inm-mark.svg":"b3a5154d96b0daf24cd44711fa13980689119287",
                    "assets/inm-square-footer.svg":"327ffd7d447e8475e4c8f0e0d0fa68f465be841b"}
    for rel,blob in approved_logos.items():
        p=d/rel
        if not p.is_file():err.append("missing approved INM logo "+rel);continue
        data=p.read_bytes()
        actual_blob=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\\0"+data).hexdigest()
        if actual_blob!=blob:err.append("INM logo source drift "+rel)
        if re.search(rb"<script|<foreignObject|onload=|javascript:|<image\\b",data,re.I):
            err.append("Unexpected active SVG content "+rel)
    nav=[v for item in project["nav"] for v in item.values()]
    if len(nav)!=len(set(nav)) or set(nav)!={p for p in expected if p.endswith(".md")}:err.append("nav mismatch")
    if project["extra_css"]!=["stylesheets/inm-solidification-v1.css"]:err.append("unapproved CSS")
    allowed_js=["javascripts/mathjax.js","https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js"]
    if project.get("extra_javascript")!=allowed_js:err.append("unapproved or unpinned mathematical JS")
    math_config=project.get("markdown_extensions",{}).get("pymdownx",{}).get("arithmatex",{})
    if math_config.get("generic") is not True:err.append("missing generic Arithmatex math rendering")
    canonical_mirrors=manifest.get("public_source_mirrors",[])
    if {item["site"] for item in canonical_mirrors}!={"site_docs/current-code.md","site_docs/scientific-methods.md"}:
        err.append("missing canonical technical source mirror provenance")
    expected_math_counts={"current-code.md":5,"scientific-methods.md":46,
                          "methods.md":4,"temporal-model.md":3}
    for name,n in expected_math_counts.items():
        page=(d/name).read_text("utf-8")
        import re as _re
        blocks=_re.findall(r"^\$\$\s*\n([\s\S]*?)\n\$\$",page,_re.M)
        if len(blocks)!=n or any(len(_re.findall(r"\\label\{eq:[^}]+\}",block))!=1 for block in blocks):
            err.append("missing/unnumbered scientific equation blocks in "+name)
        labels=_re.findall(r"\\label\{(eq:[^}]+)\}",page)
        if len(labels)!=len(set(labels)):err.append("duplicate equation label in "+name)
    jsfile=(d/"javascripts"/"mathjax.js").read_text("utf-8")
    if 'tags: "all"' not in jsfile or 'document$.subscribe' not in jsfile:
        err.append("MathJax numbering/navigation hook missing")
    forbidden=[(r"(?i)[xg]:\\","private machine path"),(r"(?i)BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY","private key"),
        (r"(?i)(?:ghp_|github_pat_)[A-Za-z0-9_]{10,}","GitHub token"),
        (r"(?i)AIza[0-9A-Za-z_-]{20,}","API key"),
        (r"(?i)password\s*[:=]\s*\S+","credential marker"),
        (r"(?i)<script\b|data:image/|base64,","unapproved script/embedded binary")]
    for rel in expected|actual:
        p=d/rel
        if rel.startswith("/") or ".." in Path(rel).parts or "\\" in rel:err.append("path escape "+rel);continue
        if not p.exists():continue
        if p.is_symlink():err.append("symlink "+rel);continue
        if p.suffix.lower() in (".tif",".tiff",".pkl",".7z",".nb",".zip",".pdf",".exe",".py",".woff",".woff2"):err.append("binary "+rel)
        if p.stat().st_size>400000:err.append("oversized "+rel)
        try:s=p.read_text("utf-8")
        except UnicodeDecodeError:err.append("non-UTF8 "+rel);continue
        for patt,label in forbidden:
            if re.search(patt,s):err.append(label+" "+rel)
    return err
if __name__=="__main__":
    errors=validate()
    if errors:
        print("\n".join("BLOCKED: "+e for e in errors));sys.exit(1)
    print("ALLOWLIST_PASS: curated public technical pages, mathematical assets, and source-mirror provenance verified; manual rights and live-browser math QA still required")
