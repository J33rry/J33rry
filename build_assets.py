#!/usr/bin/env python3
"""Generate animated monochrome SVG header + numbered section dividers for the J33rry profile README.

Emits light variants to assets/ and dark variants to assets/dark/, matching the
<picture> + prefers-color-scheme convention used in the README.

Two deliberate choices:
  * Digits are stroked vector paths, not text, so the thin geometric numerals render
    identically for every viewer regardless of installed fonts -- and so they can be
    drawn on with a stroke-dashoffset animation.
  * Backgrounds are transparent rather than an opaque fill, so the assets sit cleanly
    on any GitHub theme (dark, dark-dimmed, light) without a visible band.

Animation is plain CSS inside the SVG, which GitHub renders for <img>-referenced SVGs.
Every animation is disabled under prefers-reduced-motion.
"""

import os

MONO = ("ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, "
        "'Liberation Mono', monospace")

THEMES = {
    "light": {"fg": "#000000", "muted": "#57606a", "dir": "assets"},
    "dark": {"fg": "#ffffff", "muted": "#8b949e", "dir": "assets/dark"},
}

# Shapes are written with an {A} slot so the draw-on class and normalised pathLength
# can be injected uniformly. Each digit is drawn inside a 44 x 88 box, stroke-only.
DIGITS = {
    "0": '<ellipse {A} cx="22" cy="44" rx="19" ry="42"/><path {A} d="M35,15 L9,73"/>',
    "1": '<path {A} d="M8,19 L26,4 L26,86"/>',
    "2": '<path {A} d="M4,22 C4,9 15,2 24,2 C36,2 42,11 42,21 C42,35 31,45 4,86 L43,86"/>',
    "3": '<path {A} d="M5,17 C8,7 16,2 25,2 C36,2 42,9 42,19 C42,31 33,40 24,42 '
         'C35,42 43,50 43,62 C43,76 33,86 22,86 C12,86 5,80 3,71"/>',
    "4": '<path {A} d="M31,2 L3,62 L43,62"/><path {A} d="M31,2 L31,86"/>',
    "5": '<path {A} d="M39,3 L12,3 L10,36 C16,32 20,31 25,31 C37,31 44,40 44,55 '
         'C44,72 34,86 21,86 C12,86 5,80 3,72"/>',
    "6": '<circle {A} cx="23" cy="59" r="20"/>'
         '<path {A} d="M38,9 C31,2 22,1 15,6 C7,12 3,28 3,50"/>',
}

DRAW_ATTRS = 'class="dash" pathLength="1"'

# (number, label, slug)
SECTIONS = [
    ("01", "WHOAMI", "whoami"),
    ("02", "STACK", "stack"),
    ("03", "PROJECTS", "projects"),
    ("04", "TELEMETRY", "telemetry"),
    ("05", "SIGNALS", "signals"),
    ("06", "CONNECT", "connect"),
]

# Cycling focus terms in the header carousel.
ROTATE = [
    "full-stack developer",
    "typescript · react · next.js",
    "node.js · apis · realtime",
    "machine learning · python",
]

W, H = 1600, 180
NUM_X, NUM_Y = 45, 46          # top-left of the big numeral group
DIGIT_ADVANCE = 56
LABEL_X = 190
LABEL_SIZE, LABEL_TRACK = 21, 7.5
PATH_SIZE, PATH_TRACK = 17, 2.0
MARGIN_R = 1556
MID = H / 2


def mono_width(text, size, track):
    """Advance width of a monospace run (0.6em per glyph is the common mono advance)."""
    return len(text) * (0.6 * size + track)


def base_css(extra=""):
    return f'''    .mono {{ font-family: {MONO}; }}

    /* draw-on: shapes carry pathLength="1" so one dasharray fits every glyph */
    .dash {{ stroke-dasharray: 1; stroke-dashoffset: 1;
             animation: dash 1.15s cubic-bezier(.6,0,.2,1) forwards; }}
    @keyframes dash {{ to {{ stroke-dashoffset: 0; }} }}

    .f {{ opacity: 0; animation: f .8s ease forwards; }}
    @keyframes f {{ to {{ opacity: 1; }} }}

    .rise {{ opacity: 0; animation: rise .9s cubic-bezier(.2,.7,.2,1) forwards; }}
    @keyframes rise {{ from {{ opacity: 0; transform: translateY(10px); }}
                       to {{ opacity: 1; transform: translateY(0); }} }}

    .d1 {{ animation-delay: .05s }} .d2 {{ animation-delay: .22s }}
    .d3 {{ animation-delay: .45s }} .d4 {{ animation-delay: .70s }}
    .d5 {{ animation-delay: .95s }} .d6 {{ animation-delay: 1.2s }}
{extra}
    @media (prefers-reduced-motion: reduce) {{
      .dash, .f, .rise {{ animation: none; }}
      .dash {{ stroke-dashoffset: 0; }}
      .f, .rise {{ opacity: 1; transform: none; }}
    }}'''


def numerals(number, fg):
    """Big stroked numerals that draw themselves on, digit by digit."""
    groups = []
    for i, ch in enumerate(number):
        shapes = DIGITS[ch].replace("{A}", DRAW_ATTRS)
        groups.append(
            f'<g class="g{i + 1}" transform="translate('
            f'{NUM_X + i * DIGIT_ADVANCE},{NUM_Y})">{shapes}</g>'
        )
    return (
        f'<g fill="none" stroke="{fg}" stroke-width="5.5" '
        f'stroke-linecap="round" stroke-linejoin="round">{"".join(groups)}</g>'
    )


def divider(number, label, slug, theme):
    t = THEMES[theme]
    path_text = f"~/{number}-{slug}"

    label_w = mono_width(label, LABEL_SIZE, LABEL_TRACK)
    path_w = mono_width(path_text, PATH_SIZE, PATH_TRACK)

    line_start = LABEL_X + label_w + 55
    line_end = MARGIN_R - path_w - 50

    stagger = ('    .g1 .dash { animation-delay: .06s }\n'
               '    .g2 .dash { animation-delay: .24s }\n'
               '    .rule { animation-duration: 1.3s; animation-delay: .55s }\n')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" fill="none" role="img" aria-label="Section {number} — {label}">
  <style>
{base_css(stagger)}
  </style>
  {numerals(number, t['fg'])}
  <text class="mono rise d3" x="{LABEL_X}" y="{MID + 7.5:.0f}" font-size="{LABEL_SIZE}"
        letter-spacing="{LABEL_TRACK}" fill="{t['fg']}">{label}</text>
  <line class="dash rule" pathLength="1" x1="{line_start:.0f}" y1="{MID}" x2="{line_end:.0f}" y2="{MID}"
        stroke="{t['fg']}" stroke-width="1.5" opacity="0.45"/>
  <text class="mono f d5" x="{MARGIN_R}" y="{MID + 6:.0f}" text-anchor="end"
        font-size="{PATH_SIZE}" letter-spacing="{PATH_TRACK}" fill="{t['muted']}">{path_text}</text>
</svg>
'''


def header(theme):
    t = THEMES[theme]
    hw, hh = 1600, 320
    name = "ANIL KUMAR MEENA"

    cycle = len(ROTATE) * 3          # 3s per item
    step = 100.0 / len(ROTATE)       # % of the cycle each item owns
    rot_css = [
        f'    .rot {{ opacity: 0; animation: rot {cycle}s linear infinite; }}',
        f'    @keyframes rot {{ 0% {{opacity:0}} 2% {{opacity:1}} {step - 4:.0f}% {{opacity:1}} '
        f'{step:.0f}% {{opacity:0}} 100% {{opacity:0}} }}',
    ]
    for i in range(len(ROTATE)):
        rot_css.append(f'    .r{i + 1} {{ animation-delay: {i * 3 + 1.1:.1f}s }}')
    extra = "\n".join(rot_css) + "\n"

    rot_lines = "\n".join(
        f'  <text class="mono rot r{i + 1}" x="128" y="272" font-size="15"'
        f' letter-spacing="2" fill="{t["fg"]}" opacity="0.85">{txt}</text>'
        for i, txt in enumerate(ROTATE)
    )

    css = base_css(extra).replace(
        "      .dash, .f, .rise { animation: none; }",
        "      .dash, .f, .rise, .rot { animation: none; }\n"
        "      .rot { opacity: 0; } .rot.r1 { opacity: .85; }",
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {hw} {hh}" width="{hw}" height="{hh}" fill="none" role="img" aria-label="{name} — full-stack developer">
  <style>
{css}
  </style>

  <line class="dash" pathLength="1" x1="46" y1="92" x2="1554" y2="92"
        stroke="{t['fg']}" stroke-width="1" opacity="0.28"/>
  <g class="f d1">
    <text class="mono" x="46" y="72" font-size="16" letter-spacing="2.5"
          fill="{t['muted']}">~/github.com/J33rry</text>
    <text class="mono" x="1554" y="72" text-anchor="end" font-size="16"
          letter-spacing="2.5" fill="{t['muted']}">focusing</text>
  </g>

  <g class="rise d3">
    <text class="mono" x="44" y="186" font-size="72" font-weight="300"
          letter-spacing="11" fill="{t['fg']}">{name}</text>
  </g>
  <g class="f d4">
    <text class="mono" x="48" y="230" font-size="19" letter-spacing="4"
          fill="{t['muted']}">full-stack developer &#183; web &#183; machine learning</text>
  </g>

  <g class="f d5">
    <text class="mono" x="48" y="272" font-size="14" letter-spacing="1.5"
          fill="{t['muted']}">focus &#9656;</text>
  </g>
{rot_lines}

  <line class="dash rule" pathLength="1" x1="46" y1="300" x2="1554" y2="300"
        stroke="{t['fg']}" stroke-width="1.5" opacity="0.28"
        style="animation-delay:.75s;animation-duration:1.4s"/>
</svg>
'''


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    for theme, t in THEMES.items():
        out_dir = os.path.join(root, t["dir"])
        os.makedirs(out_dir, exist_ok=True)

        with open(os.path.join(out_dir, "header.svg"), "w") as f:
            f.write(header(theme))

        for number, label, slug in SECTIONS:
            with open(os.path.join(out_dir, f"s{number}.svg"), "w") as f:
                f.write(divider(number, label, slug, theme))

    total = 2 * (1 + len(SECTIONS))
    print(f"wrote {total} animated svg files -> assets/ and assets/dark/")


if __name__ == "__main__":
    main()
