# InnovationLab

Experimental lab for mining classic mechanism references and turning them into interactive, generative mechanism concepts.


## Demos

- `index.html` — landing page linking the demos.
- `demos/mechanism_lab/index.html` — original polished 2D mechanism studio.
- `demos/mechanism_contact_preview/index.html` — contact/boundary-focused mechanism preview for cam follower and indexing concepts.
- `demos/mechanism_rapier_physics/index.html` — Rapier 2D/WASM physics prototype with rigid-body contacts for cam follower and indexing experiments.
- `demos/four_bar_cad/index.html` — source-controlled CAD pilot with Python/build123d, STEP/STL/GLB outputs, and a web model viewer.
- `demos/mechanisms_3d/index.html` — browser-side 3D studio converting the latest 2D mechanism presets into animated Three.js solids.
- `demos/planetary_gear/index.html` — browser-side planetary gear preset with sun/planet/ring/carrier animation and ratio controls.
- `demos/slider_crank/index.html` — rotary-to-linear slider-crank preset with geometry controls and readouts.
- `demos/geneva_drive/index.html` — enhanced 3D Geneva indexing preset with generated solid wheel slots, driver pin, lock plate, orbit camera, and dwell/indexing readouts.
- `demos/cam_follower/index.html` — cam follower preset with multiple lift profiles.
- `demos/contact_boundary_lab/index.html` — first geometric contact-boundary prototype: nearest point, normal, clearance/penetration, and simple response.
- `demos/simple_pin_slot/index.html` — minimal constraint-first pin-slot mechanism: crank pin, vertical slot, horizontal prismatic slider, clearance validation, and 3D solids.
- `demos/pin_slot_yoke/index.html` — boundary-driven pin-in-slot/yoke prototype with a crank pin driving a constrained one-DOF slot body.
- `docs/text-to-cad-animation-workflow.md` — documented workflow for CAD generation, GLB publishing, and 2D/3D browser animation.

## Current prototype

- `demos/mechanism_lab/index.html` — interactive variable-dwell indexing yoke concept.
- `tools/mechanism_lab_extract.py` — builds contact sheets from scanned mechanism PDFs for rapid visual browsing.
- `demos/four_bar_cad/src/four_bar_linkage.py` — first text-to-CAD mechanism pilot.

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
