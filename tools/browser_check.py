"""Exercise offline/static reader and math at desktop and phone widths."""
from pathlib import Path
import argparse
import json
import os

from playwright.sync_api import sync_playwright
from check_math_layout import MEASURE_LAYOUT

ROOT = Path(__file__).resolve().parents[1]


def run(browser_path=None, base_url=None, screenshots=False):
    results, errors = [], []
    files = sorted(ROOT.glob('ch[0-9][0-9].html'))
    support = [ROOT / name for name in ['index.html', 'source-map.html',
               'study-guide.html', 'numerical-lab.html', 'references.html',
               'mathematical-repairs.html']
               if (ROOT / name).exists()]
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=browser_path,
                                     ignore_default_args=['--hide-scrollbars'])
        for width, height in [(1440, 1000), (390, 844)]:
            context = browser.new_context(viewport=dict(width=width, height=height))
            requests = []
            if not base_url:
                def reject(route):
                    requests.append(route.request.url)
                    route.abort()
                context.route('https://**/*', reject)
                context.route('http://**/*', reject)
            page = context.new_page()
            page_errors = []
            page.on('pageerror', lambda exc: page_errors.append(str(exc)))
            for file in support + files:
                target = f'{base_url.rstrip("/")}/{file.name}' if base_url else file.as_uri()
                before = len(page_errors)
                model_checks = {}
                try:
                    response = page.goto(target, wait_until='load')
                    if response and not response.ok:
                        raise RuntimeError(f'HTTP {response.status}')
                    page.wait_for_function('window.MathJax && MathJax.startup && MathJax.startup.promise')
                    page.evaluate('() => MathJax.startup.promise.then(() => undefined)')
                    layout = page.evaluate(MEASURE_LAYOUT)
                    if width < 721:
                        page.locator('#menu').click()
                        if page.locator('#menu').get_attribute('aria-expanded') != 'true':
                            errors.append(f'{file.name}/{width}: mobile contents failed')
                        page.locator('#menu').click()
                    if file in files or file.name == 'mathematical-repairs.html':
                        page.locator('#solutions').click()
                        if not page.locator('article details').evaluate_all('(nodes) => nodes.every(n => n.open)'):
                            errors.append(f'{file.name}/{width}: solution disclosure failed')
                        layout = page.evaluate(MEASURE_LAYOUT)
                        if not layout['rendered']:
                            errors.append(f'{file.name}/{width}: no rendered math')
                        page.locator('#solutions').click()
                        page.locator('#theme').click()
                        if not page.locator('body').evaluate("e=>e.classList.contains('light')"):
                            errors.append(f'{file.name}/{width}: light theme failed')
                        page.locator('#theme').click()
                        page.evaluate("dispatchEvent(new Event('beforeprint'))")
                        if not page.locator('article details').evaluate_all('(nodes)=>nodes.every(n=>n.open)'):
                            errors.append(f'{file.name}/{width}: print expansion failed')
                        page.evaluate("dispatchEvent(new Event('afterprint'))")
                        if page.locator('.copybtn').count():
                            button = page.locator('.copybtn').first
                            parent = button.locator('..')
                            parent.evaluate("e=>{const d=e.closest('details');if(d)d.open=true;}")
                            button.click()
                            page.wait_for_timeout(100)
                            if button.inner_text() != 'Copied':
                                errors.append(f'{file.name}/{width}: code copy failed')
                        raw = page.locator('article').evaluate('''e=>{
                            const copy=e.cloneNode(true);
                            copy.querySelectorAll('pre,code,mjx-container,script').forEach(n=>n.remove());
                            return /\\\\(?:frac|begin|mathbb|sqrt)\\b|\\$\\$/.test(copy.textContent);
                        }''')
                        if raw:
                            errors.append(f'{file.name}/{width}: unrendered TeX')
                    if file.name == 'index.html':
                        count = page.locator('.chapter-card').count()
                        page.locator('#search').fill('nonexistentsearchtoken')
                        if page.locator('.chapter-card:visible').count():
                            errors.append(f'index/{width}: empty filter failed')
                        page.locator('#search').fill('')
                        if page.locator('.chapter-card:visible').count() != count:
                            errors.append(f'index/{width}: filter restoration failed')
                    if file.name == 'numerical-lab.html' and page.locator('#tree-spot').count():
                        defaults = {'tree-spot':'100','tree-up':'1.2','tree-down':'0.8',
                                    'tree-strike':'100','tree-growth':'1.05'}
                        for key, val in defaults.items():
                            page.locator('#'+key).fill(val)
                            page.locator('#'+key).dispatch_event('input')
                        if abs(float(page.locator('#tree-price').inner_text())-11.9047619)>1e-5:
                            errors.append(f'lab/{width}: binomial replication price failed')
                        model_checks['pricing_probability_wording'] = 'The weight is a pricing probability; holdings replicate both states.' in page.locator('#tree-error').inner_text()
                        if not model_checks['pricing_probability_wording']:
                            errors.append(f'lab/{width}: pricing probability wording failed')
                        page.locator('#tree-growth').fill('1.3')
                        page.locator('#tree-growth').dispatch_event('input')
                        if page.locator('#tree-price').inner_text() != '—':
                            errors.append(f'lab/{width}: no-arbitrage-domain guard failed')
                        page.locator('#tree-growth').fill('1.05')
                        page.locator('#tree-spot').fill('1e308')
                        page.locator('#tree-up').fill('2')
                        page.locator('#tree-up').dispatch_event('input')
                        model_checks['finite_tree_overflow_rejected'] = (
                            'numerical range' in page.locator('#tree-error').inner_text()
                            and all(page.locator('#'+key).inner_text() == '—'
                                    for key in ['tree-price', 'tree-delta', 'tree-probability']))
                        if not model_checks['finite_tree_overflow_rejected']:
                            errors.append(f'lab/{width}: finite-input tree overflow guard failed')
                        for key, val in defaults.items():
                            page.locator('#'+key).fill(val)
                        page.locator('#tree-spot').dispatch_event('input')
                        for key, val in {'carry-spot':'100', 'carry-rate':'100000', 'carry-time':'100'}.items():
                            page.locator('#'+key).fill(val)
                        page.locator('#carry-time').dispatch_event('input')
                        model_checks['finite_carry_overflow_rejected'] = 'numerical range' in page.locator('#carry-forward').inner_text()
                        if not model_checks['finite_carry_overflow_rejected']:
                            errors.append(f'lab/{width}: finite-input carry overflow guard failed')
                        page.locator('#carry-rate').fill('4')
                        page.locator('#carry-time').fill('1')
                        page.locator('#carry-time').dispatch_event('input')
                        model_checks['carry_recovers_after_overflow'] = abs(float(page.locator('#carry-forward').inner_text())-104.0810774)<1e-5
                        if not model_checks['carry_recovers_after_overflow']:
                            errors.append(f'lab/{width}: carry recovery failed')
                    for key in ['mathErrors', 'unhiddenInlineScrollers', 'blockedOverflow', 'pageOverflow']:
                        if layout[key]:
                            errors.append(f'{file.name}/{width}: {key}={layout[key]}')
                    if page_errors[before:]:
                        errors.extend(f'{file.name}/{width}: {e}' for e in page_errors[before:])
                    results.append(dict(file=file.name, width=width, model_checks=model_checks, **layout))
                    print(f'{file.name} {width}: {layout}', flush=True)
                    if screenshots and ((width == 1440 and file.name in ('ch01.html', 'index.html', 'numerical-lab.html')) or (width == 390 and file.name == 'ch01.html')):
                        (ROOT / 'work').mkdir(exist_ok=True)
                        page.evaluate('scrollTo(0,0)')
                        page.screenshot(path=str(ROOT / 'work' / f'{file.stem}-{width}.png'))
                except Exception as exc:
                    errors.append(f'{file.name}/{width}: {type(exc).__name__}: {exc}')
            if requests:
                errors.append(f'Offline reader attempted network dependencies: {requests}')
            context.close()
        browser.close()
    report = dict(status='pass' if not errors else 'fail', pages=results,
                  errors=errors, offline=not bool(base_url),
                  scope='Desktop/mobile DOM and math layout, disclosures, filtering, copy, print, theme, and available interactive model checks.')
    name = 'live-browser-checks.json' if base_url else 'browser-checks.json'
    report_dir = Path(os.environ.get('LECTURE_VALIDATION_DIR', ROOT / 'validation'))
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / name).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(status=report['status'], checks=len(results), errors=errors), indent=2))
    return bool(errors)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser')
    parser.add_argument('--base-url')
    parser.add_argument('--screenshots', action='store_true')
    args = parser.parse_args()
    raise SystemExit(run(args.browser, args.base_url, args.screenshots))
