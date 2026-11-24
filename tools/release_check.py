"""Verify current independent receipts and reproducibility without raw sources."""
from hashlib import sha256
from pathlib import Path
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main(allow_partial=False):
    errors, receipts, accepted = [], [], {}
    spec_path = ROOT / 'plan' / 'book-spec.json'
    spec = json.loads(spec_path.read_text(encoding='utf-8')) if spec_path.exists() else {}
    if not spec_path.exists():
        errors.append('Release requires the public book specification')
    minimum = int(spec.get('minimum_reviewers', 1))
    authors = spec.get('chapter_authors', {})
    canonical_ids = spec.get('reviewer_canonical_id', {})
    for receipt in sorted((ROOT / 'validation').glob('review-*.json')):
        row = json.loads(receipt.read_text(encoding='utf-8-sig'))
        if row.get('superseded', False):
            continue
        mapping = row.get('accepted_files', {})
        reviewer = row.get('reviewer')
        canonical = canonical_ids.get(reviewer, reviewer)
        if row.get('disposition') != 'accepted' or row.get('remaining_findings'):
            errors.append(f'{receipt.name}: review not accepted or findings remain')
            continue
        if not mapping or not reviewer:
            errors.append(f'{receipt.name}: missing reviewer identity or accepted file bindings')
            continue
        for relative, value in mapping.items():
            path = (ROOT / relative).resolve()
            if not path.is_relative_to(ROOT):
                errors.append(f'{receipt.name}: binding leaves package')
                continue
            if not path.is_file() or digest(path) != value:
                errors.append(f'{receipt.name}: stale binding for {relative}')
            else:
                chapter = re.fullmatch(r'(?:chapters|labs)/(ch\d\d)\.(?:md|json|py)',
                                       relative.replace('\\', '/'))
                if chapter and authors.get(chapter[1]) == canonical:
                    errors.append(f'{receipt.name}: author self-review for {relative}')
                    continue
                accepted.setdefault(relative, set()).add(canonical)
        receipts.append(receipt.name)
    metadata = sorted((ROOT / 'chapters').glob('ch[0-9][0-9].json'))
    if not metadata:
        errors.append('No authored chapters are present')
    expected = spec.get('expected_chapters')
    if isinstance(expected, list):
        expected = len(expected)
    if not allow_partial and expected is not None and len(metadata) != expected:
        errors.append(f'Incomplete edition: expected {expected} chapters, found {len(metadata)}')
    for meta in metadata:
        if not authors.get(meta.stem):
            errors.append(f'{meta.stem}: missing canonical chapter author identity')
        for relative in [f'chapters/{meta.stem}.md', f'chapters/{meta.stem}.json', f'labs/{meta.stem}.py']:
            if len(accepted.get(relative, set())) < minimum:
                errors.append(f'{relative}: fewer than {minimum} current independent acceptances')
    baseline = {p.name: digest(p) for p in ROOT.glob('*.html')}
    if (ROOT / 'book.json').exists():
        baseline['book.json'] = digest(ROOT / 'book.json')
    rebuilt = {}
    (ROOT / 'work').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='derivatives-public-export-', dir=ROOT / 'work') as temp:
        target = Path(temp)
        for name in ['chapters', 'labs', 'assets', 'tools', 'figures']:
            shutil.copytree(ROOT / name, target / name,
                            ignore=shutil.ignore_patterns('__pycache__'))
        for name in ['source-manifest.json', 'overview.md', 'study-guide.md',
                     'references.md', 'numerical-lab.md']:
            path = ROOT / name
            if path.exists():
                shutil.copyfile(path, target / name)
        environment = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
        result = subprocess.run([sys.executable, str(target / 'tools' / 'build.py')],
                                cwd=target, capture_output=True, text=True,
                                encoding='utf-8', timeout=180, env=environment)
        if result.returncode:
            errors.append('Public-input rebuild failed: ' + result.stderr[-1500:])
        for name, expected_hash in baseline.items():
            path = target / name
            rebuilt[name] = path.is_file() and digest(path) == expected_hash
            if not rebuilt[name]:
                errors.append(f'{name}: public-input rebuild differs')
    report = dict(status='pass' if not errors else 'fail', allow_partial=allow_partial,
                  independent_review_receipts=receipts, minimum_reviewers=minimum,
                  accepted_file_count=len(accepted),
                  source_free_byte_identical=rebuilt, errors=errors,
                  scope='Exact-content receipt freshness and public-input reproducibility; not a new scientific review.')
    report_dir = Path(os.environ.get('LECTURE_VALIDATION_DIR', ROOT / 'validation'))
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / 'release-checks.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(report, indent=2))
    return bool(errors)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--allow-partial', action='store_true')
    args = parser.parse_args()
    raise SystemExit(main(args.allow_partial))
