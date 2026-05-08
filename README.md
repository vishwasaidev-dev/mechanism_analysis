# InnovationLab

Experimental lab for mining classic mechanism references and turning them into interactive, generative mechanism concepts.

## Current prototype

- `demos/mechanism_lab/index.html` — interactive variable-dwell indexing yoke concept.
- `tools/mechanism_lab_extract.py` — builds contact sheets from scanned mechanism PDFs for rapid visual browsing.

## Local use

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pymupdf pillow
python tools/mechanism_lab_extract.py "../sources/Artobolevsky - Mechanisms in modern engineering design Vol 1.pdf" --start 1 --stop 200 --step 8
```

Open `demos/mechanism_lab/index.html` in a browser to view the first animation.

## Notes

Large source PDFs are intentionally not committed. Keep them in a local `sources/` folder or external storage.
