# TESTING the Rush Hour Vehicle Toolkit addon

This document explains how to run the command-line test harness (`test_runner.py`)
against every supported Blender LTS release and where the results are written.

The harness is **fully self-contained**: it generates its own synthetic vehicle
geometry (body + wheels), runs the addon's operators headlessly, and verifies the
results. No external `.blend` files are required.

---

## Supported Blender LTS versions

`rhvtinfo.py` declares `SUPPORTED_BLENDER_VERSIONS = [(4, 2, 0), (4, 5, 0), (5, 2, 0)]`.
The `blender_manifest.toml` declares `blender_version_min = "4.2.0"`.

| Version | Test build | Output folder |
|---------|------------|---------------|
| 4.2.x   | 4.2.12     | `test_scenes/4.2/` |
| 4.5.x   | 4.5.1      | `test_scenes/4.5/` |
| 5.2.x   | 5.2.2      | `test_scenes/5.2/` |

---

## 1. Install the addon into Blender's user addons directory

The test runner enables the addon by name, so it must already be present in each
Blender version's user addons directory:

```
~/Library/Application Support/Blender/<major.minor>/scripts/addons/RushHourVehicleToolkit
```

Set up two variables (adjust if your paths differ):

```bash
REPO="$HOME/projects/RushHourVehicleToolkit"
BLENDER_BUILDS="$HOME/Documents/BlenderBuilds/stable"
```

Sync the local repo into that directory (repeat after any addon source change).
The exclusions keep test scaffolding out of the installed addon:

```bash
DEST="$HOME/Library/Application Support/Blender/4.5/scripts/addons/RushHourVehicleToolkit"
mkdir -p "$DEST"
rsync -a --delete \
  --exclude '.git' --exclude '.gitignore' --exclude '.gitattributes' \
  --exclude '.test_scenes' --exclude 'test_scenes' \
  --exclude 'test_runner.py' --exclude '__pycache__' \
  "$REPO/" "$DEST"
```

To install into all three supported versions at once:

```bash
base="$HOME/Library/Application Support/Blender"
for v in 4.2 4.5 5.2; do
  DEST="$base/$v/scripts/addons/RushHourVehicleToolkit"
  mkdir -p "$DEST"
  rsync -a --delete \
    --exclude '.git' --exclude '.gitignore' --exclude '.gitattributes' \
    --exclude '.test_scenes' --exclude 'test_scenes' \
    --exclude 'test_runner.py' --exclude '__pycache__' \
    "$REPO/" "$DEST"
done
```

---

## 2. Run the tests

### Important: the `--` separator

Blender forwards its **entire** command line to `sys.argv`. The test runner
extracts everything after the **last `--`**. The `--` is therefore **required**:

```
<Blender binary> -b --python test_runner.py -- <test runner options>
```

### Full pipeline against each supported version

The full pipeline runs the "Simple" panel workflow end to end:
**Prepare Scene → Add To Vehicle Collections → Export Vehicle (Simple)**.
The Simple export internally runs Prep + Rig + Export + Check.

> **Blender 4.2**
```bash
"$BLENDER_BUILDS/blender-4.2.12-macos-arm64+lts.cf1451225401/Blender/Blender.app/Contents/MacOS/Blender" \
  -b --python "$REPO/test_runner.py" -- --full-pipeline
```

> **Blender 4.5**
```bash
"$BLENDER_BUILDS/blender-4.5.1-macos-arm64+lts.b0a72b245dcf/Blender/Blender.app/Contents/MacOS/Blender" \
  -b --python "$REPO/test_runner.py" -- --full-pipeline
```

> **Blender 5.2**
```bash
"$BLENDER_BUILDS/blender-5.2.2-macos-arm64+stable.d13f752e3b9c/Blender/Blender.app/Contents/MacOS/Blender" \
  -b --python "$REPO/test_runner.py" -- --full-pipeline
```

Run all three in sequence:

```bash
SCRIPT="$REPO/test_runner.py"

"$BLENDER_BUILDS/blender-4.2.12-macos-arm64+lts.cf1451225401/Blender/Blender.app/Contents/MacOS/Blender" -b --python "$SCRIPT" -- --full-pipeline
"$BLENDER_BUILDS/blender-4.5.1-macos-arm64+lts.b0a72b245dcf/Blender/Blender.app/Contents/MacOS/Blender" -b --python "$SCRIPT" -- --full-pipeline
"$BLENDER_BUILDS/blender-5.2.2-macos-arm64+stable.d13f752e3b9c/Blender/Blender.app/Contents/MacOS/Blender" -b --python "$SCRIPT" -- --full-pipeline
```

---

## 3. Remove the addon (optional)

After testing, you can remove the addon from all Blender versions' user addon
directories. This is useful when testing a new version — the `rsync --delete`
install step already removes stale files, but this step fully cleans up the
addon directories.

```bash
base="$HOME/Library/Application Support/Blender"
for v in 4.2 4.5 5.2; do
  DEST="$base/$v/scripts/addons/RushHourVehicleToolkit"
  if [ -d "$DEST" ]; then
    rm -rf "$DEST"
    echo "Removed $DEST"
  else
    echo "Not found: $DEST"
  fi
done
```

---

## 4. Individual operator tests

Each flag runs a single operator (auto-building any prerequisite scene state) so
you can isolate a specific step. Replace `--full-pipeline` with one of these:

| Flag                 | Operator tested |
|----------------------|-----------------|
| `--test-scene-prep`  | `prepare_scene_simple` |
| `--test-collections` | `create_vehicle_collections` |
| `--test-sorting`     | `add_selected_to_vehicle_collection` |
| `--test-prep`        | `prep_vehicle_for_unreal` (also asserts a blank material slot is removed — see section 7) |
| `--test-rig`         | `rig_vehicle` |
| `--test-export`      | `export_ue_vehicle_fbx` (includes deep regression validation) |
| `--test-skeleton`    | Regression: exported skeletal FBXs contain a valid skin |
| `--test-manifest`    | Regression: export JSON manifest has predictable mesh names |
| `--test-export-validation` | Regression suite: full pipeline + skin/manifest/material checks |
| `--test-check`       | `check_vehicle` |
| `--test-center`      | `center_vehicle` |
| `--test-bounds`      | `show_object_bounds` |
| `--test-operator <bl_idname>` | any operator by id |

Example — test the rig operator on Blender 4.5:

```bash
"$BLENDER_BUILDS/blender-4.5.1-macos-arm64+lts.b0a72b245dcf/Blender/Blender.app/Contents/MacOS/Blender" \
  -b --python "$REPO/test_runner.py" -- --test-rig
```

Combine multiple tests in one invocation:

```bash
... -b --python test_runner.py -- --test-collections --test-sorting --test-prep
```

---

## 5. Options

| Option | Description |
|--------|-------------|
| `--full-pipeline` | Run the full Simple workflow (prep scene → sort → simple export), then validate the exported assets |
| `--test-export-validation` | Regression suite: full pipeline + skin/manifest/material checks (see section 7) |
| `--axle-count N` | Number of axles for the synthetic scene (default: 2) |
| `--file scene.blend` | Test an existing saved `.blend` instead of the generated one |
| `--body-meshes a,b,c` | Body mesh names to sort (only for `--file`) |
| `--wheel-meshes a,b,c` | Wheel mesh names to sort (only for `--file`) |
| `--decimate` | Enable proxy decimation during rig |
| `--decimate-ratio F` | Decimation ratio (default: 0.5) |

Non-default axle counts (e.g. `--axle-count 4`) exercise the advanced operators,
since `prepare_scene_simple` hardcodes 2 axles.

---

## 6. Where the output goes

Both the generated scene and the exported assets are written to a folder that
matches the **major.minor** version of the Blender that ran the test:

```
test_scenes/<major.minor>/
├── test_self_contained.blend        # the generated scene (saved)
└── export_test_self_contained/      # exported assets
    ├── <scene>_static.fbx           # static meshes
    ├── SK_phys_mesh-<scene>.fbx     # physical skeletal mesh
    ├── SK_proxy-<scene>.fbx         # proxy skeletal mesh
    └── export_<scene>.json          # manifest
```

For example, a run under Blender 5.2.2 writes to `test_scenes/5.2/`, and a run
under Blender 4.5.1 writes to `test_scenes/4.5/`. The export operator derives its
output directory from the saved blend file's location, so both land side by side.

---

## 7. Regression tests

The 1.6.2 release shipped with two regressions that only became apparent after
importing into Unreal:

1. **Invalid skeleton** — the exported skeletal FBX contained no skin at all
   (no `Deformer`/`Skin`/`Cluster`/`Pose` elements), so the mesh was not bound
   to the armature and Unreal rejected the skeleton.
2. **Unpredictable mesh names** — the export JSON manifest listed mesh data
   names with `.001`/`_copy` suffixes on the right-hand side of the
   `object:data` entries (e.g. `SM_wheel_0_L.001:SM_wheel_0_L.001` instead of
   `SM_wheel_0_L.001:SM_wheel_0_L`), breaking Unreal's predictable-name
   lookups.
3. **Prep crash on a blank material slot (Blender 5.2)** — the prep stage's
   `remove_blank_materials` called `material_slot_remove()` without making the
   target object active, so the operator's `poll()` failed with
   `context is incorrect`. A blank slot is produced when a mesh has a Boolean
   modifier whose cutter carries no material: applying the modifier during prep
   leaves a trailing empty slot. Cars without such a boolean never hit it, which
   is why it only surfaced on one specific vehicle.

To keep these from recurring, the harness performs deep validation of the
exported assets:

- **Skin validation** — each exported skeletal FBX is parsed with Blender's
  bundled `fbx2json` parser and must contain a real skin: at least one
  `Deformer` element, at least one skin deformer (carrying
  `Link_DeformAcuracy`), at least one weighted vertex cluster
  (`Weights` + `Indexes`), at least one `Pose`, at least one `Matrix` and at
  least one `Geometry`.
- **Manifest validation** — the right-hand side of every `object:data` entry
  in the export JSON (the mesh data name Unreal imports) must be a
  predictable name — `SM_body`, `SM_wheel_<axle>_<L|R>`, `SK_phys_mesh`,
  `SK_proxy` — with no `.NNN` or `_copy` suffixes. The left-hand side (the
  Blender object name) may legitimately differ, e.g. `SM_wheel_0_L.001`. The
  wheel `wheel_filename` entries are checked the same way, and every file
  referenced by the manifest must exist in the export directory.
- **Material check** — the synthetic test scene assigns a material to every
  mesh, and the test asserts the exported static FBX actually carries them
  (a regression that silently drops materials would be caught).
- **Blank material slot check** — the synthetic test scene adds a blank
  (material-less) slot to `body_chassis`, reproducing the slot a material-less
  Boolean cutter leaves behind. `--test-prep` asserts that prep removes it and
  that no blank slot remains in the `prepped` collection. Because the slot is in
  the shared test scene, every pipeline run (`--full-pipeline`,
  `--test-export-validation`, …) also exercises the removal; the exported static
  FBX still carries exactly the real materials, confirming the blank slot was
  stripped rather than exported.

The export folder is **deleted before every export** (the export operator does
not clean up after itself), so a previous successful run can never make a
broken run appear valid.

| Flag | What it does |
|------|--------------|
| `--test-skeleton` | Full pipeline + skin validation only |
| `--test-manifest` | Full pipeline + manifest validation only |
| `--test-export-validation` | Full pipeline + all checks (skin, manifest, materials) |

The same validation is built into `--full-pipeline` and `--test-export`, so
the per-version runs in section 2 double as a regression gate: a release that
reintroduces either bug fails those runs with `[FAIL]` lines naming the exact
problem. The blank-material-slot regression (item 3) is gated by `--test-prep`
and, transitively, by every pipeline run above.

Quick regression check across the supported versions:

```bash
SCRIPT="$REPO/test_runner.py"

"$BLENDER_BUILDS/blender-4.5.1-macos-arm64+lts.b0a72b245dcf/Blender/Blender.app/Contents/MacOS/Blender" \
  -b --python "$SCRIPT" -- --test-export-validation
"$BLENDER_BUILDS/blender-5.2.2-macos-arm64+stable.d13f752e3b9c/Blender/Blender.app/Contents/MacOS/Blender" \
  -b --python "$SCRIPT" -- --test-export-validation
```

---

## 8. Interpreting results

- The run ends with `ALL TESTS PASSED` (exit code `0`) or `SOME TESTS FAILED`
  (exit code `1`).
- `[OK]` / `[PASS]` lines indicate a check succeeded; `[FAIL]` / `[ERROR]` lines
  indicate a failure.
- After a successful `--full-pipeline`, confirm the exported files exist on disk:
  `ls test_scenes/<major.minor>/export_test_self_contained/` should list 3 `.fbx`
  files and 1 `.json`.
- The export validation prints a one-line summary per skeletal FBX, e.g.
  `Deformer=10 skins=1 weighted_clusters=5 Pose=1 Matrix=11 Geometry=1`.
  A broken (1.6.2-style) export shows `Deformer=0 ... Pose=0` and fails with
  `no Deformer elements (mesh is not bound to the armature)`.
