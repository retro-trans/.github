"""Rewrite the system chips row in profile/banner.svg.

Edit SYSTEMS and run: python scripts/banner_chips.py
"""
import re
from pathlib import Path

SYSTEMS = ["PS1", "PS2", "PS3", "PSP", "VITA", "DREAMCAST", "GAMECUBE", "PC"]

BANNER = Path(__file__).resolve().parent.parent / "profile" / "banner.svg"
WIDTH, Y, GAP, BG = 1280, 286, 14, "#0e0b1c"


def chip(x, label):
    w = len(label) * 13 + 36
    corners = "".join(
        f'<rect x="{cx}" y="{cy}" width="4" height="4" fill="{BG}"/>'
        for cy in (0, 30)
        for cx in (0, w - 4)
    )
    return w, (
        f'<g transform="translate({x} {Y})">'
        f'<rect width="{w}" height="34" fill="#1b1533" stroke="#3a2f63" stroke-width="2"/>'
        f'{corners}<text x="{w / 2}" y="23" text-anchor="middle">{label}</text></g>'
    )


def main():
    total = sum(len(s) * 13 + 36 for s in SYSTEMS) + GAP * (len(SYSTEMS) - 1)
    x, parts = (WIDTH - total) // 2, []
    for label in SYSTEMS:
        w, svg = chip(x, label)
        parts.append(svg)
        x += w + GAP
    text = BANNER.read_text(encoding="utf-8")
    new, n = re.subn(r'<g class="chips">.*?</g></g>', f'<g class="chips">{"".join(parts)}</g>', text, flags=re.S)
    assert n == 1, "chips group not found"
    with BANNER.open("w", encoding="utf-8", newline="\n") as f:
        f.write(new)
    print(f"{len(SYSTEMS)} chips written")


if __name__ == "__main__":
    main()
