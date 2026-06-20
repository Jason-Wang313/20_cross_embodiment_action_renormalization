# Paper20 VLA Highlight Hardening Plan

Date: 2026-06-20

## Objective

Make `C:/Users/wangz/Downloads/20.pdf` explicitly match the visible VLA-v4
role model's boxed-link behavior while preserving the final 26-page
cross-embodiment action-renormalization paper:

- citation links use green one-point boxes;
- internal figure/table/section links use red one-point boxes;
- URL links use green one-point boxes;
- the final PDF is rebuilt, copied to Downloads, visually checked, and leaves
  no local `paper/main.pdf`.

## Plan-Start Evidence

Baseline artifact:

- Canonical PDF: `C:/Users/wangz/Downloads/20.pdf`
- Pages: 26
- Size: 409,298 bytes
- SHA256: `E23D1C3D300FF6010FBE0F3574AC84ACA0E4FD5F2488048D6C57D79C2B9369E0`
- Local `paper/main.pdf`: absent
- Repository state: clean against `origin/master`

Baseline link inventory from the current Downloads PDF:

- Link pages: `[(1, 16), (2, 25), (3, 13), (16, 1), (17, 5)]`
- Annotation colors: green = 54, red = 6, cyan = 0
- Border widths: `(0, 0, 1)` for all 60 link annotations

Source finding:

- `paper/main.tex` is the active manuscript source.
- The preamble loads plain `\usepackage{hyperref}` but does not explicitly
  lock `citebordercolor`, `linkbordercolor`, `urlbordercolor`, or
  `pdfborder`.
- The current PDF already has green citation/URL boxes and red internal boxes,
  but the target is to make that behavior explicit and reproducible.
- The repository build script `scripts/build_paper.ps1` runs `pdflatex`,
  `bibtex`, and repeated `pdflatex` from `paper/`; it does not copy to
  Downloads or remove `paper/main.pdf`, so final export/removal must be done
  manually after a successful build.

## Role-Model Target

Install the same explicit hyperref policy as the visible VLA-v4 role model:

```tex
\usepackage{hyperref}
\hypersetup{
  colorlinks=false,
  pdfborder={0 0 1},
  citebordercolor={0 1 0},
  linkbordercolor={1 0 0},
  urlbordercolor={0 1 0}
}
```

## Execution Plan

1. Add the VLA `\hypersetup` block immediately after `\usepackage{hyperref}`
   in `paper/main.tex`.
2. Rebuild with `scripts/build_paper.ps1`.
3. If the log asks for another pass for cross-references, run the final
   canonical pass before recording metadata.
4. Copy the rebuilt `paper/main.pdf` to `C:/Users/wangz/Downloads/20.pdf`.
5. Remove local `paper/main.pdf` after export.
6. Recompute page count, byte size, SHA256, annotation colors, border widths,
   and link pages from the final Downloads PDF.
7. Render every page that contains link annotations into
   `tmp/pdfs/paper20_after`.
8. Visually inspect rendered affected pages:
   - green citation and URL boxes are crisp and aligned;
   - red internal-reference boxes are crisp and aligned;
   - no cyan boxes appear;
   - layout, figures, tables, headers, and page count remain stable.
9. Update README/status/audit/version/validation metadata with the new hash and
   VLA-style boxed-link inventory.
10. Validate build logs, JSON metadata, diff hygiene, final PDF hash, and
    absence of local `paper/main.pdf`.
11. Remove Paper20 temp renders, leaving only the shared role-model render
    directory.
12. Stage only Paper20 source and metadata files, commit, push, and verify a
    clean repository before moving to Paper19.

## Non-Goals

- Do not alter experiment results, claims, figures, tables, bibliography
  content, or page count.
- Do not add or remove citations, references, or URLs merely to change link
  counts.
- Do not leave intermediate PDFs or render folders behind.

## Completion Evidence

Final artifact after hardening:

- Canonical PDF: `C:/Users/wangz/Downloads/20.pdf`
- Pages: 26
- Size: 409,298 bytes
- SHA256: `106CC7757D60C2D17A1434DFE281981F745922B90855E29CE6E260FC0CF66E94`
- Local `paper/main.pdf`: absent after export

Final link inventory:

- Link pages: `[(1, 16), (2, 25), (3, 13), (16, 1), (17, 5)]`
- Annotation colors: green = 54, red = 6, cyan = 0
- Border widths: `(0, 0, 1)` for all 60 link annotations

Visual check:

- Rendered affected pages 1, 2, 3, 16, and 17 from the final Downloads PDF.
- Spot-checked pages 2 and 17 at high detail.
- Green citation and URL boxes and red internal-reference boxes are crisp and
  aligned; no cyan boxes are visible.
