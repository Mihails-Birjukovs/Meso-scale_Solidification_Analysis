"""Fail-closed public Markdown/CSS allowlist. Manual science/rights QA remains separate."""
from pathlib import Path
import json,re,sys,tomllib

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
    nav=[v for item in project["nav"] for v in item.values()]
    if len(nav)!=len(set(nav)) or set(nav)!={p for p in expected if p.endswith(".md")}:err.append("nav mismatch")
    if project["extra_css"]!=["stylesheets/inm-solidification-v1.css"]:err.append("unapproved CSS")
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
    print("ALLOWLIST_PASS: 9 curated public text/style sources; manual rights review still required")
