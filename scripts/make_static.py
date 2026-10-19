#!/usr/bin/env python3
"""Рисует неменяющиеся SVG: hero и разделитель. Запуск вручную: python scripts/make_static.py"""
import math, random
from pathlib import Path
OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)
AMBER, ORANGE, VIOLET, TEAL = "#FFB347", "#FF7A59", "#A78BFA", "#2DD4BF"

# ---------- hero ----------
W, H = 1200, 400
random.seed(36)
nodes = [(random.randint(30, 1170), random.randint(24, 376)) for _ in range(34)]
edges = [(i, j) for i in range(len(nodes)) for j in range(i + 1, len(nodes)) if math.dist(nodes[i], nodes[j]) < 150]
net = ""
for k, (i, j) in enumerate(edges):
    (x1, y1), (x2, y2) = nodes[i], nodes[j]
    net += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{AMBER}" stroke-opacity=".10"><animate attributeName="stroke-opacity" values=".05;.28;.05" dur="{5 + (k % 5)}s" begin="{(k % 7) * .6:.1f}s" repeatCount="indefinite"/></line>'
for k, (x, y) in enumerate(nodes):
    col = [AMBER, ORANGE, VIOLET, TEAL][k % 4]
    net += f'<circle cx="{x}" cy="{y}" r="2.6" fill="{col}" opacity=".7"><animate attributeName="r" values="2;4;2" dur="{3 + k % 4}s" begin="{(k % 6) * .5:.1f}s" repeatCount="indefinite"/><animate attributeName="opacity" values=".35;.95;.35" dur="{3 + k % 4}s" begin="{(k % 6) * .5:.1f}s" repeatCount="indefinite"/></circle>'

LINES = ["AI systems architect", "Multi-agent frameworks · prompt engineering", "Full-stack prototypes · Linux tooling", "Turning limits into opportunities"]
CHAR = 15.6; FS = 26; X0 = 70; Y = 232
CYC = 20; SLOT = 1 / len(LINES)
typed = ""
for i, t in enumerate(LINES):
    wpx = round(len(t) * CHAR)
    s, e = i * SLOT, i * SLOT + SLOT * 0.38
    keys = [(0, 0)] if s == 0 else [(0, 0), (s, 0)]
    keys += [(e, wpx), (1, wpx)]
    kt = ";".join(f"{k:.4f}" for k, _ in keys); kv = ";".join(str(v) for _, v in keys)
    op = []
    if s > 0: op.append((0, 0))
    op.append((s, 1))
    if s + SLOT < 1: op.append((s + SLOT, 0))
    okt = ";".join(f"{k:.4f}" for k, _ in op); okv = ";".join(str(v) for _, v in op)
    cx = ";".join(str(X0 + v) for _, v in keys)
    typed += f'''<g opacity="0"><animate attributeName="opacity" calcMode="discrete" keyTimes="{okt}" values="{okv}" dur="{CYC}s" repeatCount="indefinite"/>
<clipPath id="tc{i}"><rect x="{X0}" y="{Y - 30}" height="42" width="0"><animate attributeName="width" keyTimes="{kt}" values="{kv}" dur="{CYC}s" repeatCount="indefinite"/></rect></clipPath>
<text x="{X0}" y="{Y}" font-family="ui-monospace,SFMono-Regular,Consolas,'Liberation Mono',monospace" font-size="{FS}" fill="#e6edf3" textLength="{wpx}" lengthAdjust="spacingAndGlyphs" clip-path="url(#tc{i})">{t}</text>
<rect y="{Y - 25}" width="12" height="32" fill="{AMBER}"><animate attributeName="x" keyTimes="{kt}" values="{cx}" dur="{CYC}s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur=".9s" repeatCount="indefinite"/></rect></g>'''

cx0, cy0 = 985, 200
orbit = ""
for r, dur, n, col in ((58, 10, 1, AMBER), (100, 17, 2, VIOLET), (142, 26, 3, TEAL)):
    orbit += f'<circle cx="{cx0}" cy="{cy0}" r="{r}" fill="none" stroke="{col}" stroke-opacity=".35" stroke-dasharray="3 7"><animateTransform attributeName="transform" type="rotate" from="0 {cx0} {cy0}" to="{360 if r != 100 else -360} {cx0} {cy0}" dur="{dur * 2}s" repeatCount="indefinite"/></circle>'
    for k in range(n):
        a0 = 360 * k / n
        orbit += f'<g><animateTransform attributeName="transform" type="rotate" from="{a0} {cx0} {cy0}" to="{a0 + (360 if r != 100 else -360)} {cx0} {cy0}" dur="{dur}s" repeatCount="indefinite"/><circle cx="{cx0 + r}" cy="{cy0}" r="{6 if r == 58 else 5}" fill="{col}"><animate attributeName="opacity" values="1;.5;1" dur="2.2s" repeatCount="indefinite"/></circle><circle cx="{cx0 + r}" cy="{cy0}" r="12" fill="{col}" opacity=".15"/></g>'
orbit += f'<circle cx="{cx0}" cy="{cy0}" r="30" fill="url(#core)"><animate attributeName="r" values="28;34;28" dur="3.4s" repeatCount="indefinite"/></circle><circle cx="{cx0}" cy="{cy0}" r="12" fill="#fff" opacity=".9"><animate attributeName="opacity" values=".6;1;.6" dur="3.4s" repeatCount="indefinite"/></circle>'

CH = [("building · SAI framework", AMBER, "#FFD9A0"), ("shipping · Competency Tracker", TEAL, "#5eead4"), ("tinkering · ZMK keyboards", VIOLET, "#c4b5fd")]
chips, cxp = "", X0
for n, (t, col, tc) in enumerate(CH):
    wc = round(len(t) * 7.7 + 34)
    chips += f'<rect x="{cxp}" y="298" width="{wc}" height="34" rx="17" fill="{col}" fill-opacity=".12" stroke="{col}" stroke-opacity=".5"/><circle cx="{cxp + 16}" cy="315" r="3.5" fill="{col}"><animate attributeName="opacity" values="1;.3;1" dur="2s" begin="{n * .4}s" repeatCount="indefinite"/></circle><text x="{cxp + 28}" y="320" fill="{tc}">{t}</text>'
    cxp += wc + 12
chips = f'<g font-family="system-ui,-apple-system,Segoe UI,Roboto,sans-serif" font-size="14" opacity="0"><animate attributeName="opacity" values="0;1" dur="1s" begin="1.4s" fill="freeze"/>{chips}</g>'
(OUT / "hero.svg").write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="NoFilterA1 — AI systems architect">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0a0e14"/><stop offset=".5" stop-color="#14101f"><animate attributeName="stop-color" values="#14101f;#10202a;#241a12;#14101f" dur="16s" repeatCount="indefinite"/></stop><stop offset="1" stop-color="#0a1018"/></linearGradient>
<linearGradient id="nm" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff"/><stop offset=".55" stop-color="{AMBER}"/><stop offset="1" stop-color="{ORANGE}"/></linearGradient>
<radialGradient id="core"><stop offset="0" stop-color="{AMBER}"/><stop offset="1" stop-color="{ORANGE}" stop-opacity=".1"/></radialGradient>
<radialGradient id="gl1"><stop offset="0" stop-color="{AMBER}" stop-opacity=".30"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient>
<radialGradient id="gl2"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".28"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
<linearGradient id="sh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{AMBER}" stop-opacity="0"/><stop offset=".5" stop-color="{AMBER}"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient>
<pattern id="grid" width="36" height="36" patternUnits="userSpaceOnUse"><path d="M36 0H0V36" fill="none" stroke="#fff" stroke-opacity=".035"/></pattern>
<clipPath id="r"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<g clip-path="url(#r)">
<rect width="{W}" height="{H}" fill="url(#bg)"/><rect width="{W}" height="{H}" fill="url(#grid)"/>
<circle r="300" fill="url(#gl1)"><animate attributeName="cx" values="120;460;120" dur="15s" repeatCount="indefinite"/><animate attributeName="cy" values="60;320;60" dur="12s" repeatCount="indefinite"/></circle>
<circle r="280" fill="url(#gl2)"><animate attributeName="cx" values="1080;760;1080" dur="17s" repeatCount="indefinite"/><animate attributeName="cy" values="340;70;340" dur="13s" repeatCount="indefinite"/></circle>
{net}{orbit}
<g font-family="ui-monospace,SFMono-Regular,Consolas,'Liberation Mono',monospace" font-size="16" fill="#6e7681" opacity="0"><animate attributeName="opacity" values="0;1" dur=".8s" begin=".2s" fill="freeze"/><text x="{X0}" y="92"><tspan fill="{AMBER}">~</tspan> $ whoami</text></g>
<text x="{X0 - 2}" y="168" font-family="system-ui,-apple-system,'Segoe UI',Roboto,sans-serif" font-size="76" font-weight="800" fill="url(#nm)" opacity="0" letter-spacing="-1"><animate attributeName="opacity" values="0;1" dur="1s" begin=".4s" fill="freeze"/>NoFilterA1</text>
{typed}
{chips}
<rect x="-400" y="394" width="400" height="4" fill="url(#sh)"><animate attributeName="x" values="-400;1200" dur="5s" repeatCount="indefinite"/></rect>
</g></svg>''')

# ---------- разделитель-волна ----------
# Период волны ровно 440 px: сдвиг на любую долю периода туда и обратно, без разрывов и пустых краёв.
def wave(amp, ph, col, op):
    pts = " ".join(f"{x},{12 + amp * math.sin(x * 2 * math.pi / 440 + ph):.1f}" for x in range(-480, 1741, 10))
    return f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-opacity="{op}" stroke-width="2" stroke-linejoin="round"/>'
SPL = 'calcMode="spline" keyTimes="0;.5;1" keySplines=".45 0 .55 1;.45 0 .55 1"'
(OUT / "divider.svg").write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="24" viewBox="0 0 1200 24" role="presentation">
<g>{wave(5, 0, AMBER, .75)}<animateTransform attributeName="transform" type="translate" values="0 0;-220 0;0 0" dur="9s" {SPL} repeatCount="indefinite"/></g>
<g>{wave(4, 2, VIOLET, .55)}<animateTransform attributeName="transform" type="translate" values="-110 0;110 0;-110 0" dur="12s" {SPL} repeatCount="indefinite"/></g>
</svg>''')
print("static ok")
