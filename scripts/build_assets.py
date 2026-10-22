"""Builds the animated profile SVGs in assets/. Run: python scripts/build_assets.py
Outputs self-contained, responsive animated SVGs for Gaurav Patil's GitHub profile.
"""
import base64
import datetime
import io
import json
from pathlib import Path
import re
import urllib.request
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
OUT.mkdir(exist_ok=True)
PORTRAIT = ROOT / "scripts" / "gaurav.png"

# Color tokens: Obsidian Dark + Electric Cyan accent
BG, BG2, BORDER, FG, FG2, ACC = (
    "#050505",
    "#0A0A0A",
    "#27272a",
    "#ffffff",
    "#b4b4bd",
    "#00F2FE",
)
UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0 Safari/537.36"
    )
}


def get(url):
  return urllib.request.urlopen(urllib.request.Request(url, headers=UA)).read()


def font_b64(family, weight):
  css = get(
      f"https://fonts.googleapis.com/css2?family={family}:wght@{weight}&display=swap"
  ).decode()
  url = re.findall(r"url\((https://[^)]+\.woff2)\)", css)[-1]
  return base64.b64encode(get(url)).decode()


print("Fetching web fonts (Outfit, JetBrains Mono)...")
FONTS = {
    "Outfit": [(900, font_b64("Outfit", 900)), (600, font_b64("Outfit", 600))],
    "JetBrains Mono": [(500, font_b64("JetBrains+Mono", 500))],
}


def font_css(prefix):
  out = []
  for fam, ws in FONTS.items():
    for w, b in ws:
      out.append(
          f"@font-face{{font-family:'{prefix}-{fam}';font-weight:{w};"
          f"src:url(data:font/woff2;base64,{b}) format('woff2');}}"
      )
  return "".join(out)


def portrait(size):
  im = (
      Image.open(PORTRAIT)
      .convert("RGBA")
      .resize((size, size), Image.Resampling.LANCZOS)
  )
  buf = io.BytesIO()
  im.save(buf, "PNG", optimize=True)
  return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


SI_VER = "13.21.0"


def icon(slug):
  svg = get(
      f"https://cdn.jsdelivr.net/npm/simple-icons@{SI_VER}/icons/{slug}.svg"
  ).decode()
  return re.search(r' d="([^"]+)"', svg).group(1)


def svg(name, w, h, css, body, prefix):
  base = f"""
  .{prefix} .d{{font-family:'{prefix}-Outfit',sans-serif;font-weight:900}}
  .{prefix} .s{{font-family:'{prefix}-Outfit',sans-serif;font-weight:600}}
  .{prefix} .m{{font-family:'{prefix}-JetBrains Mono',monospace;font-weight:500}}
  @media (prefers-reduced-motion: reduce){{.{prefix} *{{animation:none!important}}}}"""
  doc = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" class="{prefix}" role="img" aria-label="{name}">
<style>{font_css(prefix)}{base}{css}</style>
<defs>
  <pattern id="{prefix}-dots" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{FG}" opacity=".07"/></pattern>
  <linearGradient id="{prefix}-hair" x1="0" x2="1"><stop offset="0" stop-color="{FG}" stop-opacity="0"/><stop offset=".5" stop-color="{FG}" stop-opacity=".35"/><stop offset="1" stop-color="{FG}" stop-opacity="0"/></linearGradient>
  <radialGradient id="{prefix}-glow" cx=".5" cy="0" r=".9"><stop offset="0" stop-color="{ACC}" stop-opacity=".09"/><stop offset="1" stop-color="{FG}" stop-opacity="0"/></radialGradient>
</defs>
<rect width="{w}" height="{h}" rx="24" fill="{BG}"/>
<rect width="{w}" height="{h}" rx="24" fill="url(#{prefix}-dots)"/>
<rect width="{w}" height="{h}" rx="24" fill="url(#{prefix}-glow)"/>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="23.5" fill="none" stroke="{BORDER}"/>
<rect x="80" y="0" width="{w-160}" height="1" fill="url(#{prefix}-hair)"/>
{body}
</svg>"""
  (OUT / name).write_text(doc, encoding="utf-8")
  print(f"{name}: {len(doc)//1024} KB")


def esc(t):
  return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- hero
def hero():
  p = "hr"
  roles = [
      "Healthcare AI Engineer",
      "Deep Learning & Computer Vision",
      "Low-Latency Clinical RAG",
      "6× Hackathon Winner · IEEE Lead",
  ]
  role_css = "".join(
      f".{p} .r{i}{{animation:{p}role 12s {i*3}s infinite both}}"
      for i in range(4)
  )
  css = f"""
  .{p} .rise{{animation:{p}rise 1s cubic-bezier(.2,.8,.2,1) both}}
  .{p} .fade{{animation:{p}fade .9s ease-out both}}
  .{p} .pic{{animation:{p}pic 1.4s ease-out both}}
  .{p} .r1,.{p} .r2,.{p} .r3{{opacity:0}}
  {role_css}
  .{p} .blink{{animation:{p}blink 1s steps(1) infinite}}
  .{p} .pulse{{animation:{p}pulse 2s ease-in-out infinite;transform-origin:center;transform-box:fill-box}}
  @keyframes {p}rise{{from{{transform:translateY(120px)}}}}
  @keyframes {p}fade{{from{{opacity:0;transform:translateY(12px)}}}}
  @keyframes {p}pic{{from{{opacity:0;transform:scale(1.06)}}}}
  @keyframes {p}role{{0%{{opacity:0;transform:translateY(14px)}}3%,22%{{opacity:1;transform:none}}25%,100%{{opacity:0;transform:translateY(-14px)}}}}
  @keyframes {p}blink{{50%{{opacity:0}}}}
  @keyframes {p}pulse{{50%{{transform:scale(2.2);opacity:0}}}}"""
  roles_svg = "".join(
      f'<text class="s r{i}" x="64" y="330" font-size="28" fill="{FG}">{esc(r)}</text>'
      for i, r in enumerate(roles)
  )
  greet = "> hello, world. i'm"
  body = f"""
<defs>
  <linearGradient id="{p}-fadeb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}"/></linearGradient>
  <clipPath id="{p}-type"><rect x="64" y="44" height="30" width="360"><animate attributeName="width" values="0;0;360" keyTimes="0;.25;1" dur="1.6s"/></rect></clipPath>
  <clipPath id="{p}-n1"><rect x="0" y="80" width="760" height="112"/></clipPath>
  <clipPath id="{p}-n2"><rect x="0" y="182" width="760" height="112"/></clipPath>
  <clipPath id="{p}-roles"><rect x="60" y="296" width="640" height="46"/></clipPath>
  <radialGradient id="{p}-portraitglow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{ACC}" stop-opacity=".25"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>
</defs>
<circle cx="950" cy="220" r="180" fill="url(#{p}-portraitglow)"/>
<circle cx="950" cy="220" r="142" fill="none" stroke="{ACC}" stroke-width="2" stroke-dasharray="4 6" opacity=".5"/>
<image class="pic" href="{portrait(280)}" x="810" y="80" width="280" height="280"/>
<g clip-path="url(#{p}-type)"><text class="m" x="64" y="66" font-size="20" fill="{FG2}">{esc(greet)}</text></g>
<rect class="blink" x="300" y="48" width="11" height="22" fill="{ACC}"/>
<g clip-path="url(#{p}-n1)"><text class="d rise" x="58" y="182" font-size="120" letter-spacing="-5" fill="{FG}">GAURAV</text></g>
<g clip-path="url(#{p}-n2)"><text class="d rise" style="animation-delay:.15s" x="58" y="284" font-size="120" letter-spacing="-5" fill="{FG}">PATIL</text></g>
<g clip-path="url(#{p}-roles)">{roles_svg}</g>
<text class="s fade" style="animation-delay:.6s" x="64" y="372" font-size="17" fill="{FG2}">Translating biomedical imaging &amp; clinical data into real-time, explainable AI systems.</text>
<rect x="64" y="396" width="660" height="1" fill="{BORDER}"/>
<g class="fade m" style="animation-delay:.9s" font-size="14" fill="{FG2}">
  <circle class="pulse" cx="72" cy="423" r="5" fill="{ACC}"/><circle cx="72" cy="423" r="5" fill="{ACC}"/>
  <text x="86" y="428" fill="{ACC}" letter-spacing="2">OPEN TO WORK</text>
  <text x="230" y="428">Mumbai, India</text><text x="350" y="428" fill="{BORDER}">/</text>
  <text x="370" y="428">Frontend AI Intern @ CoralOS</text><text x="610" y="428" fill="{BORDER}">/</text>
  <text x="630" y="428">github.com/GauravPatil2515</text>
</g>"""
  svg("hero.svg", 1200, 460, css, body, p)


# ---------------------------------------------------------------- about
def about():
  p = "ab"
  caps = [
      (
          "01",
          "Medical Computer Vision",
          "ViT, U-Net++, Grad-CAM explainability, semantic segmentation",
      ),
      (
          "02",
          "Clinical Decision RAG",
          "ICD-10 semantic chunking &amp; 29ms vector retrieval via FAISS",
      ),
      (
          "03",
          "Agentic AI Interfaces",
          "Multi-modal routing (Fact/Nav/Decision) &amp; Memory Graphs",
      ),
      (
          "04",
          "Production ML Systems",
          "Model training, FastAPI serving, quantization, Docker containers",
      ),
  ]
  slides = [
      (
          "NOW",
          "Dec 2025 → Present",
          "CoralOS",
          "Frontend AI Intern · Remote",
          [
              "Building Aelura — decision-first AI interface with Gemini API",
              "Interactive Memory Knowledge Graph for conversation context",
              "Multi-modal structured query routing (Fact/Nav/Decision)",
          ],
      ),
      (
          "PREVIOUSLY",
          "Jun 2025 → Nov 2025",
          "Pioneer Machines",
          "AI Research Intern · Clinical AI",
          [
              "10,000+ PubMed articles indexed with automated chunking",
              "29ms query latency achieved on FAISS vector retrieval",
              "40% improvement in clinical data ingestion throughput",
          ],
      ),
      (
          "LEADERSHIP",
          "2024 → Present",
          "IEEE SIES GST",
          "Technical Head · Leadership",
          [
              "Directed Technopedia symposium for 2 years (500+ attendees)",
              "Technical Star Award recipient — Dr. K Lakshmi Sudha",
              "Mentored 100+ students on ML model design &amp; deployment",
          ],
      ),
  ]
  cap_svg = "".join(f"""<g class="fade" style="animation-delay:{.15*i:.2f}s">
  <text class="m" x="64" y="{150+i*64}" font-size="13" fill="{ACC}">{n}</text>
  <text class="s" x="104" y="{150+i*64}" font-size="22" fill="{FG}">{t}</text>
  <text class="m" x="104" y="{174+i*64}" font-size="13" fill="{FG2}">{d}</text></g>""" for i, (n, t, d) in enumerate(caps))
  sl_svg, bars = "", ""
  for i, (tag, when, org, role, pts) in enumerate(slides):
    items = "".join(
        f'<text class="m" x="680" y="{258+j*30}" font-size="15"'
        f' fill="{FG2}"><tspan fill="{ACC}">→ </tspan>{t}</text>'
        for j, t in enumerate(pts)
    )
    sl_svg += f"""<g class="sl sl{i}">
  <text class="m" x="680" y="142" font-size="12" letter-spacing="3" fill="{ACC if tag == 'NOW' else FG2}">{tag} · {when}</text>
  <text class="d" x="676" y="196" font-size="44" letter-spacing="-1.5" fill="{FG}">{org}</text>
  <text class="s" x="680" y="226" font-size="18" fill="{FG2}">{role}</text>{items}</g>"""
    x = 680 + i * 160
    bars += (
        f'<rect x="{x}" y="372" width="148" height="3" rx="1.5"'
        f' fill="{BORDER}"/><rect class="bar b{i}" x="{x}" y="372" width="148"'
        f' height="3" rx="1.5" fill="{ACC}"/>'
    )
  css = f"""
  .{p} .fade{{animation:{p}fade .8s ease-out both}}
  .{p} .sl1,.{p} .sl2{{opacity:0}}
  .{p} .sl{{animation:{p}slide 12s infinite both}}
  .{p} .sl1{{animation-delay:4s}} .{p} .sl2{{animation-delay:8s}}
  .{p} .bar{{transform-box:fill-box;transform-origin:left;animation:{p}bar 12s linear infinite both}}
  .{p} .b1{{animation-delay:4s;transform:scaleX(0)}} .{p} .b2{{animation-delay:8s;transform:scaleX(0)}}
  @keyframes {p}fade{{from{{opacity:0;transform:translateX(-12px)}}}}
  @keyframes {p}slide{{0%{{opacity:0;transform:translateY(10px)}}3%,30%{{opacity:1;transform:none}}33.3%,100%{{opacity:0;transform:translateY(-10px)}}}}
  @keyframes {p}bar{{0%{{transform:scaleX(0)}}33.3%{{transform:scaleX(1)}}33.4%,100%{{transform:scaleX(0)}}}}"""
  body = f"""
<text class="m" x="64" y="80" font-size="13" letter-spacing="3" fill="{FG2}">01 / WHAT I BUILD</text>
{cap_svg}
<rect x="624" y="40" width="536" height="360" rx="18" fill="{BG2}" stroke="{BORDER}"/>
<text class="m" x="680" y="88" font-size="13" letter-spacing="3" fill="{FG2}">02 / WHERE I'M BUILDING</text>
{sl_svg}{bars}"""
  svg("about-life.svg", 1200, 420, css, body, p)


# ---------------------------------------------------------------- stack
STACK = {
    "Deep Learning & CV": [
        "PyTorch",
        "TensorFlow",
        "Vision Transformers",
        "U-Net++",
        "Grad-CAM",
        "Detectron2",
        "OpenCV",
    ],
    "AI / LLM & RAG": [
        "LangChain",
        "FAISS",
        "Groq LPU",
        "Vertex AI",
        "Llama 3.3",
        "Semantic Search",
    ],
    "Backend & Data": [
        "FastAPI",
        "PostgreSQL",
        "SQL",
        "Docker",
        "Flask",
        "Pandas",
        "NumPy",
    ],
    "Languages & Frontend": [
        "Python",
        "C/C++",
        "JavaScript",
        "React",
        "Git",
        "Streamlit",
    ],
}
ORBITS = [
    (110, 46, -18, 14, ["python", "pytorch", "opencv"]),
    (
        200,
        84,
        12,
        22,
        ["tensorflow", "huggingface", "docker", "fastapi", "postgresql"],
    ),
    (
        262,
        116,
        -8,
        30,
        ["langchain", "googlegemini", "scikitlearn", "react", "git", "mlflow"],
    ),
]


def stack():
  p = "st"
  cx, cy = 320, 310
  orb = ""
  for k, (rx, ry, tilt, dur, slugs) in enumerate(ORBITS):
    path = (
        f"M{cx-rx},{cy} a{rx},{ry} 0 1,0 {2*rx},0 a{rx},{ry} 0 1,0 {-2*rx},0"
    )
    orb += (
        f'<g transform="rotate({tilt} {cx} {cy})"><path id="{p}-o{k}"'
        f' d="{path}" fill="none" stroke="{BORDER}" stroke-dasharray="3 6"/>'
    )
    for i, s in enumerate(slugs):
      d = icon(s)
      orb += f"""<g><animateMotion dur="{dur}s" repeatCount="indefinite" begin="-{dur*i/len(slugs):.2f}s"><mpath href="#{p}-o{k}"/></animateMotion>
  <g transform="rotate({-tilt})"><circle r="22" fill="{BG2}" stroke="{BORDER}"/><path transform="translate(-11 -11) scale(.9167)" d="{d}" fill="{FG}"/></g></g>"""
    orb += "</g>"
  chips, y = "", 98
  for group, items in STACK.items():
    chips += f'<text class="m" x="680" y="{y}" font-size="12" letter-spacing="3" fill="{ACC}">{esc(group.upper())}</text>'
    x, y = 680, y + 14
    for it in items:
      w = 18 + len(it) * 8.4
      if x + w > 1150:
        x, y = 680, y + 38
      chips += f'<rect x="{x}" y="{y}" width="{w:.0f}" height="28" rx="14" fill="{BG2}" stroke="{BORDER}"/><text class="m" x="{x+w/2:.0f}" y="{y+19}" font-size="13" text-anchor="middle" fill="{FG}">{it}</text>'
      x += w + 8
    y += 56
  css = f"""
  .{p} .core{{animation:{p}pulse 3s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
  @keyframes {p}pulse{{50%{{transform:scale(1.15);opacity:.6}}}}"""
  body = f"""
<text class="m" x="64" y="80" font-size="13" letter-spacing="3" fill="{FG2}">03 / STACK &amp; ARSENAL</text>
{orb}
<circle class="core" cx="{cx}" cy="{cy}" r="34" fill="{ACC}" opacity=".22"/>
<circle cx="{cx}" cy="{cy}" r="26" fill="{FG}"/><text class="d" x="{cx}" y="{cy+8}" font-size="22" text-anchor="middle" fill="{BG}">GP</text>
<line x1="640" y1="70" x2="640" y2="510" stroke="{BORDER}"/>
{chips}"""
  svg("stack.svg", 1200, 560, css, body, p)


# ---------------------------------------------------------------- id + dashboard
def id_dashboard(gh):
  p = "id"
  bars = "".join(
      f'<rect x="{126+i*7}" y="476" width="{(1, 3, 2, 1, 4, 2)[i % 6]}"'
      f' height="34" fill="{FG}"/>'
      for i, _ in enumerate(range(14))
  )
  metrics = [
      ("29ms", "FAISS vector retrieval latency", "Pioneer Machines · 2025"),
      ("99.1%", "DermAI diagnostic accuracy", "ViT + Grad-CAM Explainability"),
      ("83.7%", "Retinal segmentation Dice score", "U-Net++ DRIVE Dataset"),
      ("10,000+", "PubMed clinical records indexed", "Vertex AI RAG Pipeline"),
      ("6×", "Hackathon podiums &amp; wins", "GenAI Sprint #1 Solo · 2026"),
      ("100+", "Engineers &amp; students mentored", "IEEE &amp; GDG Coordinator"),
  ]
  m_svg = ""
  for i, (v, l, src) in enumerate(metrics):
    x, y = 520 + (i % 2) * 320, 120 + (i // 2) * 130
    m_svg += f"""<g class="fade" style="animation-delay:{.8+i*.12:.2f}s">
  <rect x="{x}" y="{y}" width="296" height="110" rx="16" fill="{BG2}" stroke="{BORDER}"/>
  <text class="d" x="{x+24}" y="{y+52}" font-size="36" letter-spacing="-1" fill="{FG}">{v}</text>
  <text class="s" x="{x+24}" y="{y+78}" font-size="14" fill="{FG2}">{l}</text>
  <text class="m" x="{x+24}" y="{y+98}" font-size="11" fill="{ACC}">{src}</text></g>"""
  css = f"""
  .{p} .swing{{transform-origin:240px 0;animation:{p}drop 2.6s cubic-bezier(.3,.7,.3,1) both,{p}swing 5s 2.6s ease-in-out infinite}}
  .{p} .fade{{animation:{p}fade .7s ease-out both}}
  .{p} .foil{{animation:{p}foil 5s 1.5s ease-in-out infinite}}
  @keyframes {p}drop{{0%{{transform:translateY(-560px) rotate(0)}}35%{{transform:translateY(0) rotate(9deg)}}55%{{transform:rotate(-6deg)}}72%{{transform:rotate(3.5deg)}}86%{{transform:rotate(-2.4deg)}}100%{{transform:rotate(1.7deg)}}}}
  @keyframes {p}swing{{0%,100%{{transform:rotate(1.7deg)}}50%{{transform:rotate(-1.7deg)}}}}
  @keyframes {p}fade{{from{{opacity:0;transform:translateY(10px)}}}}
  @keyframes {p}foil{{0%{{transform:translateX(-300px)}}40%,100%{{transform:translateX(420px)}}}}"""
  body = f"""
<defs>
  <clipPath id="{p}-card"><rect x="100" y="150" width="280" height="384" rx="20"/></clipPath>
  <linearGradient id="{p}-sheen" x1="0" x2="1"><stop offset="0" stop-color="{FG}" stop-opacity="0"/><stop offset=".5" stop-color="{FG}" stop-opacity=".14"/><stop offset="1" stop-color="{FG}" stop-opacity="0"/></linearGradient>
  <linearGradient id="{p}-metal" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#e4e4e7"/><stop offset="1" stop-color="#71717a"/></linearGradient>
</defs>
<g class="swing">
  <path d="M212 0 L228 118 M268 0 L252 118" stroke="{FG}" stroke-width="16" opacity=".9"/>
  <path d="M212 0 L228 118 M268 0 L252 118" stroke="{BG}" stroke-width="16" stroke-dasharray="2 10" opacity=".5"/>
  <rect x="216" y="112" width="48" height="22" rx="6" fill="url(#{p}-metal)"/>
  <rect x="232" y="130" width="16" height="26" rx="4" fill="none" stroke="url(#{p}-metal)" stroke-width="4"/>
  <rect x="100" y="150" width="280" height="384" rx="20" fill="{BG2}" stroke="{BORDER}"/>
  <g clip-path="url(#{p}-card)">
    <rect x="100" y="150" width="280" height="384" fill="url(#{p}-dots)"/>
    <rect x="216" y="164" width="48" height="8" rx="4" fill="{BG}" stroke="{BORDER}"/>
    <image href="{portrait(200)}" x="140" y="184" width="200" height="200"/>
    <rect x="100" y="320" width="280" height="90" fill="url(#{p}-fadec)"/>
    <text class="d" x="126" y="420" font-size="28" letter-spacing="-1" fill="{FG}">GAURAV PATIL</text>
    <text class="m" x="126" y="444" font-size="11" fill="{FG2}">HEALTHCARE AI SPECIALIST</text>
    <circle cx="131" cy="461" r="4" fill="{ACC}"/><text class="m" x="142" y="465" font-size="11" fill="{ACC}">ACCESS: OPEN TO WORK</text>
    {bars}
    <text class="m" x="330" y="510" font-size="10" text-anchor="end" fill="{FG2}">@GauravPatil2515</text>
    <rect class="foil" x="100" y="150" width="140" height="384" fill="url(#{p}-sheen)" transform="skewX(-12)"/>
  </g>
  <defs><linearGradient id="{p}-fadec" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG2}" stop-opacity="0"/><stop offset=".7" stop-color="{BG2}"/></linearGradient></defs>
</g>
<text class="m" x="520" y="80" font-size="13" letter-spacing="3" fill="{FG2}">04 / ID &amp; DASHBOARD</text>
{m_svg}"""
  svg("id-dashboard.svg", 1200, 560, css, body, p)


# ---------------------------------------------------------------- achievements
GOLD = "#fbbf24"
TROPHY = "M7 3h10v5a5 5 0 0 1-10 0zM7 5H3v1a4 4 0 0 0 4 4M17 5h4v1a4 4 0 0 1-4 4M12 13v4M8 21h8l-1-4H9z"


def achievements():
  p = "ac"
  stats = [
      ("6×", "hackathon wins"),
      ("8.57", "CGPA @ SIES GST"),
      ("100+", "mentored engineers"),
      ("29ms", "FAISS query latency"),
      ("99.1%", "DermAI ViT accuracy"),
  ]
  tiles = ""
  for i, (v, l) in enumerate(stats):
    x = 64 + i * 218
    tiles += f"""<g class="up" style="animation-delay:{.1+i*.1:.1f}s">
  <rect x="{x}" y="108" width="202" height="122" rx="16" fill="{BG2}" stroke="{BORDER}"/>
  <text class="d" x="{x+22}" y="170" font-size="44" letter-spacing="-1.5" fill="{FG}">{v}</text>
  <text class="m" x="{x+22}" y="204" font-size="12" fill="{FG2}">{esc(l)}</text></g>"""
  wall = [
      (
          "Bounty Hunters GenAI Sprint",
          GOLD,
          "Rank #1 Solo Winner (National GenAI Challenge 2026)",
      ),
      (
          "Code 4 Compassion",
          GOLD,
          "Winner – Healthcare &amp; Clinical AI Track",
      ),
      (
          "BNB Chain Bombay Hackathon",
          GOLD,
          "2nd Place – Web3 × AI Infrastructure",
      ),
      (
          "OxygenIgnite @ NIT Goa",
          GOLD,
          "3rd Place – National AI Innovation Track",
      ),
      (
          "Deep Blue Season 11",
          GOLD,
          "Finalist – Mastek Enterprise AI Competition",
      ),
  ]
  rows = ""
  for i, (t, c, d) in enumerate(wall):
    y = 286 + i * 44
    rows += f"""<g class="side" style="animation-delay:{.6+i*.1:.2f}s">
  <circle cx="{622}" cy="{y}" r="15" fill="none" stroke="{c}" stroke-opacity=".45"/>
  <path transform="translate(614 {y-8}) scale(.7)" d="{TROPHY}" fill="none" stroke="{c}" stroke-width="2" stroke-linejoin="round"/>
  <text class="s" x="{650}" y="{y-2}" font-size="16" fill="{FG}">{t}</text>
  <text class="m" x="{650}" y="{y+16}" font-size="11" fill="{FG2}">{d}</text>
</g>"""
  chips_l = [
      "B.E. AI &amp; DS · SIES GST",
      "IEEE Technical Head",
      "GDG ML/DS Coordinator",
      "Technical Star Award",
      "ISL CV Workshop Lead",
      "Bounty Hunters #1 Solo",
  ]
  chips, x, y = "", 440, 524
  for i, c in enumerate(chips_l):
    w = 22 + len(c) * 7.8
    if x + w > 1136:
      x, y = 440, y + 40
    chips += f'<g class="up" style="animation-delay:{1.1+i*.08:.2f}s"><rect x="{x}" y="{y}" width="{w:.0f}" height="30" rx="15" fill="{BG2}" stroke="{BORDER}"/><text class="m" x="{x+w/2:.0f}" y="{y+20}" font-size="12" text-anchor="middle" fill="{FG}">{esc(c)}</text></g>'
    x += w + 8
  css = f"""
  .{p} .up{{animation:{p}up .7s ease-out both}}
  .{p} .side{{animation:{p}side .7s ease-out both}}
  .{p} .sweep{{animation:{p}sweep 4s 1s ease-in-out infinite}}
  .{p} .pulse{{animation:{p}pulse 2s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
  .{p} .float{{animation:{p}float 4s ease-in-out infinite}}
  @keyframes {p}up{{from{{opacity:0;transform:translateY(14px)}}}}
  @keyframes {p}side{{from{{opacity:0;transform:translateX(14px)}}}}
  @keyframes {p}sweep{{0%{{transform:translateX(-260px)}}45%,100%{{transform:translateX(620px)}}}}
  @keyframes {p}pulse{{50%{{transform:scale(2.4);opacity:0}}}}
  @keyframes {p}float{{50%{{transform:translateY(-6px)}}}}"""
  body = f"""
<defs>
  <clipPath id="{p}-award"><rect x="64" y="254" width="496" height="234" rx="18"/></clipPath>
  <linearGradient id="{p}-gold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GOLD}" stop-opacity=".16"/><stop offset=".6" stop-color="{GOLD}" stop-opacity="0"/></linearGradient>
  <linearGradient id="{p}-sheen" x1="0" x2="1"><stop offset="0" stop-color="{FG}" stop-opacity="0"/><stop offset=".5" stop-color="{FG}" stop-opacity=".09"/><stop offset="1" stop-color="{FG}" stop-opacity="0"/></linearGradient>
</defs>
<text class="m" x="64" y="76" font-size="13" letter-spacing="3" fill="{FG2}">05 / ACHIEVEMENTS &amp; HONORS</text>
{tiles}
<g class="up" style="animation-delay:.5s">
  <rect x="64" y="254" width="496" height="234" rx="18" fill="{BG2}" stroke="{GOLD}" stroke-opacity=".35"/>
  <g clip-path="url(#{p}-award)">
    <rect x="64" y="254" width="496" height="234" fill="url(#{p}-gold)"/>
    <rect class="sweep" x="64" y="254" width="180" height="234" fill="url(#{p}-sheen)" transform="skewX(-14)"/>
  </g>
  <g class="float"><path transform="translate(452 286) scale(3.4)" d="{TROPHY}" fill="none" stroke="{GOLD}" stroke-width=".9" stroke-linejoin="round"/></g>
  <text class="m" x="96" y="304" font-size="12" letter-spacing="3" fill="{GOLD}">HONOR · 2024–25</text>
  <text class="d" x="94" y="364" font-size="44" letter-spacing="-1.5" fill="{FG}">Technical Star</text>
  <text class="d" x="94" y="412" font-size="44" letter-spacing="-1.5" fill="{FG}">Award</text>
  <text class="m" x="96" y="456" font-size="13" fill="{FG2}">Conferred by Dr. K Lakshmi Sudha · IEEE SIES GST</text>
</g>
<rect x="584" y="254" width="552" height="234" rx="18" fill="{BG2}" stroke="{BORDER}"/>
{rows}
<g class="up" style="animation-delay:1s">
  <rect x="64" y="512" width="352" height="96" rx="16" fill="{BG2}" stroke="{ACC}" stroke-opacity=".35"/>
  <circle class="pulse" cx="92" cy="541" r="5" fill="{ACC}"/><circle cx="92" cy="541" r="5" fill="{ACC}"/>
  <text class="m" x="106" y="545" font-size="11" letter-spacing="2.5" fill="{ACC}">CURRENTLY BUILDING</text>
  <text class="d" x="86" y="588" font-size="30" letter-spacing="-1" fill="{FG}">Aelura AI @ CoralOS</text>
  <text class="s" x="392" y="588" font-size="15" text-anchor="end" fill="{FG2}">Decision-First AI</text>
</g>
{chips}"""
  svg("achievements.svg", 1200, 640, css, body, p)


# ---------------------------------------------------------------- connect
SOCIALS = [
    ("github", "GitHub", "@GauravPatil2515"),
    ("linkedin", "LinkedIn", "in/gaurav-patil-6b1241215"),
    ("gmail", "Email", "gauravpatil2516@gmail.com"),
    ("googlegemini", "Focus Area", "Healthcare AI & Vision"),
]


def connect():
  p = "cn"
  cards = ""
  for i, (slug, name, handle) in enumerate(SOCIALS):
    x, y = 470 + (i % 2) * 350, 90 + (i // 2) * 110
    d = icon(slug)
    cards += f"""<g class="fade" style="animation-delay:{.2+i*.1:.1f}s">
  <rect x="{x}" y="{y}" width="330" height="84" rx="16" fill="{BG2}" stroke="{BORDER}"/>
  <circle cx="{x+42}" cy="{y+42}" r="22" fill="{BG}" stroke="{BORDER}"/><path transform="translate({x+31} {y+31}) scale(.9167)" d="{d}" fill="{FG}" fill-rule="evenodd"/>
  <text class="s" x="{x+78}" y="{y+38}" font-size="18" fill="{FG}">{name}</text>
  <text class="m" x="{x+78}" y="{y+62}" font-size="12" fill="{FG2}">{handle}</text>
  <text class="m nudge" x="{x+300}" y="{y+48}" font-size="18" text-anchor="end" fill="{ACC}" style="animation-delay:{i*.2:.1f}s">→</text></g>"""
  css = f"""
  .{p} .fade{{animation:{p}fade .7s ease-out both}}
  .{p} .nudge{{animation:{p}nudge 1.6s ease-in-out infinite}}
  .{p} .rise{{animation:{p}rise 1s cubic-bezier(.2,.8,.2,1) both}}
  @keyframes {p}fade{{from{{opacity:0;transform:translateX(16px)}}}}
  @keyframes {p}nudge{{50%{{transform:translateX(6px)}}}}
  @keyframes {p}rise{{from{{transform:translateY(90px)}}}}"""
  body = f"""
<defs>
  <linearGradient id="{p}-fadeb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}"/></linearGradient>
  <clipPath id="{p}-t"><rect x="0" y="270" width="460" height="90"/></clipPath>
</defs>
<image href="{portrait(260)}" x="80" y="30" width="260" height="260"/>
<g clip-path="url(#{p}-t)"><text class="d rise" x="56" y="340" font-size="64" letter-spacing="-3" fill="{FG}">LET'S BUILD.</text></g>
<text class="m" x="470" y="56" font-size="13" letter-spacing="3" fill="{FG2}">06 / INITIATE CONTACT</text>
{cards}"""
  svg("connect.svg", 1200, 380, css, body, p)


if __name__ == "__main__":
  u = json.loads(get("https://api.github.com/users/GauravPatil2515"))
  gh = {
      "public_repos": u["public_repos"],
      "followers": u["followers"],
      "date": datetime.date.today().strftime("%b %Y"),
  }
  print("Building SVGs for Gaurav Patil...")
  hero()
  about()
  stack()
  id_dashboard(gh)
  achievements()
  connect()
  print("All 6 Bento SVGs generated successfully in assets/!")
