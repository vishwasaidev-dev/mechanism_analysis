# Text-to-CAD Mechanism Animation Workflow

This document records the workflow used for the Four-Bar CAD Pilot in InnovationLab, including the original repository references and the split between CAD generation, web viewing, and browser-side animation.

## Original repository references

Primary toolkit:

- GitHub: <https://github.com/earthtojake/text-to-cad>
- Toolkit description: CAD, robotics, and hardware-design agent skills for source-controlled CAD generation.
- License: MIT.
- Toolkit commit used locally during the first pilot: `0470134a44a456c1c63e582a385509cec889a30b`.

Important upstream pieces:

- CAD skill: <https://github.com/earthtojake/text-to-cad/blob/main/skills/cad/SKILL.md>
- Render skill / CAD Explorer: <https://github.com/earthtojake/text-to-cad/blob/main/skills/render/SKILL.md>
- Harness instructions: <https://github.com/earthtojake/text-to-cad/blob/main/harness/AGENTS.md>
- Main README: <https://github.com/earthtojake/text-to-cad/blob/main/README.md>

The toolkit is STEP-first: edit Python/build123d source, regenerate explicit CAD outputs, inspect the geometry, then render or publish browser-friendly artifacts.

## Local project layout

InnovationLab demo location:

```text
demos/four_bar_cad/
  index.html                         # GitHub Pages demo: GLB viewer + 2D/3D animation
  src/four_bar_linkage.py             # Python/build123d CAD source
  assets/four_bar_linkage_pose_45deg.step
  assets/four_bar_linkage_pose_45deg.glb
  assets/four_bar_linkage_pose_45deg.stl
  assets/ground_link.step
  assets/input_crank.step
  assets/coupler_link.step
  assets/output_rocker.step
  docs/four-bar-brief.md
  docs/inspect-four-bar.txt
```

The local working pilot was first created at:

```text
projects/mechanism-innovation/pilot-four-bar/
```

The original `text-to-cad` repo was cloned beside it at:

```text
projects/mechanism-innovation/text-to-cad/
```

## Dependency setup

From the local pilot directory:

```bash
python3 -m virtualenv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/pip install -r ../text-to-cad/skills/cad/requirements.txt
```

The upstream CAD skill requirements were:

```text
build123d
ezdxf
numpy
trimesh
vtk
```

For the CAD Explorer / render viewer:

```bash
npm --prefix ../text-to-cad/skills/render/scripts/viewer install
```

Optional headless PNG snapshots require Playwright browsers and system libraries. On the WSL image used for this pilot, Playwright Chromium was missing `libnspr4`, so browser snapshot export was left as a later environment fix. CAD Explorer itself served correctly.

## CAD generation steps

### 1. Write source-first CAD

The CAD source is:

```text
demos/four_bar_cad/src/four_bar_linkage.py
```

It defines mechanism parameters such as:

```python
GROUND_SPAN = 90.0
CRANK_LENGTH = 28.0
COUPLER_LENGTH = 80.0
ROCKER_LENGTH = 55.0
LINK_WIDTH = 12.0
LINK_THICKNESS = 6.0
PIVOT_HOLE_DIAMETER = 4.5
CRANK_ANGLE_DEG = 45.0
```

It also exposes a `gen_step()` function so the upstream `scripts/step` launcher can generate the STEP artifact from source.

### 2. Generate STEP / STL / GLB

From the local pilot directory:

```bash
./.venv/bin/python ../text-to-cad/skills/cad/scripts/step \
  src/four_bar_linkage.py=STEP/four_bar_linkage_pose_45deg.step \
  --stl STL/four_bar_linkage_pose_45deg.stl \
  --glb GLB/four_bar_linkage_pose_45deg.glb
```

Notes:

- STEP is the primary CAD artifact.
- GLB is used for browser viewing.
- STL is available for mesh workflows.
- The toolkit also creates a hidden CAD Explorer GLB/topology sidecar next to the STEP file.

### 3. Inspect generated CAD

```bash
./.venv/bin/python ../text-to-cad/skills/cad/scripts/inspect refs \
  STEP/four_bar_linkage_pose_45deg.step \
  --facts --planes --positioning \
  > docs/inspect-four-bar.txt
```

This verifies that the generated CAD can be loaded and summarized geometrically. The first pilot inspection succeeded and reported four leaf occurrences for the assembly-like compound.

### 4. Open CAD Explorer locally

```bash
npm --prefix ../text-to-cad/skills/render/scripts/viewer run dev:ensure -- \
  --workspace-root "$PWD" \
  --root-dir . \
  --file STEP/four_bar_linkage_pose_45deg.step
```

The verified local viewer URL during setup was:

```text
http://127.0.0.1:4178/?file=STEP/four_bar_linkage_pose_45deg.step
```

## Publishing to GitHub Pages

Generated files were copied into the InnovationLab repository under:

```text
demos/four_bar_cad/assets/
```

The demo page is:

```text
demos/four_bar_cad/index.html
```

GitHub Pages URL:

- <https://vishwasaidev-dev.github.io/innovationlab/demos/four_bar_cad/>

Cache-busted links can use commit query strings, for example:

```text
https://vishwasaidev-dev.github.io/innovationlab/demos/four_bar_cad/?v=60a35da
```

## Web viewing strategy

GitHub does not provide a rich native STEP viewer on Pages. The practical browser strategy is:

1. Keep STEP available for real CAD exchange.
2. Export GLB for web viewing.
3. Use `<model-viewer>` for the static CAD model.
4. Add custom browser-side kinematics for interactive animation.

The top 3D CAD viewer uses:

```html
<script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
<model-viewer src="./assets/four_bar_linkage_pose_45deg.glb" camera-controls auto-rotate></model-viewer>
```

This shows the STEP-derived GLB as a static 45-degree reference pose.

## Animation strategy

There are three possible animation levels.

### Level 1 — 2D kinematic sketch

This is currently implemented.

Where:

```text
demos/four_bar_cad/index.html
```

How it works:

- A JavaScript four-bar solver computes joints A/B/C/D from the crank angle.
- SVG lines draw the ground, crank, coupler, and rocker.
- A slider and play button update the crank angle.
- A trace path shows the coupler joint trajectory.

This is fast, simple, and ideal for mechanism exploration.

### Level 2 — live 3D kinematic animation

This is currently implemented.

Where:

```text
demos/four_bar_cad/index.html
```

How it works:

- Three.js creates simple 3D bars, bosses, and pivot pins.
- The same JavaScript solver drives the 3D part transforms.
- The existing crank-angle slider/play button updates both the 2D SVG and Three.js scene.
- Pivot pins were adjusted to match visual link/crank thickness so they do not protrude awkwardly across the whole stack.

Important distinction:

- The live 3D animation is browser-side parametric geometry.
- It is not yet deforming or reassembling the STEP-derived GLB.

This gives us a useful interactive 3D mechanism without needing to regenerate CAD on every frame.

### Level 3 — CAD pose sweep / generated GLB animation

This is the next possible upgrade.

Approach:

1. Modify `four_bar_linkage.py` to accept a crank-angle parameter.
2. Generate many poses, for example every 5 or 10 degrees.
3. Export each pose as GLB.
4. In the browser, either:
   - scrub between GLB pose files, or
   - merge poses into a proper animated glTF/GLB timeline.

Pros:

- Animation is closer to the actual CAD geometry.
- Good for demonstrations where precise CAD shape matters.

Cons:

- More files.
- More generation time.
- Browser interpolation between rigid assemblies needs careful handling.

### Level 4 — assembly-aware CAD animation

A more advanced future path is to generate assembly components once, load the actual link meshes, and animate each mesh rigidly in Three.js using the four-bar solver.

This is probably the best long-term approach:

- Source CAD remains authoritative.
- Link meshes look like the real generated CAD.
- Browser animation stays lightweight because only transforms change.
- It avoids hundreds of pose files.

Likely implementation:

1. Export each link as a separate GLB or extract named meshes from one GLB.
2. Load them with Three.js `GLTFLoader`.
3. Set each link's local origin/pivot convention.
4. Apply transforms from the four-bar solver.
5. Keep STEP files available for CAD exchange.

## Where to change parameters

### For real CAD output

Edit:

```text
demos/four_bar_cad/src/four_bar_linkage.py
```

Then regenerate STEP/GLB/STL with the upstream CAD skill scripts.

### For browser-only animation

Edit:

```text
demos/four_bar_cad/index.html
```

Look for:

```js
const params = { ground: 90, crank: 28, coupler: 80, rocker: 55 };
```

For now, keep browser parameters synchronized manually with the Python CAD constants.

A future improvement is to move shared parameters into a JSON file, for example:

```text
demos/four_bar_cad/four_bar_params.json
```

Then both Python generation and browser animation can read the same source of truth.

## GitHub commits from the pilot

Key InnovationLab commits:

- `3d79764` — Add four-bar CAD pilot demo.
- `3e37009` — Add four-bar parameter animation.
- `59efde0` — Center four-bar animation viewport.
- `c4d0e45` — Add live 3D four-bar animation.
- `60a35da` — Match 3D pivot pins to link thickness.

## Recommended next steps

1. Move four-bar dimensions into a shared JSON parameter file.
2. Add UI controls for link lengths, not just crank angle.
3. Regenerate CAD from shared parameters.
4. Export individual link GLBs and animate the actual CAD meshes in Three.js.
5. Add additional mechanisms: Geneva drive, cam follower, quick-return, toggle clamp, gripper linkage.
