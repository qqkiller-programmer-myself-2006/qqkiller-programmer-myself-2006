from __future__ import annotations

from pathlib import Path
from typing import Iterable
import base64

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
SOURCE = ASSETS / "avatar.png"

WIDTH, HEIGHT = 1180, 610


def subject_mask(image: Image.Image) -> np.ndarray:
    """Keep the illustrated subject while suppressing the uniform navy backdrop."""
    arr = np.asarray(image.convert("RGB"), dtype=np.int16)
    h, w, _ = arr.shape
    corner = np.concatenate(
        [
            arr[:100, :100].reshape(-1, 3),
            arr[:100, -100:].reshape(-1, 3),
            arr[-100:, :100].reshape(-1, 3),
            arr[-100:, -100:].reshape(-1, 3),
        ],
        axis=0,
    )
    background = np.median(corner, axis=0)
    distance = np.sqrt(np.sum((arr - background) ** 2, axis=2))
    # Retain hair, clothing, skin, and rim-light while removing the flat background.
    mask = distance > 20
    return mask.astype(np.uint8) * 255


def make_dither(output: Path, colour: tuple[int, int, int]) -> None:
    source = Image.open(SOURCE).convert("RGB")
    width, height = source.size
    crop_width = min(width, int(height * 0.80))
    left = (width - crop_width) // 2
    top = int(height * 0.04)
    bottom = min(height, top + int(crop_width * 1.20))
    source = source.crop((left, top, left + crop_width, bottom))

    mask = subject_mask(source)
    gray = ImageOps.autocontrast(source.convert("L"), cutoff=1)
    gray = ImageEnhance.Contrast(gray).enhance(1.30)
    gray = gray.filter(ImageFilter.UnsharpMask(radius=3, percent=140, threshold=2))
    gray = gray.resize((150, 178), Image.Resampling.LANCZOS)
    mask_image = Image.fromarray(mask).resize((150, 178), Image.Resampling.LANCZOS)

    luminance = np.asarray(gray, dtype=np.float32)
    subject = np.asarray(mask_image, dtype=np.float32) / 255.0
    # Floyd-Steinberg-like density levels through luminance; low values remain visible as sparse dots.
    alpha = np.clip((luminance - 12) * 1.18, 0, 255) * subject
    alpha = np.where(alpha >= 34, alpha, 0).astype(np.uint8)

    rgba = np.zeros((178, 150, 4), dtype=np.uint8)
    rgba[..., 0] = colour[0]
    rgba[..., 1] = colour[1]
    rgba[..., 2] = colour[2]
    rgba[..., 3] = alpha
    rendered = Image.fromarray(rgba, "RGBA").resize((300, 356), Image.Resampling.NEAREST)
    rendered.save(output, optimize=True)


def rows(
    items: Iterable[tuple[str, str]],
    x: int,
    y: int,
    label_colour: str,
    value_colour: str,
    value_x: int,
    spacing: int = 40,
) -> str:
    markup: list[str] = []
    for index, (label, value) in enumerate(items):
        yy = y + index * spacing
        markup.append(
            f'''<text x="{x}" y="{yy}" class="label" fill="{label_colour}">{label}</text>
            <line x1="{x + 148}" y1="{yy - 6}" x2="{value_x - 250}" y2="{yy - 6}" class="leader" />
            <text x="{value_x}" y="{yy}" class="value" text-anchor="end" textLength="{min(280, max(72, int(len(value) * 9.2)))}" lengthAdjust="spacingAndGlyphs" fill="{value_colour}">{value}</text>'''
        )
    return "\n".join(markup)


def build_banner(theme: str) -> str:
    is_dark = theme == "dark"
    colours = {
        "bg": "#071426" if is_dark else "#F4F8FC",
        "surface": "#0A1A2F" if is_dark else "#FFFFFF",
        "surface_alt": "#10243B" if is_dark else "#EAF2F8",
        "edge": "#1C4060" if is_dark else "#BCD5E6",
        "cyan": "#22D3EE" if is_dark else "#0E7490",
        "blue": "#3B82F6" if is_dark else "#2563EB",
        "green": "#10B981" if is_dark else "#059669",
        "text": "#E5F1FA" if is_dark else "#102A43",
        "muted": "#8FA9BC" if is_dark else "#486581",
        "red": "#FB7185" if is_dark else "#DC2626",
        "shadow": "#020817" if is_dark else "#B9C7D5",
    }
    avatar_file = ASSETS / ("avatar-dither-dark.png" if is_dark else "avatar-dither-light.png")
    avatar = "data:image/png;base64," + base64.b64encode(avatar_file.read_bytes()).decode("ascii")
    left_items = [
        ("NAME", "IQ · THIRAPHAT"),
        ("ROLE", "Full-Stack Developer"),
        ("LOCATION", "Loei, Thailand"),
        ("EDUCATION", "CS Year 3 · Loei Rajabhat"),
    ]
    right_items = [
        ("FOCUS", "Web · Backend · API · Mobile"),
        ("FRONTEND", "React · Next.js · Tailwind"),
        ("BACKEND", "Node.js · Express.js · Python"),
        ("DATA", "MySQL · PHP"),
    ]
    identity_rows = rows(left_items, 500, 165, colours["cyan"], colours["text"], 1082)
    stack_rows = rows(right_items, 500, 377, colours["green"], colours["text"], 1082)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1180" height="610" viewBox="0 0 1180 610" role="img" aria-labelledby="title desc">
  <title id="title">IQ — Full-Stack Developer profile banner</title>
  <desc id="desc">A terminal-style developer profile banner with a dithered avatar and system information.</desc>
  <defs>
    <linearGradient id="edgeGlow" x1="0" x2="1"><stop stop-color="{colours['cyan']}"/><stop offset=".55" stop-color="{colours['blue']}"/><stop offset="1" stop-color="{colours['green']}"/></linearGradient>
    <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="8" stdDeviation="11" flood-color="{colours['shadow']}" flood-opacity=".35"/></filter>
    <clipPath id="avatarClip"><rect x="55" y="114" width="366" height="424" rx="10"/></clipPath>
    <pattern id="microGrid" width="18" height="18" patternUnits="userSpaceOnUse"><path d="M18 0H0V18" fill="none" stroke="{colours['edge']}" stroke-opacity=".25" stroke-width="1"/></pattern>
    <style>
      .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; }}
      .label {{ font: 700 15px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; letter-spacing: .55px; }}
      .value {{ font: 600 15px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
      .leader {{ stroke: {colours['muted']}; stroke-opacity: .48; stroke-dasharray: 2 5; }}
      .cursor {{ animation: blink 1.2s steps(2, jump-none) infinite; }}
      @keyframes blink {{ 50% {{ opacity: 0; }} }}
    </style>
  </defs>
  <rect width="1180" height="610" rx="18" fill="{colours['bg']}"/>
  <rect x="18" y="18" width="1144" height="574" rx="14" fill="{colours['surface']}" filter="url(#softShadow)"/>
  <rect x="18.5" y="18.5" width="1143" height="573" rx="14" fill="none" stroke="url(#edgeGlow)" stroke-opacity=".82"/>
  <rect x="19" y="19" width="1142" height="52" rx="14" fill="{colours['surface_alt']}"/>
  <path d="M19 70.5H1161" stroke="{colours['edge']}"/>
  <circle cx="47" cy="45" r="7" fill="#FB7185"/><circle cx="72" cy="45" r="7" fill="#FBBF24"/><circle cx="97" cy="45" r="7" fill="{colours['green']}"/>
  <text x="590" y="52" text-anchor="middle" class="mono" font-size="19" font-weight="700" fill="{colours['green']}">profile.sh --live<tspan class="cursor">_</tspan></text>
  <text x="1132" y="51" text-anchor="end" class="mono" font-size="11" fill="{colours['muted']}">README / MAIN</text>

  <rect x="45" y="94" width="386" height="464" rx="12" fill="{colours['surface_alt']}" stroke="{colours['edge']}"/>
  <rect x="55" y="114" width="366" height="424" rx="10" fill="url(#microGrid)"/>
  <rect x="57" y="96" width="109" height="24" rx="5" fill="{colours['surface']}" stroke="{colours['cyan']}"/>
  <text x="70" y="113" class="mono" font-size="11" font-weight="700" fill="{colours['cyan']}">VISUAL.MAP</text>
  <g clip-path="url(#avatarClip)">
    <image x="68" y="112" width="340" height="403" href="{avatar}" xlink:href="{avatar}" preserveAspectRatio="xMidYMid meet" style="image-rendering:pixelated"/>
    <path d="M55 490H421" stroke="{colours['cyan']}" stroke-opacity=".55"/>
    <line x1="82" y1="490" x2="82" y2="511" stroke="{colours['cyan']}" stroke-opacity=".55"><animate attributeName="x1" values="65;398;65" dur="6s" repeatCount="indefinite"/><animate attributeName="x2" values="65;398;65" dur="6s" repeatCount="indefinite"/></line>
  </g>
  <text x="72" y="525" class="mono" font-size="10" fill="{colours['muted']}">SIGNAL: STABLE</text>
  <rect x="358" y="510" width="46" height="5" rx="2.5" fill="{colours['green']}"/><rect x="358" y="520" width="31" height="5" rx="2.5" fill="{colours['blue']}"/>

  <rect x="461" y="94" width="674" height="464" rx="12" fill="{colours['surface_alt']}" stroke="{colours['edge']}"/>
  <rect x="475" y="96" width="111" height="24" rx="5" fill="{colours['surface']}" stroke="{colours['cyan']}"/>
  <text x="488" y="113" class="mono" font-size="11" font-weight="700" fill="{colours['cyan']}">SYSTEM.INFO</text>
  <circle cx="1069" cy="108" r="5" fill="{colours['red']}"><animate attributeName="opacity" values="1;.25;1" dur="1.5s" repeatCount="indefinite"/></circle>
  <text x="1081" y="112" class="mono" font-size="11" font-weight="700" fill="{colours['red']}">LIVE</text>
  {identity_rows}
  <path d="M500 326H1096" stroke="{colours['edge']}"/>
  {stack_rows}
  <rect x="958" y="514" width="138" height="28" rx="14" fill="{colours['bg']}" stroke="{colours['green']}" stroke-opacity=".78"/>
  <circle cx="976" cy="528" r="4" fill="{colours['green']}"/><text x="987" y="532" class="mono" font-size="11" font-weight="700" fill="{colours['green']}">BUILDING</text>
  <text x="500" y="532" class="mono" font-size="11" fill="{colours['muted']}">LOEI / THAILAND / GMT+7</text>
  <path d="M22 590H1158" stroke="url(#edgeGlow)" stroke-width="2" opacity=".75"/>
</svg>
'''


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    make_dither(ASSETS / "avatar-dither-dark.png", (34, 211, 238))
    make_dither(ASSETS / "avatar-dither-light.png", (14, 116, 144))
    (ROOT / "dark.svg").write_text(build_banner("dark"), encoding="utf-8")
    (ROOT / "light.svg").write_text(build_banner("light"), encoding="utf-8")
    print("Created dark.svg, light.svg, and theme-specific dither avatar assets.")


if __name__ == "__main__":
    main()
