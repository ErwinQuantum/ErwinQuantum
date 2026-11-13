"""
The last year of contributions as a city under construction, in the style of the
"Obras" model on edwinvasquez.dev: each day is a lot, its building as tall as that
day's work, terracotta (civil) turning blue (software) as the year goes by. The
buildings rise on load, week by week. Standard library only.

    GITHUB_TOKEN=... python city/build.py [login] [out_dir]

Writes city-dark.svg and city-light.svg. Private contributions are included as
counts only, when the profile shows them (GitHub never exposes their details).
"""

import datetime as dt
import json
import math
import os
import sys
import urllib.request

LOGIN = sys.argv[1] if len(sys.argv) > 1 else "ErwinQuantum"
OUT = sys.argv[2] if len(sys.argv) > 2 else "dist"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}"""

THEMES = {
    "dark": dict(civil=(227, 139, 98), accent=(125, 180, 220), ink="#e8e2d9", muted="#8a8378", rule="#3a3631", lot="#2a2723"),
    "light": dict(civil=(168, 74, 40), accent=(31, 95, 139), ink="#2a2622", muted="#7a7268", rule="#d8d0c4", lot="#e7e0d5"),
}

W, H = 1200, 430
U = (18.4, -2.4)  # one week along the street (up and to the right)
V = (9.6, 5.4)  # one weekday across it (down and to the right)
ORIGIN = (60, 300)
GAP = 0.16  # space between lots, as a share of a lot
MAX_H = 108
MONO = 'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"'


def fetch(login):
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is not set")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-city"},
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.load(res)
    if "errors" in data:
        sys.exit(json.dumps(data["errors"]))
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def pt(w, d, up=0.0):
    return (ORIGIN[0] + w * U[0] + d * V[0], ORIGIN[1] + w * U[1] + d * V[1] - up)


def poly(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shade(c, k):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v * k))) for v in c)


def build(cal, theme):
    c = THEMES[theme]
    weeks = cal["weeks"]
    days = [(wi, d) for wi, wk in enumerate(weeks) for d in wk["contributionDays"]]
    peak = max((d["contributionCount"] for _, d in days), default=0) or 1
    n_weeks = len(weeks)
    last = days[-1][1]["date"] if days else ""

    o = []
    a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
      f'aria-label="{cal["totalContributions"]} contributions in the last year, drawn as a city under construction">')

    # The sheet, like the header: dashed frame, crop marks, title block.
    m = 14
    a(f'<rect x="{m}" y="{m}" width="{W - 2 * m}" height="{H - 2 * m}" rx="10" fill="none" stroke="{c["rule"]}" stroke-dasharray="2 6"/>')
    for x, y, dx, dy in [(m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)]:
        a(f'<path d="M{x},{y + dy * 22} V{y} H{x + dx * 22}" fill="none" stroke="{c["muted"]}" stroke-width="1.4"/>')
    a(f'<text x="34" y="46" {MONO} font-size="11" letter-spacing="2.5" fill="{c["muted"]}">LÁMINA 01 · LA OBRA DEL AÑO</text>')
    a(f'<text x="34" y="78" {MONO} font-size="26" font-weight="600" fill="{c["ink"]}">{cal["totalContributions"]:,}</text>')
    a(f'<text x="34" y="98" {MONO} font-size="11" letter-spacing="1.5" fill="{c["muted"]}">contributions in the last year</text>')
    a(f'<text x="{W - 34}" y="{H - 30}" text-anchor="end" {MONO} font-size="11" letter-spacing="2" fill="{c["muted"]}">edwinvasquez.dev</text>')
    a(f'<text x="34" y="{H - 30}" {MONO} font-size="11" letter-spacing="2" fill="{c["muted"]}">ONE DAY = ONE LOT · HEIGHT = WORK DONE</text>')

    # Month marks along the front edge of the street.
    seen = set()
    for wi, wk in enumerate(weeks):
        first = wk["contributionDays"][0]["date"]
        month = first[:7]
        if month in seen or wi == 0:
            seen.add(month)
            continue
        seen.add(month)
        x, y = pt(wi, 7.6)
        label = dt.date.fromisoformat(first).strftime("%b").upper()
        a(f'<text x="{x:.1f}" y="{y + 12:.1f}" {MONO} font-size="9.5" letter-spacing="1.5" fill="{c["muted"]}">{label}</text>')

    # Lots and buildings, painted back to front: later weeks sit further back.
    order = sorted(days, key=lambda e: (-e[0], e[1]["weekday"]))
    for wi, day in order:
        dd = day["weekday"]
        count = day["contributionCount"]
        g = GAP / 2
        base = [pt(wi + g, dd + g), pt(wi + 1 - g, dd + g), pt(wi + 1 - g, dd + 1 - g), pt(wi + g, dd + 1 - g)]
        if count == 0:
            a(f'<polygon points="{poly(base)}" fill="{c["lot"]}" opacity=".55"/>')
            continue
        t = wi / max(1, n_weeks - 1)
        col = mix(c["civil"], c["accent"], t)
        h = 5 + (MAX_H - 5) * math.log1p(count) / math.log1p(peak)
        top = [(x, y - h) for x, y in base]
        # Faces in local coordinates (origin at the lot's front corner), so the whole
        # building can grow upwards from its base with one scale transform.
        ox, oy = base[2]
        rel = lambda pts: [(x - ox, y - oy) for x, y in pts]
        front = [base[3], base[2], top[2], top[3]]  # along the week direction, facing down
        side = [base[1], base[2], top[2], top[1]]  # along the weekday direction, facing right
        delay = 0.25 + wi * 0.035 + dd * 0.01
        a(f'<g transform="translate({ox:.1f},{oy:.1f})"><g transform="scale(1 0)">')
        a(f'<animateTransform attributeName="transform" type="scale" values="1 0;1 1" keyTimes="0;1" keySplines=".2 .7 .2 1" calcMode="spline" begin="{delay:.2f}s" dur=".9s" fill="freeze"/>')
        a(f'<polygon points="{poly(rel(front))}" fill="{shade(col, .62)}"/>')
        a(f'<polygon points="{poly(rel(side))}" fill="{shade(col, .80)}"/>')
        a(f'<polygon points="{poly(rel(top))}" fill="{shade(col, 1.0)}" stroke="{shade(col, 1.15)}" stroke-width=".6"/>')
        # Lit windows on the taller ones.
        if h > 34:
            for k in range(1, int(h // 16)):
                fx, fy = (front[0][0] + front[1][0]) / 2 - ox, (front[0][1] + front[1][1]) / 2 - oy - k * 16
                a(f'<rect x="{fx - 3:.1f}" y="{fy - 3:.1f}" width="6" height="2.2" fill="#ffe7b3" opacity=".75"/>')
        a("</g></g>")
        if day["date"] == last:
            lx, ly = top[2][0], top[2][1]
            a(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="3.5" fill="#fff"><animate attributeName="opacity" values="1;.2;1" dur="1.6s" repeatCount="indefinite"/></circle>')

    a("</svg>")
    return "\n".join(o)


def main():
    cal = fetch(LOGIN)
    os.makedirs(OUT, exist_ok=True)
    for theme in THEMES:
        path = os.path.join(OUT, f"city-{theme}.svg")
        with open(path, "w", encoding="utf8") as fh:
            fh.write(build(cal, theme))
        print(path, os.path.getsize(path), "bytes,", cal["totalContributions"], "contributions")


if __name__ == "__main__":
    main()
