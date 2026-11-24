# content.py로 index.html, ox.html, concepts.html을 만든다. (26-2-exercise 구조를 따름)
# 실행: python -I src/build.py  (레포 폴더에서)
import html, importlib.util, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('content', os.path.join(ROOT, 'src', 'content.py'))
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
UNITS = C.UNITS
IMG = os.path.join(ROOT, 'img')
TOTAL = 0
BRAND = '철도 상식 OX'


def number():
    """문항 번호. 기록이 q001 같은 번호로 저장되므로 기존 번호는 바꾸지 않는다.
    나중에 더한 개념은 'late': 1(또는 2…)을 달면 나머지 뒤 번호를 받는다."""
    global TOTAL
    n = 0
    for u in UNITS:
        u['n'] = 0
    for late in (0, 1, 2, 3):
        for u in UNITS:
            for c in u['concepts']:
                if int(c.get('late', 0)) != late:
                    continue
                c['nums'] = []
                for _ in c['q']:
                    n += 1
                    c['nums'].append(n)
                    u['n'] += 1
    TOTAL = n
    return n


def ranges(ns):
    ns = sorted(ns)
    parts, start = [], ns[0]
    for a, b in zip(ns, ns[1:] + [None]):
        if b != a + 1:
            parts.append(f'{start}~{a}' if start != a else f'{start}')
            start = b
    return ', '.join(parts) + '번'


def head(title, desc):
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="style.css?v=1">
</head>
'''


def nav(active):
    items = [('index.html', '처음으로'), ('ox.html', f'OX {TOTAL}문제'), ('concepts.html', '기본 상식')]
    links = ''.join(f'<a href="{h}"{" aria-current=page" if h == active else ""}>{t}</a>' for h, t in items)
    return f'<header class="top"><div class="wrap topin"><a class="brand" href="index.html">{BRAND}</a><nav>{links}</nav></div></header>'


def groups():
    out = []
    for u in UNITS:
        if not out or out[-1]['big'] != u['big']:
            out.append({'big': u['big'], 'key': u['key'], 'units': []})
        out[-1]['units'].append(u)
    return out


def srcs(names):
    return ', '.join(f'<a href="{C.NW}{n}" target="_blank" rel="noopener">{n}</a>' for n in names)


FOOT = '<footer class="wrap foot">철도 상식 OX · 글 출처 나무위키(CC BY-NC-SA 2.0 KR) · 사진 Wikimedia Commons</footer>'


def build_index():
    rows = ''
    for g in groups():
        cnt = sum(u['n'] for u in g['units'])
        ccnt = sum(len(u['concepts']) for u in g['units'])
        rows += f'<tr class="grp {g["key"]}"><th scope="colgroup">{g["big"]}</th><td>{ccnt}</td><td>{cnt}</td></tr>'
        for u in g['units']:
            ns = [n for c in u['concepts'] for n in c['nums']]
            rows += (f'<tr><td><a href="ox.html#{u["id"]}">{u["title"]}</a></td>'
                     f'<td>{len(u["concepts"])}</td><td>{u["n"]}<span class="rng">{ranges(ns)}</span></td></tr>')
    allc = sum(len(u['concepts']) for u in UNITS)
    body = f'''<body>
<div class="stick" id="stick">{nav('index.html')}</div>
<main class="wrap">
<section class="hero">
<h1>철도 상식 OX</h1>
<p>철도의 역사, 궤간, 전기로 달리는 원리, 신호, 고속철도, 지하철과 특별한 철도까지. 면접에서 물어볼 만한 철도 기본 상식을 OX 문제로 확인합니다.</p>
<div class="cta">
<a class="big" href="ox.html"><b>OX {TOTAL}문제 풀기</b><span>누르면 바로 정답과 풀이가 나옵니다</span></a>
<a class="big alt" href="concepts.html"><b>기본 상식 보기</b><span>핵심 내용 {allc}개, 사진과 함께</span></a>
</div>
</section>
<section>
<h2>문항 구성</h2>
<p class="lead">단원 이름을 누르면 그 문제로 이동합니다. 어렵게 느껴지면 기본 상식을 먼저 읽고 풀어 보세요.</p>
<div class="tablewrap"><table class="plan">
<thead><tr><th scope="col">단원</th><th scope="col">핵심</th><th scope="col">문항</th></tr></thead>
<tbody>{rows}
<tr class="sum"><th scope="row">합계</th><td>{allc}</td><td>{TOTAL}</td></tr></tbody>
</table></div>
</section>
</main>
{FOOT}
<script src="app.js?v=1"></script>
</body></html>
'''
    write('index.html', head(BRAND, f'철도 기본 상식 OX {TOTAL}문제와 정리') + body)


def build_ox():
    jump = ''
    sec = ''
    for g in groups():
        jump += f'<div class="jg {g["key"]}"><b>{g["big"]}</b>'
        for u in g['units']:
            jump += f'<a href="#{u["id"]}">{u["title"]}<span data-prog="{u["id"]}">{u["n"]}문제</span></a>'
        jump += '</div>'
    for u in UNITS:
        sec += f'<section class="unit {u["key"]}" id="{u["id"]}" data-unit="{u["id"]}">'
        sec += f'<p class="crumb">{u["big"]}</p><h2>{u["title"]}</h2>'
        for c in u['concepts']:
            for n, (st, a, sol) in zip(c['nums'], c['q']):
                qid = f'q{n:03d}'
                sec += f'''<article class="q" id="{qid}" data-a="{a}" data-unit="{u["id"]}">
<div class="qrow"><span class="qn">{n}</span><p class="st">{html.escape(st)}</p>
<div class="btns" role="group" aria-label="{n}번 답 고르기"><button type="button" class="o" data-v="O" aria-label="O, 맞다">O</button><button type="button" class="x" data-v="X" aria-label="X, 틀리다">X</button></div></div>
<div class="sol" hidden><p class="res"></p><p class="exp"><b>풀이</b> {html.escape(sol)}</p>
<p class="solfoot"><a class="go" href="concepts.html?from={qid}#{c["id"]}">상식 보기: {html.escape(c["title"])}</a><button type="button" class="again">다시 풀기</button></p></div>
</article>
'''
        sec += '</section>'
    body = f'''<body class="oxpage">
<div class="stick" id="stick">{nav('ox.html')}
<div class="bar"><div class="wrap barin">
<div class="score" aria-live="polite"><b id="done">0</b>/{TOTAL} 풀이 · 맞힘 <b id="right">0</b></div>
<div class="filters" role="group" aria-label="문제 거르기">
<button type="button" data-f="all" aria-pressed="true">전체</button>
<button type="button" data-f="todo" aria-pressed="false">안 푼 문제</button>
<button type="button" data-f="wrong" aria-pressed="false">틀린 문제</button>
</div>
<div class="tools"><button type="button" id="showall" aria-pressed="false">풀이 모두 보기</button><button type="button" id="reset">기록 지우기</button></div>
</div><div class="meter"><i id="meter"></i></div></div></div>
<main class="wrap">
<h1>철도 상식 OX {TOTAL}문제</h1>
<p class="lead">문장이 맞으면 O, 틀리면 X를 누르세요. 푼 기록은 지금 쓰는 기기의 브라우저에만 저장됩니다.</p>
<details class="jump"><summary>단원 바로가기</summary><div class="jgs">{jump}</div></details>
<p class="empty" id="empty" hidden>조건에 맞는 문제가 없습니다.</p>
{sec}
</main>
{FOOT}
<script src="app.js?v=1"></script>
</body></html>
'''
    write('ox.html', head(f'철도 상식 OX {TOTAL}문제', '철도 기본 상식 OX 문제') + body)


def size(f):
    from PIL import Image
    return Image.open(os.path.join(IMG, f)).size


def figure(items):
    s = '<div class="figs photos">'
    for f, alt, cap in items:
        w, h = size(f)
        s += (f'<figure class="ph"><a href="img/{f}" target="_blank" rel="noopener" title="크게 보기">'
              f'<img src="img/{f}" alt="{html.escape(alt)}" width="{w}" height="{h}" loading="lazy"></a><figcaption>{html.escape(cap)}</figcaption></figure>')
    return s + '</div>'


def build_concepts():
    toc = ''
    main = ''
    for g in groups():
        toc += f'<div class="tg {g["key"]}"><b>{g["big"]}</b>'
        for u in g['units']:
            toc += f'<a href="#k{u["id"]}">{u["title"]}</a>'
        toc += '</div>'
    for u in UNITS:
        main += f'<section class="kunit {u["key"]}" id="k{u["id"]}"><p class="crumb">{u["big"]}</p><h2>{u["title"]}</h2>'
        for c in u['concepts']:
            nums = ' '.join(f'<a href="ox.html#q{n:03d}">{n}번</a>' for n in c['nums'])
            main += f'<article class="concept" id="{c["id"]}"><h3>{c["title"]}<span class="pg">나무위키: {srcs(c["src"])}</span></h3>'
            if c.get('points'):
                main += '<ul>' + ''.join(f'<li>{p}</li>' for p in c['points']) + '</ul>'
            if c.get('img'):
                main += figure(c['img'])
            if c.get('table'):
                t = c['table']
                main += '<div class="tablewrap"><table class="cmp"><thead><tr>' + ''.join(f'<th scope="col">{h}</th>' for h in t['head']) + '</tr></thead><tbody>'
                for r in t['rows']:
                    main += f'<tr><th scope="row">{r[0]}</th>' + ''.join(f'<td>{x}</td>' for x in r[1:]) + '</tr>'
                main += '</tbody></table></div>'
            if c.get('warn'):
                main += f'<p class="warn"><b>헷갈리지 말기</b> {c["warn"]}</p>'
            main += (f'<p class="rel">이 내용의 OX 문제: {nums}</p>' if nums else '') + '</article>'
        main += '</section>'
    body = f'''<body class="kpage">
<div class="stick" id="stick">{nav('concepts.html')}</div>
<div class="wrap klayout">
<aside class="toc"><details open><summary>목차</summary>{toc}</details></aside>
<main>
<h1>기본 상식</h1>
<p class="lead">단원별 핵심 철도 상식입니다. 사진을 누르면 크게 볼 수 있고, 문서 이름을 누르면 원래 나무위키 문서가 열립니다.</p>
{main}
<p class="credit">{C.CREDITS}</p>
</main>
</div>
<a class="back" id="back" href="ox.html" hidden>문제로 돌아가기</a>
<script src="app.js?v=1"></script>
</body></html>
'''
    write('concepts.html', head('기본 상식', '철도 기본 상식 정리') + body)


def write(name, s):
    with open(os.path.join(ROOT, name), 'w', encoding='utf8', newline='\n') as f:
        f.write(s)


def check():
    ids = [c['id'] for u in UNITS for c in u['concepts']]
    assert len(ids) == len(set(ids)), '개념 id 중복'
    answers = [q[1] for u in UNITS for c in u['concepts'] for q in c['q']]
    assert set(answers) <= {'O', 'X'}
    run = best = 0
    prev = None
    for a in answers:
        run = run + 1 if a == prev else 1
        prev = a
        best = max(best, run)
    print('문항', TOTAL, 'O', answers.count('O'), 'X', answers.count('X'), '개념', len(ids), '같은 답 최대 연속', best)
    for u in UNITS:
        for c in u['concepts']:
            for f, _, _ in c.get('img', []):
                assert os.path.exists(os.path.join(IMG, f)), f


if __name__ == '__main__':
    number()
    check()
    build_index()
    build_ox()
    build_concepts()
