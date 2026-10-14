#!/usr/bin/env python
"""Recolor a vector figure (PDF or SVG) for dark/light mode.

Never modifies the input. All outputs go to --out.

Commands
  inspect FIG --out DIR [--bg HEX] [--map PRIOR.json] [--text-as-path] [--force]
      PDF->SVG, list every (color, role, opacity), render original.png,
      write colors.json and a draft map.json. With --map, reuse matching
      entries from a prior/saved map and seed only the new colors.
  check  DIR   Score map.json -> report.json (contrast, distinctness, hue shift).
  apply  DIR   Recolor source.svg -> themed.svg/png/compare.png [--pdf].
  round  DIR   check + apply + snapshot to history/NNN/ + append log.jsonl.

map.json: colors[hex] = {"to": hex, "roles": {role: {"to": hex, "opacity": 0-1}}}
  Roles: text, fill, stroke, gradient-stop. A role entry overrides "to" for
  that role only. "opacity" replaces fill-/stroke-opacity for that role.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HEX = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b")
RGB = re.compile(r"rgb\(\s*(\d+(?:\.\d+)?)(%?)\s*,\s*(\d+(?:\.\d+)?)%?\s*,\s*(\d+(?:\.\d+)?)%?\s*\)")
COLOR_ATTRS = ("fill", "stroke", "stop-color", "color")
NAMED = {"white": "#ffffff", "black": "#000000"}


# ---------- color math ----------
def norm_hex(c: str) -> str:
    c = c.strip().lower()
    c = NAMED.get(c, c)
    if len(c) == 4:
        c = "#" + "".join(ch * 2 for ch in c[1:])
    return c


def to_rgb(c: str) -> np.ndarray:
    c = norm_hex(c)
    return np.array([int(c[i:i + 2], 16) for i in (1, 3, 5)], float) / 255


def lin(rgb: np.ndarray) -> np.ndarray:
    return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)


def luminance(c: str) -> float:
    return float(lin(to_rgb(c)) @ np.array([0.2126, 0.7152, 0.0722]))


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def to_lab(c: str) -> np.ndarray:
    m = np.array([[0.4124564, 0.3575761, 0.1804375],
                  [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]])
    xyz = m @ lin(to_rgb(c)) / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def de2000(c1: str, c2: str) -> float:
    L1, a1, b1 = to_lab(c1)
    L2, a2, b2 = to_lab(c2)
    C1, C2 = np.hypot(a1, b1), np.hypot(a2, b2)
    G = 0.5 * (1 - np.sqrt(((C1 + C2) / 2) ** 7 / (((C1 + C2) / 2) ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = np.hypot(a1p, b1), np.hypot(a2p, b2)
    h1 = np.degrees(np.arctan2(b1, a1p)) % 360
    h2 = np.degrees(np.arctan2(b2, a2p)) % 360
    dL, dC = L2 - L1, C2 - C1p
    dh = h2 - h1
    dh = dh - 360 if dh > 180 else dh + 360 if dh < -180 else dh
    if C1p * C2p == 0:
        dh = 0
    dH = 2 * np.sqrt(C1p * C2p) * np.sin(np.radians(dh / 2))
    Lb, Cb = (L1 + L2) / 2, (C1p + C2p) / 2
    hb = (h1 + h2) / 2 if abs(h1 - h2) <= 180 else (h1 + h2 + 360) / 2
    if C1p * C2p == 0:
        hb = h1 + h2
    T = (1 - 0.17 * np.cos(np.radians(hb - 30)) + 0.24 * np.cos(np.radians(2 * hb))
         + 0.32 * np.cos(np.radians(3 * hb + 6)) - 0.20 * np.cos(np.radians(4 * hb - 63)))
    Sl = 1 + 0.015 * (Lb - 50) ** 2 / np.sqrt(20 + (Lb - 50) ** 2)
    Sc, Sh = 1 + 0.045 * Cb, 1 + 0.015 * Cb * T
    Rc = 2 * np.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7))
    Rt = -np.sin(np.radians(60 * np.exp(-(((hb - 275) / 25) ** 2)))) * Rc
    return float(np.sqrt((dL / Sl) ** 2 + (dC / Sc) ** 2 + (dH / Sh) ** 2 + Rt * (dC / Sc) * (dH / Sh)))


def hue(c: str) -> float:
    _, a, b = to_lab(c)
    return float(np.degrees(np.arctan2(b, a)) % 360)


def chroma(c: str) -> float:
    _, a, b = to_lab(c)
    return float(np.hypot(a, b))


def hue_diff(a: str, b: str) -> float:
    d = abs(hue(a) - hue(b)) % 360
    return min(d, 360 - d)


# ---------- extra color math ----------
def lab_to_hex(L: float, a: float, b: float) -> str:
    fy = (L + 16) / 116
    f = np.array([fy + a / 500, fy, fy - b / 200])
    xyz = np.where(f ** 3 > 216 / 24389, f ** 3, (116 * f - 16) / (24389 / 27)) * np.array([0.95047, 1.0, 1.08883])
    m = np.linalg.inv(np.array([[0.4124564, 0.3575761, 0.1804375],
                                [0.2126729, 0.7151522, 0.0721750],
                                [0.0193339, 0.1191920, 0.9503041]]))
    l = np.clip(m @ xyz, 0, 1)
    s = np.where(l <= 0.0031308, 12.92 * l, 1.055 * l ** (1 / 2.4) - 0.055)
    return "#" + "".join(f"{int(round(v * 255)):02x}" for v in np.clip(s, 0, 1))


def blend(fg: str, bg: str, alpha: float) -> str:
    c = to_rgb(fg) * alpha + to_rgb(bg) * (1 - alpha)
    return "#" + "".join(f"{int(round(v * 255)):02x}" for v in c)


def lift_to_contrast(c: str, bg: str, target: float) -> str:
    """Raise Lab lightness (keep a,b) until contrast vs bg >= target."""
    L, a, b = to_lab(c)
    for _ in range(100):
        h = lab_to_hex(L, a, b)
        if contrast(h, bg) >= target or L >= 98:
            return h
        L += 1.0
    return h


# ---------- file handling ----------
def pdf_to_svg(pdf: Path, out_svg: Path, text_as_path: bool) -> None:
    import fitz  # PyMuPDF
    doc = fitz.open(pdf)
    out_svg.write_text(doc[0].get_svg_image(text_as_path=text_as_path), encoding="utf-8")


def render_png(svg: Path, png: Path, scale: float = 2.0) -> None:
    import fitz
    doc = fitz.open(svg)
    doc[0].get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False).save(png)


def side_by_side(a: Path, b: Path, out: Path) -> None:
    from PIL import Image
    ia, ib = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    im = Image.new("RGB", (ia.width + ib.width + 10, max(ia.height, ib.height)), "#808080")
    im.paste(ia, (0, 0)); im.paste(ib, (ia.width + 10, 0))
    im.save(out)


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _ET():
    import xml.etree.ElementTree as ET
    for pfx, uri in (("", "http://www.w3.org/2000/svg"), ("xlink", "http://www.w3.org/1999/xlink"),
                     ("inkscape", "http://www.inkscape.org/namespaces/inkscape")):
        ET.register_namespace(pfx, uri)
    return ET


SHAPES = ("path", "rect", "circle", "ellipse", "polygon", "polyline", "text")
ROLE_ATTR = {"fill": "fill", "stroke": "stroke", "stop-color": "gradient-stop"}


def parse_color(v: str | None) -> str | None:
    if not v:
        return None
    v = v.strip().lower()
    if v in NAMED:
        return NAMED[v]
    return norm_hex(v) if HEX.fullmatch(v) else None


def make_fills_explicit(svg_text: str) -> str:
    """Shapes with no fill attribute are black. Write that out so the map can see it."""
    ET = _ET()
    root = ET.fromstring(svg_text)

    def walk(el, inherited):
        has = inherited or el.get("fill") is not None or "fill:" in (el.get("style") or "")
        if local(el.tag) in SHAPES and not has:
            el.set("fill", "#000000")
        for ch in el:
            if local(ch.tag) not in ("defs", "clipPath", "mask"):
                walk(ch, has)

    walk(root, False)
    return ET.tostring(root, encoding="unicode")


def iter_colors(root):
    """Yield (element, attr, role, hex, opacity) for every colored attribute."""
    def walk(el, in_text, op_in):
        tag = local(el.tag)
        in_text = in_text or tag == "text"
        op_self = float(el.get("opacity", 1)) * op_in
        for attr, base in ROLE_ATTR.items():
            c = parse_color(el.get(attr))
            if c:
                role = "text" if (in_text and attr == "fill") else base
                op = op_self * float(el.get(attr + "-opacity", 1)) if attr != "stop-color" else op_self
                yield el, attr, role, c, round(op, 3)
        for ch in el:
            yield from walk(ch, in_text, op_self)
    yield from walk(root, False, 1.0)


def scan(svg_text: str):
    root = _ET().fromstring(svg_text)
    info: dict = defaultdict(lambda: {"count": 0, "roles": {}})
    flags = {"images": 0, "gradients": 0, "has_background_rect": False}
    vb = root.get("viewBox", "").split()
    for el in root.iter():
        t = local(el.tag)
        flags["images"] += t == "image"
        flags["gradients"] += t in ("linearGradient", "radialGradient")
    for el, attr, role, c, op in iter_colors(root):
        d = info[c]; d["count"] += 1
        r = d["roles"].setdefault(role, {"count": 0, "opacities": []})
        r["count"] += 1
        if op not in r["opacities"]:
            r["opacities"].append(op)
    # background = white-ish fill on a shape at least 95% of the viewBox width
    for el in root.iter():
        if local(el.tag) in ("path", "rect") and parse_color(el.get("fill")) and len(vb) == 4:
            m = re.match(r"M0 0H([\d.]+)V([\d.]+)", el.get("d", ""))
            if (m and float(m.group(1)) * 0.75 >= 0.95 * float(vb[2]) and float(el.get("fill-opacity", 1)) == 1) or \
               (local(el.tag) == "rect" and el.get("width", "").rstrip("pt%") and float(el.get("width").rstrip("pt%")) >= 0.95 * float(vb[2])):
                flags["has_background_rect"] = True
    colors = dict(sorted(info.items(), key=lambda kv: -kv[1]["count"]))
    return colors, flags


def resolve(m: dict, c: str, role: str) -> tuple[str, float | None]:
    e = m["colors"].get(c)
    if not e:
        return c, None
    r = e.get("roles", {}).get(role, {})
    return norm_hex(r.get("to", e["to"])), r.get("opacity")


def recolor(svg_text: str, m: dict):
    ET = _ET()
    root = ET.fromstring(svg_text)
    n = 0
    for el, attr, role, c, op in list(iter_colors(root)):
        to, new_op = resolve(m, c, role)
        if to != c:
            el.set(attr, to); n += 1
        if new_op is not None and attr != "stop-color":
            el.set(attr + "-opacity", f"{new_op:g}"); n += 1
    return ET.tostring(root, encoding="unicode"), n


# ---------- seeding ----------
def seed_map(colors: dict, bg_new: str, mode: str) -> dict:
    out = {}
    for c, d in colors.items():
        roles = d["roles"]
        L = to_lab(c)[0]
        if chroma(c) <= 8:                       # neutral: flip lightness, keep it a little soft
            to = lab_to_hex(min(92.0, max(8.0, 100 - L)), 0, 0)
            if "fill" in roles and "text" not in roles and "stroke" not in roles and L > 95:
                to = bg_new                      # page / plot background
        else:                                    # data color: keep hue, lift until visible
            to = lift_to_contrast(c, bg_new, 3.5)
        out[c] = {"to": to, "role": "auto-seeded", "note": ""}
    return out


# ---------- commands ----------
def reuse_map(colors: dict, prior: dict, bg_new: str, mode: str):
    """Reuse entries from a prior map where the hex matches; seed the rest."""
    seeded = seed_map({c: d for c, d in colors.items() if c not in prior["colors"]}, bg_new, mode)
    out, report = {}, {"reused": [], "new": [], "verify_roles": [], "unused_prior": []}
    for c in colors:
        if c in prior["colors"]:
            out[c] = prior["colors"][c]
            report["reused"].append(c)
            ov = prior["colors"][c].get("roles", {})
            if ov:   # role overrides were tuned for the old figure's use of this color
                report["verify_roles"].append(f"{c}: overrides for {sorted(ov)}, this figure uses {sorted(colors[c]['roles'])}")
        else:
            out[c] = seeded[c]
            report["new"].append(c)
    report["unused_prior"] = [c for c in prior["colors"] if c not in colors]
    return out, report


def cmd_inspect(a):
    src, out = Path(a.fig), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    svg = out / "source.svg"
    if src.suffix.lower() == ".pdf":
        pdf_to_svg(src, svg, a.text_as_path)
    else:
        svg.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    svg.write_text(make_fills_explicit(svg.read_text(encoding="utf-8")), encoding="utf-8")
    render_png(svg, out / "original.png")
    colors, flags = scan(svg.read_text(encoding="utf-8"))
    (out / "colors.json").write_text(json.dumps({"flags": flags, "colors": colors}, indent=2))
    mp = out / "map.json"
    if mp.exists() and not a.force:
        print("map.json exists; kept (use --force to reseed)")
    else:
        prior = json.loads(Path(a.map).read_text()) if a.map else None
        bg = a.bg or (prior["background"]["new"] if prior else "#1e1e1e")
        mode = prior.get("mode", a.mode) if prior else a.mode
        if prior:
            cmap, rep = reuse_map(colors, prior, bg, mode)
            print(f"reused {len(rep['reused'])}, new {len(rep['new'])} {rep['new']}")
            for v in rep["verify_roles"]:
                print("  verify roles:", v)
            if rep["unused_prior"]:
                print("  prior colors absent from this figure:", rep["unused_prior"])
        else:
            cmap = seed_map(colors, bg, mode)
        mp.write_text(json.dumps({"mode": mode, "background": {"original": "#ffffff", "new": bg},
                                  "colors": cmap}, indent=2))
    print(f"{len(colors)} unique colors; flags: {flags}")
    for c, d in colors.items():
        print(f"  {c}  n={d['count']:<4}", {r: (v['count'], v['opacities']) for r, v in d['roles'].items()})


def load(d: Path, name: str | None):
    return json.loads(Path(name or d / "map.json").read_text())


def cmd_check(a):
    d = Path(a.dir)
    m = load(d, a.map)
    bg = norm_hex(m["background"]["new"])
    colors = json.loads((d / "colors.json").read_text())["colors"]
    rows, issues, prim, orig = [], [], {}, {}
    for c in colors:
        if c not in m["colors"]:
            issues.append(f"{c}: not in map (stays unchanged)")
    for c, info in colors.items():
        for role, rd in info["roles"].items():
            to, new_op = resolve(m, c, role)
            ops = [new_op] if new_op is not None else rd["opacities"]
            top = max(ops)
            if to == bg:                         # background itself
                continue
            eff = blend(to, bg, top)
            cr = contrast(eff, bg)
            deco = role == "fill" and top < 0.5  # translucent band: only has to be visible
            need = 1.15 if deco else 4.5 if role == "text" else 3.0
            dh = hue_diff(c, to) if chroma(c) > 8 else 0.0
            rows.append({"from": c, "role": role, "to": to, "opacities": ops, "effective": eff,
                         "contrast": round(cr, 2), "need": need, "hue_shift": round(dh, 1)})
            if cr < need:
                issues.append(f"{c}[{role}]->{to} @{top:g}: contrast {cr:.2f} < {need}")
            low = min(ops)
            if low < top and role != "fill":     # faint layers (raw traces) must stay visible
                cl = contrast(blend(to, bg, low), bg)
                rows[-1]["contrast_faint"] = round(cl, 2)
                if cl < 1.8:
                    issues.append(f"{c}[{role}]->{to} @{low:g} (faint): contrast {cl:.2f} < 1.8")
            if dh > 15:
                issues.append(f"{c}[{role}]->{to}: hue shifted {dh:.0f} deg")
            if role == "stroke" and chroma(to) > 8:
                prim[to] = eff
                orig[to] = c
    pairs, keys = [], list(prim)
    for i, k1 in enumerate(keys):
        for k2 in keys[i + 1:]:
            de = de2000(prim[k1], prim[k2])
            d0 = de2000(orig[k1], orig[k2])
            pairs.append({"a": k1, "b": k2, "dE2000": round(de, 1), "dE2000_original": round(d0, 1)})
            if de < 15:
                issues.append(f"{k1} vs {k2}: dE2000 {de:.1f} < 15")
            elif de < 0.9 * d0:
                issues.append(f"{k1} vs {k2}: dE2000 {de:.1f} is below original {d0:.1f}")
    rep = {"background": bg, "rows": rows, "pairs": pairs, "issues": issues, "pass": not issues}
    (d / "report.json").write_text(json.dumps(rep, indent=2))
    print(f"{len(rows)} (color,role) rows; {len(issues)} issue(s)")
    for r in rows:
        print(f"  {r['from']} {r['role']:<6} -> {r['to']} op={r['opacities']} contrast={r['contrast']} (need {r['need']})"
              + (f" faint={r['contrast_faint']}" if "contrast_faint" in r else ""))
    for p in pairs:
        print(f"  pair {p['a']} / {p['b']}: dE2000={p['dE2000']} (original {p['dE2000_original']})")
    for i in issues:
        print("  ISSUE:", i)
    return rep


def cmd_apply(a):
    d = Path(a.dir)
    m = load(d, a.map)
    text = (d / "source.svg").read_text(encoding="utf-8")
    out, n = recolor(text, m)
    flags = json.loads((d / "colors.json").read_text())["flags"]
    bg = norm_hex(m["background"]["new"])
    if not flags["has_background_rect"]:
        vb = re.search(r'viewBox="([^"]+)"', out)
        x, y, w, h = vb.group(1).split() if vb else ("0", "0", "100%", "100%")
        out = re.sub(r"(<svg[^>]*>)", lambda mm: mm.group(1) + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}"/>',
                     out, count=1)
        print("no page background found: added one")
    (d / "themed.svg").write_text(out, encoding="utf-8")
    render_png(d / "themed.svg", d / "themed.png")
    side_by_side(d / "original.png", d / "themed.png", d / "compare.png")
    if a.pdf:
        import fitz
        fitz.open("pdf", fitz.open(d / "themed.svg").convert_to_pdf()).save(d / "themed.pdf")
    print(f"wrote themed.svg, themed.png, compare.png; {n} attribute edits")
    if flags["images"]:
        print(f"WARNING: {flags['images']} raster image(s) not recolored")


def cmd_round(a):
    import shutil, time
    d = Path(a.dir)
    rep = cmd_check(a)
    cmd_apply(a)
    h = d / "history"; h.mkdir(exist_ok=True)
    k = len(list(h.glob("[0-9]*"))) + 1
    r = h / f"{k:03d}"; r.mkdir()
    for f in ("map.json", "report.json", "themed.png"):
        shutil.copy(d / f, r / f)
    with open(d / "log.jsonl", "a") as fh:
        fh.write(json.dumps({"round": k, "time": time.strftime("%H:%M:%S"), "pass": rep["pass"],
                             "issues": rep["issues"], "note": a.note}) + "\n")
    print(f"snapshot -> {r}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("inspect"); s.add_argument("fig"); s.add_argument("--out", required=True)
    s.add_argument("--text-as-path", action="store_true"); s.add_argument("--mode", default="dark")
    s.add_argument("--bg", default=None); s.add_argument("--force", action="store_true")
    s.add_argument("--map", help="prior or saved palette map to reuse")
    s.set_defaults(f=cmd_inspect)
    for name, fn in (("check", cmd_check), ("apply", cmd_apply), ("round", cmd_round)):
        s = sp.add_parser(name); s.add_argument("dir"); s.add_argument("--map"); s.add_argument("--pdf", action="store_true")
        s.add_argument("--note", default=""); s.set_defaults(f=fn)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    sys.exit(main())
