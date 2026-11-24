"""Check public source coverage, rendered links, timestamps and executable labs."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit
import argparse
import ast
import importlib.metadata
import json
import os
import re
import subprocess
import sys

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def specification():
    path = ROOT / 'plan' / 'book-spec.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}


def check(allow_partial=False):
    errors, chapters, labs, timestamps = [], [], [], 0
    pending_links = []
    manifest = json.loads((ROOT / 'source-manifest.json').read_text(encoding='utf-8'))
    records = manifest['recordings']
    if len(records) != manifest.get('expected_entries', len(records)):
        errors.append('Source manifest entry count differs from its declared inventory')
    by_id = {r['video_id']: r for r in records}
    positions = [r.get('position', r.get('playlist_position')) for r in records]
    if len(by_id) != len(records) or len(set(positions)) != len(records):
        errors.append('Duplicate source identity or playlist position')
    if sorted(positions) != list(range(1, len(records) + 1)):
        errors.append('Playlist positions are not complete')
    spec = specification()
    expected_positions = spec.get('expected_positions', [
        r.get('position', r.get('playlist_position')) for r in records
        if r.get('role') != 'introduction'])
    covered = []
    metadata = sorted((ROOT / 'chapters').glob('ch[0-9][0-9].json'))
    if not metadata:
        errors.append('No authored chapters are present')
    if not allow_partial and not (ROOT / 'plan' / 'book-spec.json').exists():
        errors.append('Final validation requires the public book specification')
    expected_chapters = spec.get('expected_chapters')
    if isinstance(expected_chapters, list):
        expected_chapters = len(expected_chapters)
    if expected_chapters is not None and not allow_partial and len(metadata) != expected_chapters:
        errors.append(f'Expected {expected_chapters} chapters, found {len(metadata)}')
    for path in metadata:
        row = json.loads(path.read_text(encoding='utf-8-sig'))
        source, page, lab = path.with_suffix('.md'), ROOT / f'{path.stem}.html', ROOT / 'labs' / f'{path.stem}.py'
        covered.extend(row['lectures'])
        if any(n not in positions for n in row['lectures']):
            errors.append(f'{path.name}: unknown source position')
        if not all(p.exists() for p in (source, page, lab)):
            errors.append(f'{path.stem}: missing manuscript, generated page or laboratory')
            continue
        text = source.read_text(encoding='utf-8')
        if re.search(rb'[\x00-\x08\x0b\x0c\x0e-\x1f]|\r(?!\n)',
                     source.read_bytes()):
            errors.append(f'{source.name}: embedded control character in manuscript')
        if re.search(r'\[(?:PROOF NEEDED|CITATION NEEDED|TODO|NUMBER NOT YET COMPUTED)', text):
            errors.append(f'{source.name}: unresolved manuscript placeholder')
        soup = BeautifulSoup(page.read_text(encoding='utf-8'), 'html.parser')
        if not soup.select_one('article details:not(.lab)'):
            errors.append(f'{source.name}: no worked-solution disclosure')
        for url in re.findall(r'https://(?:www\.)?youtube\.com/watch\?[^\s)"<>]+', text):
            query = parse_qs(urlsplit(url).query)
            record = by_id.get(query.get('v', [''])[0])
            if not record:
                errors.append(f'{source.name}: unknown recording URL {url}')
                continue
            if 't' in query:
                token = query['t'][0]
                match = re.fullmatch(r'(?:(\d+)h)?(?:(\d+)m)?(?:(\d+(?:\.\d+)?)s?)?', token)
                if not match or not any(match.groups()):
                    errors.append(f'{source.name}: unrecognized timestamp {token}')
                    continue
                seconds = float(match[1] or 0) * 3600 + float(match[2] or 0) * 60 + float(match[3] or 0)
                if seconds > record.get('duration', record.get('duration_seconds', 0)):
                    errors.append(f'{source.name}: timestamp beyond recording duration')
                timestamps += 1
        try:
            tree = ast.parse(lab.read_text(encoding='utf-8-sig'))
            if not any(isinstance(node, ast.Assert) for node in ast.walk(tree)):
                errors.append(f'{lab.name}: no assertion-based laboratory check')
        except SyntaxError as exc:
            errors.append(f'{lab.name}: syntax error {exc}')
        print(f'Running {lab.name}', flush=True)
        environment = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1',
                           MKL_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1')
        try:
            result = subprocess.run([sys.executable, str(lab)], cwd=ROOT,
                                    capture_output=True, text=True, encoding='utf-8',
                                    timeout=180, env=environment)
        except subprocess.TimeoutExpired:
            result = subprocess.CompletedProcess([str(lab)], 124, '', 'Laboratory exceeded 180 seconds')
        labs.append(dict(file=lab.relative_to(ROOT).as_posix(), sha256=digest(lab),
                         exit_code=result.returncode, stdout=result.stdout.strip(),
                         stderr=result.stderr.strip()))
        if result.returncode:
            errors.append(f'{lab.name}: runtime check failed')
        chapters.append(dict(id=path.stem, source_sha256=digest(source),
                             metadata_sha256=digest(path), html_sha256=digest(page),
                             source_words=len(re.findall(r'\b[\w-]+\b', text))))
    if not allow_partial and set(covered) != set(expected_positions):
        errors.append(f'Teaching recording coverage mismatch: missing={sorted(set(expected_positions)-set(covered))}; extra={sorted(set(covered)-set(expected_positions))}')
    if not spec.get('allow_shared_recordings', False) and any(count > 1 for count in Counter(covered).values()):
        errors.append('A teaching recording is assigned more than once')
    links, ids_by_path = 0, {}
    pages = sorted(ROOT.glob('*.html'))
    for page in pages:
        soup = BeautifulSoup(page.read_text(encoding='utf-8'), 'html.parser')
        ids = [x['id'] for x in soup.select('[id]')]
        ids_by_path[page] = (soup, set(ids))
        if len(ids) != len(set(ids)):
            errors.append(f'{page.name}: duplicate HTML IDs')
        if not soup.title or not soup.html or soup.html.get('lang') != 'en' or len(soup.select('h1')) != 1:
            errors.append(f'{page.name}: invalid title, language or H1 count')
    for page, (soup, ids) in ids_by_path.items():
        for node in soup.select('[href], [src]'):
            value = node.get('href', node.get('src', ''))
            parts = urlsplit(value)
            if parts.scheme or parts.netloc:
                if parts.scheme not in ('https', 'mailto', 'data'):
                    errors.append(f'{page.name}: unsafe or personal local URL {value}')
                if node.name in ('script', 'img', 'iframe', 'link') and parts.scheme in ('http', 'https'):
                    errors.append(f'{page.name}: remote rendering dependency {value}')
                continue
            target = (page.parent / unquote(parts.path)).resolve() if parts.path else page
            if not target.is_relative_to(ROOT):
                errors.append(f'{page.name}: link escapes public package')
            elif not target.exists():
                future = re.fullmatch(r'ch(\d\d)\.html', target.name)
                if (allow_partial and expected_chapters is not None and
                        target.parent == ROOT and future and
                        1 <= int(future[1]) <= expected_chapters):
                    pending_links.append(dict(page=page.name, target=value))
                else:
                    errors.append(f'{page.name}: missing local link {value}')
            elif parts.fragment and target.suffix == '.html':
                target_ids = ids_by_path.get(target)
                if target_ids is None:
                    destination = BeautifulSoup(target.read_text(encoding='utf-8'), 'html.parser')
                    valid = destination.find(id=unquote(parts.fragment)) is not None
                else:
                    valid = unquote(parts.fragment) in target_ids[1]
                if not valid:
                    errors.append(f'{page.name}: missing anchor {value}')
            links += 1
        text = page.read_text(encoding='utf-8')
        if re.search(r'(?:C:|/Users/|/home/)[\\/](?:Users[\\/])?[A-Za-z]', text):
            errors.append(f'{page.name}: possible personal machine path')
    report = dict(status='pass' if not errors else 'fail', chapter_count=len(chapters),
                  allow_partial=allow_partial, covered_positions=sorted(set(covered)),
                  chapters=chapters, labs=labs, timestamp_links_checked=timestamps,
                  local_links_checked=links, pending_planned_chapter_links=pending_links,
                  errors=errors,
                  versions={x: importlib.metadata.version(x) for x in
                            ['Markdown', 'beautifulsoup4', 'numpy', 'scipy']},
                  scope='Mechanical structure, source/timestamp bounds, local links and fresh lab execution; not a new scientific review.')
    report_dir = Path(os.environ.get('LECTURE_VALIDATION_DIR', ROOT / 'validation'))
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / 'package-checks.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(status=report['status'], chapters=len(chapters),
                          timestamp_links=timestamps, errors=errors), indent=2))
    return bool(errors)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--allow-partial', action='store_true')
    args = parser.parse_args()
    raise SystemExit(check(args.allow_partial))
