# Animated header for the GitHub profile README: the qubit (Bloch sphere) with its state
# vector precessing, inside truss rings that turn, in the site's palette. Pure SVG + SMIL
# (works inside <img>, no scripts, no external services). Writes header-dark.svg / header-light.svg.
import math, os

W, H = 1200, 320
CX, CY, R = 600, 162, 74
OUT = os.path.dirname(os.path.abspath(__file__))

THEMES = {
    "dark": dict(civil="#e38b62", accent="#7db4dc", ink="#e8e2d9", muted="#8a8378", rule="#3a3631", core1="#ffffff", core2="#7db4dc"),
    "light": dict(civil="#a84a28", accent="#1f5f8b", ink="#2a2622", muted="#7a7268", rule="#d8d0c4", core1="#ffffff", core2="#1f5f8b"),
}

def f(x):
    return f"{x:.1f}"

def ellipse_path(cx, cy, rx, ry):
    return f"M{f(cx - rx)},{f(cy)} a{f(rx)},{f(ry)} 0 1,0 {f(2 * rx)},0 a{f(rx)},{f(ry)} 0 1,0 {f(-2 * rx)},0"

def series(fn, n=72):
    return ";".join(f(fn(i / n)) for i in range(n + 1))

def build(t):
    c = THEMES[t]
    out = []
    a = out.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Edwin Vásquez — a qubit inside turning truss rings">')
    a(f"""<defs>
  <radialGradient id="core" cx="40%" cy="35%" r="65%"><stop offset="0" stop-color="{c['core1']}"/><stop offset="1" stop-color="{c['core2']}"/></radialGradient>
  <radialGradient id="halo"><stop offset="0" stop-color="{c['accent']}" stop-opacity=".28"/><stop offset="1" stop-color="{c['accent']}" stop-opacity="0"/></radialGradient>
  <radialGradient id="warm"><stop offset="0" stop-color="{c['civil']}" stop-opacity=".16"/><stop offset="1" stop-color="{c['civil']}" stop-opacity="0"/></radialGradient>
  <linearGradient id="mix" x1="0" x2="1"><stop offset="0" stop-color="{c['civil']}"/><stop offset="1" stop-color="{c['accent']}"/></linearGradient>
</defs>""")

    # Sheet: thin frame with crop marks, like the site's drawings.
    m = 14
    a(f'<g stroke="{c["rule"]}" stroke-width="1" fill="none">')
    a(f'<rect x="{m}" y="{m}" width="{W - 2 * m}" height="{H - 2 * m}" rx="10" stroke-dasharray="2 6" opacity=".7"/>')
    for x, y, dx, dy in [(m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)]:
        a(f'<path d="M{x},{y + dy * 22} V{y} H{x + dx * 22}" stroke="{c["muted"]}" stroke-width="1.4"/>')
    a("</g>")
    a(f'<text x="34" y="44" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="11" letter-spacing="2.5" fill="{c["muted"]}">LÁMINA 00 · EDWIN VÁSQUEZ</text>')
    a(f'<text x="{W - 34}" y="{H - 30}" text-anchor="end" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="11" letter-spacing="2" fill="{c["muted"]}">edwinvasquez.dev</text>')
    a(f'<text x="34" y="{H - 30}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="11" letter-spacing="2" fill="{c["muted"]}">CIVIL → SOFTWARE → QUANTUM</text>')

    a(f'<ellipse cx="{CX}" cy="{CY + 60}" rx="360" ry="70" fill="url(#warm)"/>')
    a(f'<circle cx="{CX}" cy="{CY}" r="{R * 2.2}" fill="url(#halo)"/>')

    # Rings: two chords and a zigzag (Warren truss) between them, which slides to look like it turns.
    rings = [
        dict(rx=470, ry=78, rot=-7, color=c["civil"], dur=46, pulse=9, rev=False),
        dict(rx=300, ry=92, rot=16, color="url(#mix)", dur=34, pulse=7, rev=True),
        dict(rx=545, ry=104, rot=-2, color=c["accent"], dur=58, pulse=11, rev=False),
    ]
    for i, r in enumerate(rings):
        rx, ry = r["rx"], r["ry"]
        a(f'<g transform="rotate({r["rot"]} {CX} {CY})" fill="none" stroke="{r["color"]}">')
        a(f'<ellipse cx="{CX}" cy="{CY}" rx="{rx}" ry="{ry}" stroke-width="1.6" opacity=".85"/>')
        a(f'<ellipse cx="{CX}" cy="{CY}" rx="{rx - 9}" ry="{ry - 7}" stroke-width="1" opacity=".55"/>')
        # Truss: a dashed ellipse in between, its dashes sliding.
        per = 2 * math.pi * math.sqrt((rx * rx + ry * ry) / 2)
        a(f'<ellipse cx="{CX}" cy="{CY}" rx="{rx - 4.5}" ry="{ry - 3.5}" stroke-width="7.5" stroke-dasharray="1 13" opacity=".35">')
        a(f'<animate attributeName="stroke-dashoffset" from="0" to="{"-" if r["rev"] else ""}{f(per / 5)}" dur="{r["dur"] / 5:.0f}s" repeatCount="indefinite"/></ellipse>')
        path = ellipse_path(CX, CY, rx - 4.5, ry - 3.5)
        # Nodes riding the ring (the technologies on the site), and an energy pulse.
        for k in range(5):
            a(f'<circle r="4.2" fill="{c["civil"] if i == 0 else c["accent"]}" stroke="none" opacity=".9">')
            a(f'<animateMotion dur="{r["dur"]}s" repeatCount="indefinite" begin="-{r["dur"] * k / 5:.1f}s" path="{path}"{" keyPoints=\"1;0\" keyTimes=\"0;1\" calcMode=\"linear\"" if r["rev"] else ""}/></circle>')
        a(f'<circle r="2.6" fill="{c["core1"]}" stroke="none"><animateMotion dur="{r["pulse"]}s" repeatCount="indefinite" path="{path}"/>')
        a(f'<animate attributeName="opacity" values="0;1;1;0" dur="{r["pulse"]}s" repeatCount="indefinite"/></circle>')
        a("</g>")

    # Bloch sphere: outline, equator and meridians turning (rx follows |cos|).
    a(f'<g fill="none" stroke="{c["accent"]}">')
    a(f'<circle cx="{CX}" cy="{CY}" r="{R}" stroke-width="1.4" opacity=".9"/>')
    a(f'<ellipse cx="{CX}" cy="{CY}" rx="{R}" ry="{R * 0.24:.1f}" stroke-width="1.1" opacity=".75"/>')
    a(f'<ellipse cx="{CX}" cy="{CY - R * 0.5:.1f}" rx="{R * 0.866:.1f}" ry="{R * 0.2:.1f}" stroke-width=".8" opacity=".35"/>')
    a(f'<ellipse cx="{CX}" cy="{CY + R * 0.5:.1f}" rx="{R * 0.866:.1f}" ry="{R * 0.2:.1f}" stroke-width=".8" opacity=".35"/>')
    for k in range(3):
        off = k * math.pi / 3
        vals = series(lambda u: abs(math.cos(2 * math.pi * u + off)) * R)
        a(f'<ellipse cx="{CX}" cy="{CY}" ry="{R}" stroke-width=".9" opacity=".55"><animate attributeName="rx" dur="14s" repeatCount="indefinite" values="{vals}"/></ellipse>')
    a("</g>")
    a(f'<line x1="{CX}" y1="{CY - R - 16}" x2="{CX}" y2="{CY + R + 16}" stroke="{c["muted"]}" stroke-width="1" stroke-dasharray="3 4"/>')
    mono = 'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="13"'
    a(f'<text x="{CX}" y="{CY - R - 22}" text-anchor="middle" {mono} fill="{c["muted"]}">|0⟩</text>')
    a(f'<text x="{CX}" y="{CY + R + 34}" text-anchor="middle" {mono} fill="{c["muted"]}">|1⟩</text>')

    # State vector |ψ⟩ precessing around the vertical axis.
    th = math.radians(38)
    def tip(u):
        ph = 2 * math.pi * u
        return CX + R * math.sin(th) * math.cos(ph), CY - R * math.cos(th) + R * math.sin(th) * math.sin(ph) * 0.24
    xs = series(lambda u: tip(u)[0])
    ys = series(lambda u: tip(u)[1])
    a(f'<line x1="{CX}" y1="{CY}" stroke="{c["accent"]}" stroke-width="2.4" stroke-linecap="round">')
    a(f'<animate attributeName="x2" dur="7s" repeatCount="indefinite" values="{xs}"/><animate attributeName="y2" dur="7s" repeatCount="indefinite" values="{ys}"/></line>')
    a(f'<circle r="6" fill="{c["accent"]}"><animate attributeName="cx" dur="7s" repeatCount="indefinite" values="{xs}"/><animate attributeName="cy" dur="7s" repeatCount="indefinite" values="{ys}"/></circle>')
    a(f'<circle r="13" fill="{c["accent"]}" opacity=".18"><animate attributeName="cx" dur="7s" repeatCount="indefinite" values="{xs}"/><animate attributeName="cy" dur="7s" repeatCount="indefinite" values="{ys}"/></circle>')
    a(f'<text {mono} fill="{c["accent"]}"><animate attributeName="x" dur="7s" repeatCount="indefinite" values="{series(lambda u: tip(u)[0] + 12)}"/><animate attributeName="y" dur="7s" repeatCount="indefinite" values="{series(lambda u: tip(u)[1] - 10)}"/>|ψ⟩</text>')
    a(f'<circle cx="{CX}" cy="{CY}" r="11" fill="url(#core)"/>')

    # Dust: a few motes that come and go.
    import random
    rnd = random.Random(7)
    for _ in range(26):
        x, y = rnd.uniform(40, W - 40), rnd.uniform(40, H - 40)
        if abs(x - CX) < 100 and abs(y - CY) < 100:
            continue
        col = c["civil"] if rnd.random() < 0.4 else c["accent"]
        d = rnd.uniform(3, 7)
        a(f'<circle cx="{f(x)}" cy="{f(y)}" r="{rnd.uniform(0.8, 1.8):.1f}" fill="{col}" opacity="0"><animate attributeName="opacity" values="0;.7;0" dur="{d:.1f}s" begin="{rnd.uniform(0, 6):.1f}s" repeatCount="indefinite"/></circle>')
    a("</svg>")
    return "\n".join(out)

for t in THEMES:
    with open(os.path.join(OUT, f"header-{t}.svg"), "w", encoding="utf8") as fh:
        fh.write(build(t))
    print(t, os.path.getsize(os.path.join(OUT, f"header-{t}.svg")), "bytes")
