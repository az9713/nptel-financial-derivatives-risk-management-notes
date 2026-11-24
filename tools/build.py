"""Deterministically build the offline reader from public authored inputs."""
from hashlib import sha256
from pathlib import Path
import html
import json
import re

from bs4 import BeautifulSoup
import markdown

ROOT = Path(__file__).resolve().parents[1]
TITLE = "Financial Derivatives and Risk Management"
SUBTITLE = "Contracts, replication, and the limits of a hedge"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def render_markdown(source):
    """Protect TeX before Markdown handles escapes, HTML, and underscores."""
    source = re.sub(r'<details(?![^>]*\bmarkdown=)([^>]*)>',
                    r'<details markdown="1"\1>', source)
    saved = {}
    pieces = re.split(r'(```[^\n]*\n.*?```)', source, flags=re.S)
    pattern = re.compile(
        r'\\\[.*?\\\]|\\\(.*?\\\)|\$\$.*?\$\$|'
        r'(?<![\\$])\$(?!\$)(?:\\.|[^$\\\n])*?(?<!\\)\$(?!\$)',
        re.S)
    for index in range(0, len(pieces), 2):
        def save(match):
            token = f'MATHPLACEHOLDER{len(saved):06d}END'
            saved[token] = html.escape(match.group(0), quote=False)
            return token
        pieces[index] = pattern.sub(save, pieces[index])
    output = markdown.markdown(
        ''.join(pieces), extensions=['fenced_code', 'tables', 'toc',
                                    'sane_lists', 'md_in_html'])
    for token, expression in saved.items():
        output = output.replace(token, expression)
    soup = BeautifulSoup(output, 'html.parser')
    for table in soup.select('table'):
        table.wrap(soup.new_tag('div', attrs={
            'class': 'tablewrap', 'tabindex': '0',
            'aria-label': 'Scrollable table'}))
    for pre in soup.select('pre'):
        wrapper = soup.new_tag('div', attrs={'class': 'codewrap'})
        pre.wrap(wrapper)
        button = soup.new_tag('button', attrs={
            'class': 'copybtn', 'type': 'button', 'aria-label': 'Copy code'})
        button.string = 'Copy'
        wrapper.insert(0, button)
    for anchor in soup.select('a[href]'):
        href = anchor['href']
        if href.startswith('../'):
            href = href[3:]
        if re.match(r'^(?:chapters/)?ch\d\d\.md(?:#.*)?$', href):
            href = re.sub(r'^chapters/', '', href).replace('.md', '.html')
        anchor['href'] = href
    for image in soup.select('img[src]'):
        if image['src'].startswith('../'):
            image['src'] = image['src'][3:]
    if soup.h1:
        soup.h1.decompose()
    return str(soup)


def load_chapters():
    rows = []
    for path in sorted((ROOT / 'chapters').glob('ch[0-9][0-9].json')):
        row = json.loads(path.read_text(encoding='utf-8-sig'))
        source = path.with_suffix('.md')
        if not source.exists():
            continue
        row.update(id=path.stem, number=int(path.stem[2:]),
                   source_sha256=digest(source),
                   metadata_sha256=digest(path),
                   source_words=len(re.findall(r'\b[\w-]+\b',
                                               source.read_text(encoding='utf-8'))))
        rows.append(row)
    return rows


def shell(title, content, chapters, current='', script=''):
    nav = ''.join(
        f'<a href="{c["id"]}.html"'
        f'{" aria-current=page" if c["id"] == current else ""}>'
        f'{c["number"]:02d}. {html.escape(c["title"])}</a>' for c in chapters)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark light">
<meta name="description" content="Independent study edition of NPTEL Financial Derivatives and Risk Management, IIT Roorkee: mathematical reasoning, original examples, solved exercises, and executable laboratories.">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'none'">
<title>{html.escape(title)} · Financial Derivatives</title>
<link rel="stylesheet" href="assets/reader.css">
<script src="assets/math-config.js" defer></script>
<script src="assets/mathjax-tex-svg.js" defer></script>
<script src="assets/reader.js" defer></script>{script}</head><body>
<a class="skip" href="#main">Skip to main content</a><div class="shell">
<aside><a class="brand" href="index.html">Financial Derivatives</a>
<p>Contracts, replication, and risk<br>Independent NPTEL study edition</p>
<button id="menu" type="button" aria-expanded="false" aria-controls="navigation">Contents</button>
<nav id="navigation" aria-label="Book"><a href="index.html">Overview and chapter finder</a>
<a href="source-map.html">Recordings and source map</a>
<a href="study-guide.html">Study guide and dependency map</a>
<a href="numerical-lab.html">Interactive numerical laboratory</a>
<a href="references.html">References and evidence limits</a>{nav}</nav></aside>
<main id="main"><div class="eyebrow">NPTEL · IIT Roorkee · J. P. Singh</div>
{content}
<p class="publication-note">Independent educational notes. Not an official NPTEL or IIT Roorkee publication, affiliation, or endorsement. Educational models are presented under stated assumptions.</p>
</main></div></body></html>
'''


def write_page(name, title, content, chapters, current='', script=''):
    (ROOT / name).write_text(shell(title, content, chapters, current, script),
                             encoding='utf-8', newline='\n')


def build():
    chapters = load_chapters()
    manifest = json.loads((ROOT / 'source-manifest.json').read_text(encoding='utf-8'))
    records = manifest['recordings']
    by_position = {r.get('position', r.get('playlist_position')): r for r in records}
    for index, row in enumerate(chapters):
        body = render_markdown((ROOT / 'chapters' / f'{row["id"]}.md').read_text(encoding='utf-8'))
        soup = BeautifulSoup(body, 'html.parser')
        toc = '<div class="toc"><strong>In this chapter</strong><ul>' + ''.join(
            f'<li><a href="#{h["id"]}">{html.escape(h.get_text(" ", strip=True))}</a></li>'
            for h in soup.select('h2[id]')) + '</ul></div>'
        sources = ', '.join(
            f'<a href="{html.escape(by_position[n]["url"], quote=True)}">Recording {n}</a>'
            for n in row['lectures'])
        objectives = ''.join(f'<li>{html.escape(x)}</li>'
                             for x in row.get('objectives', []))
        lab_path = ROOT / 'labs' / f'{row["id"]}.py'
        lab = ''
        if lab_path.exists():
            code = html.escape(lab_path.read_text(encoding='utf-8'))
            lab = f'''<details class="lab"><summary>Executable chapter laboratory</summary>
<p><a href="labs/{row["id"]}.py">Download the Python source</a>. Run in a fresh interpreter; see requirements.txt for dependencies.</p>
<div class="codewrap"><button class="copybtn" type="button" aria-label="Copy laboratory source">Copy</button><pre><code class="language-python">{code}</code></pre></div></details>'''
        previous = (f'<a rel="prev" href="{chapters[index-1]["id"]}.html">Previous: '
                    f'{html.escape(chapters[index-1]["title"])}</a>') if index else '<a href="index.html">Overview</a>'
        following = (f'<a rel="next" href="{chapters[index+1]["id"]}.html">Next: '
                     f'{html.escape(chapters[index+1]["title"])}</a>') if index + 1 < len(chapters) else '<a href="study-guide.html">Study guide</a>'
        content = f'''<h1>{row["number"]:02d}. {html.escape(row["title"])}</h1>
<p class="meta">{sources} · Expanded, independently developed exposition</p>
<div class="objectives"><strong>What you will learn</strong><ul>{objectives}</ul>
<p><strong>Prerequisites:</strong> {html.escape(row.get('prerequisites', ''))}</p></div>
<div class="toolbar"><button id="solutions" type="button">Open solutions and code</button>
<button id="print" type="button">Print / save PDF</button><button id="theme" type="button" aria-pressed="false">Use light theme</button>
<a href="chapters/{row["id"]}.md">Editable chapter source</a></div>{toc}
<article>{body}{lab}</article><div class="footer">{previous}{following}</div>'''
        write_page(f'{row["id"]}.html', row['title'], content, chapters, row['id'])
    cards = ''.join(
        f'<div class="chapter-card"><small>Chapter {r["number"]:02d} · Recordings '
        f'{", ".join(map(str, r["lectures"]))}</small><a href="{r["id"]}.html">'
        f'{html.escape(r["title"])}</a><p>{html.escape("; ".join(r.get("objectives", [])))}</p></div>'
        for r in chapters)
    overview = render_markdown((ROOT / 'overview.md').read_text(encoding='utf-8'))
    write_page('index.html', TITLE,
               f'<h1>{TITLE}</h1><p class="subtitle">{SUBTITLE}</p>{overview}'
               '<label for="search">Find a chapter by contract, model, or method</label>'
               '<input id="search" type="search" placeholder="Try futures, replication, duration…">'
               f'<p class="status" id="search-status" aria-live="polite">{len(chapters)} chapters shown</p>'
               f'<div class="chapter-list">{cards}</div>', chapters)
    rows = []
    for position, record in sorted(by_position.items()):
        linked = [c for c in chapters if position in c['lectures']]
        chapter_links = ', '.join(f'<a href="{c["id"]}.html">{c["number"]:02d}</a>' for c in linked)
        duration = record.get('duration', record.get('duration_seconds', 0)) or 0
        label = record.get('lecture_number', record.get('lecture', ''))
        if record.get('role') == 'introduction':
            label = 'Introduction'
        rows.append(f'<tr><td>{position}</td><td>{html.escape(str(label))}</td>'
                    f'<td><a href="{html.escape(record["url"], quote=True)}">{html.escape(record["title"])}</a></td>'
                    f'<td>{int(duration)//60}:{int(duration)%60:02d}</td>'
                    f'<td>{chapter_links or "Introductory source / see overview"}</td></tr>')
    source_note = manifest.get('coverage_note',
        'Source identities and caption provenance are recorded in the manifest. '
        'Timestamp links locate related discussions; they do not attribute every added derivation or example to the source lecturer.')
    intro = ('<h1>Recording and source map</h1>'
             f'<p>{html.escape(source_note)}</p>'
             '<p>Playlist positions, original upload titles, and any verified lecture numbering remain distinct. '
             '<a href="source-manifest.json">Machine-readable source manifest</a>.</p>')
    write_page('source-map.html', 'Recording and source map', intro +
               '<div class="tablewrap" tabindex="0" aria-label="Scrollable source table"><table><thead><tr>'
               '<th>Playlist position</th><th>Lecture label</th><th>Original upload title</th><th>Duration</th><th>Chapters</th>'
               '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>', chapters)
    for stem, title in [('study-guide', 'Study guide and dependency map'),
                        ('references', 'References and evidence limits'),
                        ('numerical-lab', 'Interactive numerical laboratory')]:
        path = ROOT / f'{stem}.md'
        if path.exists():
            script = '<script src="assets/lab.js" defer></script>' if stem == 'numerical-lab' and (ROOT / 'assets/lab.js').exists() else ''
            write_page(f'{stem}.html', title, '<h1>' + title + '</h1>' +
                       render_markdown(path.read_text(encoding='utf-8')), chapters, script=script)
    (ROOT / 'book.json').write_text(json.dumps(
        dict(title=TITLE, subtitle=SUBTITLE, chapters=chapters),
        indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    print(f'Built {len(chapters)} chapters from public authoring inputs.')


if __name__ == '__main__':
    build()
