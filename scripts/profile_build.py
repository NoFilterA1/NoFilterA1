#!/usr/bin/env python3
"""Генератор SVG для профиля: считает данные через GitHub API и рисует карточки, статистику и тепловую карту.
Работает без сторонних сервисов: нужен только токен (GH_TOKEN) или авторизованный `gh`."""
import json, math, os, subprocess, urllib.request, urllib.error, datetime as dt, html, random
from pathlib import Path

USER = os.environ.get("PROFILE_USER", "NoFilterA1")
OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)
FEATURED = {  # репозиторий -> (подпись статуса, цвет акцента)
    "SAI_instructions": ("Framework", "#FFB347"),
    "competency-tracker": ("Prototype", "#2DD4BF"),
    "omen-hub": ("Active", "#FF7A59"),
    "obs-zmk-widget": ("Active", "#A78BFA"),
    "translAI": ("Active", "#60A5FA"),
    "LEX.KG": ("Final", "#4ADE80"),
}
LANG_COLORS = {"Python": "#3572A5", "HTML": "#e34c26", "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Shell": "#89e051",
               "QML": "#44a51c", "C": "#9aa0a6", "Batchfile": "#C1F12E", "CSS": "#8b5cf6", "Other": "#6b7280"}
DESC = {  # описание на английском для карточек, если в репозитории оно на другом языке
    "competency-tracker": "Student competency tracker built from digital footprint: profiles, curator panel, consent center, QR passport.",
}
AMBER = "#FFB347"
BG = "#0d1117"

def token():
    t = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if t: return t
    try: return subprocess.check_output(["gh", "auth", "token"], text=True).strip()
    except Exception: return None

def api(path, data=None):
    req = urllib.request.Request("https://api.github.com" + path, data=json.dumps(data).encode() if data else None)
    req.add_header("Accept", "application/vnd.github+json"); req.add_header("User-Agent", "profile-build")
    t = token()
    if t: req.add_header("Authorization", f"Bearer {t}")
    with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)

def esc(s): return html.escape(str(s), quote=True)
def wrap(text, width, lines):
    words, out, cur = (text or "").split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width: cur = (cur + " " + w).strip()
        else:
            out.append(cur); cur = w
    if cur: out.append(cur)
    if len(out) > lines:
        out = out[:lines]; out[-1] = out[-1][: max(0, width - 1)].rstrip(" .,;|-") + "…"
    return out

# ---------- данные ----------
user = api(f"/users/{USER}")
repos = [r for r in api(f"/users/{USER}/repos?per_page=100&sort=pushed") if not r["fork"]]
by_name = {r["name"]: r for r in repos}
langs = {}
for r in repos:
    try:
        for k, v in api(f"/repos/{USER}/{r['name']}/languages").items(): langs[k] = langs.get(k, 0) + v
    except Exception: pass
stars = sum(r["stargazers_count"] for r in repos)
cache = OUT.parent / "data"; cache.mkdir(exist_ok=True)
cal_file = cache / "calendar.json"
try:
    q = "query($l:String!){user(login:$l){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"
    cal = api("/graphql", {"query": q, "variables": {"l": USER}})["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    cal_file.write_text(json.dumps(cal))
except Exception as e:
    print("graphql failed, using cache:", e)
    cal = json.loads(cal_file.read_text()) if cal_file.exists() else {"totalContributions": 0, "weeks": []}

years = max(1, dt.datetime.now(dt.timezone.utc).year - int(user["created_at"][:4]))

# ---------- карточки репозиториев ----------
def repo_card(name, status, color):
    r = by_name.get(name)
    if not r: return
    desc = wrap(DESC.get(name) or r["description"] or "", 58, 3)
    lang = r["language"] or "Other"; lc = LANG_COLORS.get(lang, "#8b949e")
    pushed = dt.datetime.fromisoformat(r["pushed_at"].replace("Z", "+00:00")).strftime("%b %Y")
    lines = "".join(f'<text x="28" y="{84 + i * 20}" font-size="13.5" fill="#9ba7b4">{esc(l)}</text>' for i, l in enumerate(desc))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="540" height="168" viewBox="0 0 540 168" font-family="system-ui,-apple-system,'Segoe UI',Roboto,sans-serif">
<defs>
<linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{color}"/><stop offset=".55" stop-color="{color}" stop-opacity=".25"/><stop offset="1" stop-color="{color}" stop-opacity=".9"/></linearGradient>
<linearGradient id="sh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".09"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<radialGradient id="g" cx=".9" cy=".1" r=".8"><stop offset="0" stop-color="{color}" stop-opacity=".22"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>
<clipPath id="c"><rect x="1" y="1" width="538" height="166" rx="16"/></clipPath>
</defs>
<rect x="1" y="1" width="538" height="166" rx="16" fill="#11161d"/>
<rect x="1" y="1" width="538" height="166" rx="16" fill="url(#g)"/>
<g clip-path="url(#c)"><rect x="-200" y="0" width="160" height="168" fill="url(#sh)" transform="skewX(-18)"><animate attributeName="x" values="-200;700" dur="6s" repeatCount="indefinite"/></rect></g>
<rect x="1" y="1" width="538" height="166" rx="16" fill="none" stroke="url(#b)" stroke-width="1.6" stroke-dasharray="1200" stroke-dashoffset="1200"><animate attributeName="stroke-dashoffset" values="1200;0" dur="1.6s" fill="freeze"/></rect>
<circle cx="34" cy="38" r="5" fill="{color}"><animate attributeName="opacity" values="1;.35;1" dur="2.4s" repeatCount="indefinite"/></circle>
<text x="48" y="43" font-size="18" font-weight="700" fill="#f0f6fc">{esc(name)}</text>
<g transform="translate({540 - 28 - (len(status) * 7.4 + 22):.0f},24)"><rect width="{len(status) * 7.4 + 22:.0f}" height="26" rx="13" fill="{color}" fill-opacity=".14" stroke="{color}" stroke-opacity=".55"/><text x="{(len(status) * 7.4 + 22) / 2:.0f}" y="17.5" font-size="12" font-weight="600" fill="{color}" text-anchor="middle">{esc(status)}</text></g>
{lines}
<g transform="translate(28,146)" font-size="12.5" fill="#8b949e"><circle cx="5" cy="-4" r="5" fill="{lc}"/><text x="16" y="0">{esc(lang)}</text><text x="{16 + len(lang) * 7.2 + 18:.0f}" y="0">★ {r["stargazers_count"]}</text><text x="{16 + len(lang) * 7.2 + 56:.0f}" y="0">updated {pushed}</text></g>
</svg>'''
    (OUT / f"card-{name.replace('.', '-')}.svg").write_text(svg)

for n, (st, c) in FEATURED.items(): repo_card(n, st, c)

# ---------- статистика ----------
total = sum(langs.values()) or 1
top = sorted(langs.items(), key=lambda kv: -kv[1])
main, other = top[:6], sum(v for _, v in top[6:])
if other: main.append(("Other", other))
tiles = [(str(len(repos)), "public repositories"), (str(cal["totalContributions"]), "contributions, last 12 months"), (str(stars), "stars received"), (f"{years}+", "years on GitHub")]
tl = ""
for i, (num, lab) in enumerate(tiles):
    x = 30 + i * 262
    tl += f'''<g transform="translate({x},28)" opacity="0"><animate attributeName="opacity" values="0;1" dur=".7s" begin="{i * .18:.2f}s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="{x},44;{x},28" dur=".7s" begin="{i * .18:.2f}s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/>
<rect width="240" height="96" rx="14" fill="#11161d" stroke="#222a35"/><rect width="4" height="40" x="0" y="28" rx="2" fill="{AMBER}"/>
<text x="26" y="52" font-size="38" font-weight="800" fill="#f0f6fc">{esc(num)}</text><text x="26" y="78" font-size="13" fill="#8b949e">{esc(lab)}</text></g>'''
bar, leg, x0 = "", "", 30
barw = 1040
for i, (k, v) in enumerate(main):
    w = max(6, barw * v / total); c = LANG_COLORS.get(k, "#8b949e")
    bar += f'<rect x="{x0:.1f}" y="170" height="14" rx="3" fill="{c}" width="0"><animate attributeName="width" values="0;{w - 3:.1f}" dur="1s" begin="{.6 + i * .1:.1f}s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/></rect>'
    lx = 30 + (i % 4) * 262; ly = 214 + (i // 4) * 24
    leg += f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{c}"/><text x="{lx + 18}" y="{ly}" font-size="13" fill="#c9d1d9">{esc(k)} <tspan fill="#8b949e">{100 * v / total:.1f}%</tspan></text>'
    x0 += w
h = 214 + ((len(main) - 1) // 4) * 24 + 30
(OUT / "stats.svg").write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{h}" viewBox="0 0 1100 {h}" font-family="system-ui,-apple-system,'Segoe UI',Roboto,sans-serif">
<rect width="1100" height="{h}" rx="18" fill="{BG}"/>{tl}
<text x="30" y="158" font-size="13" font-weight="600" fill="#8b949e" letter-spacing=".08em">LANGUAGES BY CODE VOLUME</text>
<rect x="30" y="170" width="{barw}" height="14" rx="3" fill="#161b22"/>{bar}{leg}
</svg>''')

# ---------- тепловая карта ----------
weeks = cal["weeks"][-53:]
cell, gap, left, top_ = 15, 3, 52, 62
w = 1100
mx = max([d["contributionCount"] for wk in weeks for d in wk["contributionDays"]] or [1]) or 1
palette = ["#161b22", "#5a3a12", "#9a6118", "#e08f1f", AMBER]
cells, months = "", ""
last_m = -1
for ci, wk in enumerate(weeks):
    for d in wk["contributionDays"]:
        dd = dt.date.fromisoformat(d["date"]); n = d["contributionCount"]
        lvl = 0 if n == 0 else min(4, 1 + int(3 * (n - 1) / max(1, mx - 1))) if mx > 1 else 4
        x = left + ci * (cell + gap); y = top_ + dd.weekday() * (cell + gap) if False else top_ + ((dd.weekday() + 1) % 7) * (cell + gap)
        cells += f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{palette[lvl]}" opacity="0"><title>{d["date"]}: {n}</title><animate attributeName="opacity" values="0;1" dur=".45s" begin="{ci * .03:.2f}s" fill="freeze"/>' + (f'<animate attributeName="fill" values="{palette[lvl]};#ffe0a8;{palette[lvl]}" dur="3s" begin="{4 + ci * .06:.2f}s" repeatCount="indefinite"/>' if lvl >= 3 else "") + '</rect>'
    first = dt.date.fromisoformat(wk["contributionDays"][0]["date"])
    if first.month != last_m and first.day <= 14:
        months += f'<text x="{left + ci * (cell + gap)}" y="52" font-size="11" fill="#8b949e">{first.strftime("%b")}</text>'; last_m = first.month
days = "".join(f'<text x="20" y="{top_ + (i) * (cell + gap) + 10}" font-size="10" fill="#6e7681">{n}</text>' for i, n in ((1, "Mon"), (3, "Wed"), (5, "Fri")))
lx0 = w - 30 - 40 - 5 * 17
lg = "".join(f'<rect x="{lx0 + i * 17}" y="{top_ + 7 * (cell + gap) + 14}" width="13" height="13" rx="3" fill="{c}"/>' for i, c in enumerate(palette))
hh = top_ + 7 * (cell + gap) + 44
(OUT / "activity.svg").write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{hh}" viewBox="0 0 {w} {hh}" font-family="system-ui,-apple-system,'Segoe UI',Roboto,sans-serif">
<rect width="{w}" height="{hh}" rx="18" fill="{BG}"/>
<text x="30" y="30" font-size="15" font-weight="700" fill="#f0f6fc">{cal["totalContributions"]} contributions in the last year</text>
{months}{days}{cells}
<text x="{lx0 - 8}" y="{top_ + 7 * (cell + gap) + 25}" font-size="11" fill="#6e7681" text-anchor="end">Less</text>{lg}<text x="{lx0 + 5 * 17 + 4}" y="{top_ + 7 * (cell + gap) + 25}" font-size="11" fill="#6e7681">More</text>
</svg>''')
print("ok", len(repos), "repos,", cal["totalContributions"], "contributions,", stars, "stars")
