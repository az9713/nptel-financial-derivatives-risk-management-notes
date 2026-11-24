"""Index public chapter provenance and package files without private sources."""
from hashlib import sha256
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8", newline="\n")


def main():
    manifest = json.loads((ROOT / "source-manifest.json").read_text(
        encoding="utf-8"))
    by_position = {x["position"]: x for x in manifest["recordings"]}
    chapters = []
    for path in sorted((ROOT / "chapters").glob("ch[0-9][0-9].json")):
        row = json.loads(path.read_text(encoding="utf-8"))
        manuscript = path.with_suffix(".md")
        if not manuscript.exists():
            continue
        source = manuscript.read_text(encoding="utf-8")
        sections = []
        for match in re.finditer(r"^## (.+)$", source, re.M):
            heading = match.group(1)
            links = re.findall(r"https://www\.youtube\.com/watch\?[^)\s]+",
                               heading)
            sections.append({"heading": heading,
                             "recording_locators": links,
                             "source_line": source.count("\n", 0,
                                                        match.start()) + 1})
        ledgers = [p.relative_to(ROOT).as_posix() for p in
                   sorted((ROOT / "validation").glob("source-read*.json"))
                   if path.stem in p.stem]
        chapters.append({
            "id": path.stem, "title": row["title"],
            "manuscript": manuscript.relative_to(ROOT).as_posix(),
            "manuscript_sha256": digest(manuscript),
            "laboratory": f"labs/{path.stem}.py",
            "recordings": [{"position": n,
                            "video_id": by_position[n]["video_id"]}
                           for n in row["lectures"]],
            "reading_ledgers": ledgers,
            "sections": sections,
            "external_reference_urls": sorted(set(re.findall(
                r"\]\((https://(?!www\.youtube\.com)[^)\s]+)\)",
                source))),
            "diagnostics": {"whitespace_words": len(source.split()),
                            "major_headings": len(sections),
                            "display_equation_blocks": (source.count("$$") // 2
                                                        + source.count(r"\["))},
        })
    write_json(ROOT / "analysis-ir.json", {
        "title": "Chapter provenance and section index",
        "kind": "section-index, not automatic claim attribution",
        "boundary": "Recording locators identify related discussion. They do not attribute every derivation, example, or research extension to the lecture. Reading and review ledgers state actual scope.",
        "chapters": chapters,
    })
    public = []
    roots = ["chapters", "labs", "assets", "tools", "figures", "research",
             "plan", "validation", "specs", ".github"]
    excluded = {"report-checks.json", "preview-1440.png", "preview-390.png"}
    for name in roots:
        folder = ROOT / name
        if not folder.exists():
            continue
        for path in folder.rglob("*"):
            if (path.is_file() and "__pycache__" not in path.parts
                    and path.name not in excluded):
                public.append(path)
    for pattern in ["*.html", "*.md", "BOOK-STATE.yaml", "requirements.txt", "book.json",
                    "source-manifest.json", "analysis-ir.json",
                    ".gitignore", ".gitattributes"]:
        public.extend(p for p in ROOT.glob(pattern)
                      if p.name != "HANDOFF.md")
    records = []
    for path in sorted(set(public)):
        relative = path.relative_to(ROOT).as_posix()
        if relative.startswith("validation/"):
            role = "scoped production, review, or validation evidence"
        elif relative.startswith("chapters/"):
            role = "authored chapter source or metadata"
        elif relative.startswith("labs/"):
            role = "executable educational computation"
        else:
            role = "public reader, supporting content, asset, or rebuild input"
        records.append({"path": relative, "bytes": path.stat().st_size,
                        "sha256": digest(path), "purpose": role})
    write_json(ROOT / "artifact-manifest.json", {
        "purpose": "Inventory public educational artifacts and their digests",
        "self_verification": "This manifest excludes itself. Later live-publication evidence is a separate record, not a self-signed hash.",
        "source_dependencies": [x["video_id"]
                                for x in manifest["recordings"]],
        "artifacts": records,
    })
    print(f"Indexed {len(chapters)} chapters and {len(records)} public files")


if __name__ == "__main__":
    main()
