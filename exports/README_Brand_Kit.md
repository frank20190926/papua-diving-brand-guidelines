# Papua Diving Resorts / 2026 Brand Kit

## Contents
- Papua_Diving_Resorts_Brand_Guidelines_2026.pdf: 19-page A4 printable reference book, embedded fonts and vector graphics.
- Papua_Diving_Resorts_2026_Master_Palette.ase: nine current colours in sRGB and supplied-CMYK groups (18 swatches).
- Colour_Specifications.json: authoritative numeric HEX, RGB and supplied CMYK targets, including Sorido Teal.
- Three SVG motifs: scalable, transparent backgrounds, no embedded raster images or text objects.
- Three PNG motifs: 4800 x 640, 4800 x 520 and 1200 x 1200 pixels, RGBA, 300 ppi metadata.
- papua_logo_cropped.png: original 373 x 357 supplied raster, unchanged (including its opaque white field).
- fonts/: Tenor Sans Regular; Source Sans 3 Regular, Medium, SemiBold; OFL licences.
- SHA256SUMS.txt: file integrity list.

## Use
Master logo clear space is at least one bird height on every side. Minimum widths: 32 mm print / 120 px digital.
On dark photography or dark brown, use the Natural Linen #F6F1EB rounded holding shape with the full clear space inside.
Do not recolour, stretch, reverse, trace, rebuild or remove the background from the supplied master.
SVG borders repeat horizontally at native aspect ratio. Keep all motifs outside logo clear space.
Motifs are new bark-inspired geometric designs, not culturally authenticated traditional artwork. Obtain local Papuan review before commercial production.

## Typography
Tenor Sans Regular headings: uppercase, +0.08em tracking.
Source Sans 3 SemiBold subheads; Medium navigation; Regular body.
Body: 10.5pt / 15.5pt print; 16px / 1.65 web. Karla is replaced in new work.
Fonts are from the Google Fonts official repository; Source Sans static weights were instantiated from its variable font.

## Print notes
The reference book is A4, 210 x 297 mm, with live embedded type and vector motifs. It has no bleed and is not PDF/X.
Colour fills in the reference PDF use sRGB. The exact supplied CMYK targets are printed in the manual and in JSON; they are not ICC-converted equivalents.
The ASE replaces the earlier exploratory blue/mist swatches with the specified Lagoon Reef Teal. Its RGB and CMYK groups follow Colour_Specifications.json exactly. The original ASE is backed up in tmp/pdfs in the working project.
Approve an output-profile/stock-specific physical colour proof. Use an approved vector logo for large-format production.
At 32 mm the original logo is approximately 296 ppi. Enlarged explanatory specimens and source PDF photography are limited by supplied pixel dimensions; no artificial detail was added.
The employer-supplied photography is used for reference layouts; confirm original high-resolution files and usage rights for commercial campaigns.

## Rebuild
At project root: `python3 build_guidelines_2801171.py`.
Uses existing PyMuPDF and Pillow. assets/fonts must contain the supplied local fonts.
Four 1600 x 1200 HTML boards and boards-codex.css are generated alongside the script. Boards use local assets and include working PDF/ZIP links.
