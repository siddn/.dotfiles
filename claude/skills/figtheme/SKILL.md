---
name: figtheme
description: Convert a vector figure (PDF or SVG, e.g. matplotlib/MATLAB plots for papers) from light mode to dark mode by remapping its colors, with contrast and distinctness checks and a visual review loop. Use whenever the user asks for a dark version, dark mode, dark background, or "recolor for slides/posters" of a figure, or asks to check whether a figure's colors stay readable on a dark background. Do not use for resizing to IEEE column widths, for raster images (PNG/JPG), or for regenerating a figure from plotting code (re-render with a dark style instead).
---

# figtheme: dark-mode recoloring of vector figures

The script `scripts/figtheme.py` measures and applies. You decide. A color map (`map.json`) sits between the two: you edit it, the script checks it and applies it.

Never modify the user's original file. Work in a scratch folder, and ask before writing anything into a OneDrive or Dropbox folder, because those sync.

## Setup

- Use the Conda env `figtheme` (`~/miniforge3/envs/figtheme`). It has Python 3.12, numpy, pillow, pymupdf.
- If it does not exist, ask before creating it: `conda env create -f <skill>/environment.yml`. Never install into `base`.
- Run the script as `<env>/bin/python <skill>/scripts/figtheme.py <command> ...`.

## Workflow

1. **Pick a starting map.** List `palettes/`. Each file is a map the user approved earlier, named for the palette it holds. If one matches the figure's colors, reuse it. Otherwise seed from scratch. Tell the user which you chose and why.
2. **Inspect.** `inspect FIG --out WORK [--map palettes/NAME.json] [--bg "#1e1e1e"]` converts the PDF to `source.svg`, renders `original.png`, writes `colors.json` (every color with its roles and opacities) and `map.json`. With `--map`, it reuses entries whose hex matches, seeds only the new colors, and prints what it reused, what is new, and where role overrides need a second look. The background comes from the reused map unless you pass `--bg`. Read `colors.json` and look at `original.png` before touching the map. Know which color is the background, text, axes, data series, and decoration.
3. **Round.** `round WORK --note "what changed"` runs `check`, applies the map, saves `history/NNN/` and appends to `log.jsonl`.
4. **Look at `themed.png`.** Always view the image. The numeric checks miss real problems, such as a band that is too bright or faint traces that vanish. This is the main reason to iterate.
5. **Edit `map.json`, repeat.** Stop when `check` passes and the image looks right. Plan for up to 5 rounds without the user, then stop and show the result either way. Stop early if a round changes nothing.
6. **Deliver.** `apply WORK --pdf` writes `themed.pdf`. Open `compare.png` and `themed.pdf` for the user (`open`). Report the final map, what each round changed, and judgment calls the user should review. Then ask whether to save the map as a new palette: `cp WORK/map.json palettes/<name>.json`. Name it for the colors it holds (for example `blue-teal-green`), not for the figure.

## Map format

```json
"#000000": {"to": "#e8e8e8",
            "roles": {"fill": {"to": "#ffffff", "opacity": 0.08},
                      "stroke": {"to": "#c8c8c8"}}}
```

A color often has several jobs (text, a translucent fill, a thin line). Use `roles` to give each job its own target. `opacity` replaces fill/stroke opacity for that role. See `palettes/opt-progression_blue-teal-green.json` for a finished map.

## Reusing maps

A map is keyed by the original hex colors, so it carries over to any figure with the same palette. Two cautions:
- A color can have different jobs in different figures. In the first figure, `#000000` was a translucent band fill, a thin line, and title text. Another figure may use it for only one of these jobs. Role overrides from the old figure may not fit the new one. `inspect --map` prints these under "verify roles". Look at the image to confirm.
- Colors that are not in the map stay unchanged. `check` reports them as issues. Seed or edit them before delivery.

## Judgment rules (and why)

- **Neutrals** (text, axes, grid): flip lightness, but stay soft. Off-white (about `#d4d4d4` to `#e8e8e8`) on a near-black background (`#1e1e1e`). Pure white on pure black glares and looks harsh in slides.
- **Data colors**: keep the hue and change lightness only. Legends, captions and the user's text refer to colors by name. Hue shift is flagged above 15 degrees.
- **Distinctness**: new data colors must stay at least as easy to tell apart as the originals (CIEDE2000 at least 15, and at least 0.9 times the original distance). If a pair fails, grid-search small Lab changes around the color. Do not move hue far.
- **Contrast** (checked on the opacity-blended color): text 4.5:1, lines and markers 3:1, faint layers at least 1.8:1 (raw traces drawn at 20-40% opacity must stay visible), translucent decorative fills at least 1.15:1.
- **Translucent black fills** (shaded bands at 20% black) become nearly invisible on dark. Map them to white at a low opacity (5-10%).
- **Colors that carry meaning** (heatmaps, diverging scales, red/green status): do not remap without asking. A simple lift can reverse or blur the meaning. Flag them instead.

## Known limits

- Seeding assumes a light source figure and a dark target. For other directions, edit the map by hand.
- Raster images inside a figure are not recolored. `inspect` and `apply` warn about them.
- Gradients: stop colors are listed with role `gradient-stop` and are remapped, but this path is untested.
- Shapes with no `fill` attribute are black by SVG rules. `inspect` writes these out explicitly. Without that step they would stay black on a dark page.
- PDF to SVG to PDF can substitute fonts (the test figure came out as Nimbus Sans). Text stays selectable. Check that font changes are acceptable if the journal cares.
- The page background is only added if no rectangle covers the full page.
- Style attributes (`style="fill:..."`) are not parsed. PyMuPDF output uses plain attributes.
- If the figure came from matplotlib or MATLAB code, re-rendering with a dark style gives better results than recoloring. Say so to the user when the source is available.
