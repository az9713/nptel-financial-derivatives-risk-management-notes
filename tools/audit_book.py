"""Audit declared text-reading provenance and project exercise structure."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import os
import re

import pycodestyle

ROOT = Path(__file__).resolve().parents[1]


def main(allow_partial=False):
    manifest = json.loads((ROOT / "source-manifest.json").read_text(
        encoding="utf-8"))
    spec = json.loads((ROOT / "plan/book-spec.json").read_text(
        encoding="utf-8"))
    by_position = {r["position"]: r for r in manifest["recordings"]}
    read_positions, chapters, errors = set(), [], []
    for path in sorted((ROOT / "chapters").glob("ch[0-9][0-9].json")):
        meta = json.loads(path.read_text(encoding="utf-8"))
        source = path.with_suffix(".md")
        if not source.exists():
            errors.append(f"{path.stem}: manuscript absent")
            continue
        text = source.read_text(encoding="utf-8")
        exercise = re.search(r"^## Exercises\s*$([\s\S]*?)(?:<details|^## )",
                             text, re.M)
        if exercise:
            numbers = [int(x) for x in re.findall(r"^(\d+)\. ",
                                                 exercise.group(1), re.M)]
        else:
            numbers = []
        if numbers != [1, 2, 3, 4, 5, 6]:
            errors.append(f"{path.stem}: expected six numbered exercises")
        ledgers = [p for p in (ROOT / "validation").glob("source-read*.json")
                   if path.stem in p.stem]
        if not ledgers:
            errors.append(f"{path.stem}: no source-reading ledger")
        chapter_read = set()
        for ledger in ledgers:
            data = json.loads(ledger.read_text(encoding="utf-8"))
            for row in data.get("recordings", []):
                position = row.get("position")
                reference = by_position.get(position)
                if reference is None:
                    errors.append(f"{ledger.name}: unknown position {position}")
                    continue
                if row.get("video_id") != reference["video_id"]:
                    errors.append(f"{ledger.name}: video identity mismatch")
                if row.get("normalized_text_sha256") != reference.get(
                        "normalized_text_sha256"):
                    errors.append(f"{ledger.name}: text digest mismatch")
                if row.get("reading") != "full sequential text read":
                    errors.append(f"{ledger.name}: full reading not attested")
                chapter_read.add(position)
        required = set(meta["lectures"])
        if not required <= chapter_read:
            errors.append(f"{path.stem}: reading absent for "
                          f"{sorted(required - chapter_read)}")
        read_positions.update(chapter_read)
        sections = re.split(r"^## ", text, flags=re.M)[1:]
        chapters.append({"chapter": path.stem,
                         "manuscript_sha256": sha256(
                             source.read_bytes()).hexdigest(),
                         "exercises": len(numbers),
                         "whitespace_words": len(text.split()),
                         "section_words": [len(s.split()) for s in sections],
                         "source_reading_positions": sorted(chapter_read)})
    expected = set(spec["expected_positions"])
    if not allow_partial and not expected <= read_positions:
        errors.append("Full teaching-source reading coverage absent: "
                      + str(sorted(expected - read_positions)))
    if not allow_partial and len(chapters) != spec["expected_chapters"]:
        errors.append("Full chapter scope absent")
    style = pycodestyle.StyleGuide(
        quiet=True, max_line_length=79, ignore=["E226", "W503", "W504"])
    style_result = style.check_files(
        [str(p) for p in sorted((ROOT / "labs").glob("*.py"))])
    if style_result.total_errors:
        errors.append(f"Laboratory code style: {style_result.total_errors} "
                      "PEP8/79-column violations")
    report = {"status": "pass" if not errors else "fail",
              "allow_partial": allow_partial,
              "chapters": chapters,
              "covered_reading_positions": sorted(read_positions),
              "laboratory_style_errors": style_result.total_errors,
              "errors": errors,
              "scope": "Reading-attestation identity/digest consistency and project structure. This script cannot prove that a person or model read a source or that the prose teaches it correctly; independent scientific review is separate."}
    report_dir = Path(os.environ.get("LECTURE_VALIDATION_DIR",
                                     ROOT / "validation"))
    report_dir.mkdir(parents=True, exist_ok=True)
    destination = report_dir / "book-audit.json"
    destination.write_text(json.dumps(report, indent=2) + "\n",
                           encoding="utf-8", newline="\n")
    print(json.dumps({"status": report["status"], "chapters": len(chapters),
                      "read_positions": len(read_positions), "errors": errors}))
    return bool(errors)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()
    raise SystemExit(main(args.allow_partial))
