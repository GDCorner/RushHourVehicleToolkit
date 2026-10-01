# TESTING the Rush Hour Vehicle Toolkit addon

This document explains how to run the command-line test harness (`test_runner.py`)
against every supported Blender LTS release and where the results are written.

The harness is **fully self-contained**: it generates its own synthetic vehicle
geometry (body + wheels), runs the addon's operators headlessly, and verifies the
results. No external `.blend` files are required.

---

## Supported Blender LTS versions

`__init__.py` declares `supported_blender_versions = [(3, 6, 0), (4, 2, 0), (4, 5, 0), (5, 2, 0)]`.

| Version | Test build | Output folder |
|---------|------------|---------------|
| 3.6.x   | 3.6.23     | `test_scenes/3.6/` |
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

To install into all four supported versions at once:

```bash
base="$HOME/Library/Application Support/Blender"
for v in 3.6 4.2 4.5 5.2; do
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

> **Blender 3.6** (note the root-level `Blender.app` layout)
```bash
"$BLENDER_BUILDS/blender-3.6.23-macos-arm64+lts.e467db79ca8c/Blender.app/Contents/MacOS/Blender" \
  -b --python "$REPO/test_runner.py" -- --full-pipeline
```

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

Run all four in sequence:

```bash
SCRIPT="$REPO/test_runner.py"

"$BLENDER_BUILDS/blender-3.6.23-macos-arm64+lts.e467db79ca8c/Blender.app/Contents/MacOS/Blender" -b --python "$SCRIPT" -- --full-pipeline
"$BLENDER_BUILDS/blender-4.2.12-macos-arm64+lts.cf1451225401/Blender/Blender.app/Contents/MacOS/Blender" -b --python "$SCRIPT" -- --full-pipeline
"$BLENDER_BUILDS/blender-4.5.1-macos-arm64+lts.b0a72b245dcf/Blender/Blender.app/Contents/MacOS/Blender" -b --python "$SCRIPT" -- --full-pipeline
"$BLENDER_BUILDS/blender-5.2.2-macos-arm64+stable.d13f752e3b9c/Blender/Blender.app/Contents/MacOS/Blender" -b --python "$SCRIPT" -- --full-pipeline
```

---

## 3. Individual operator tests

Each flag runs a single operator (auto-building any prerequisite scene state) so
you can isolate a specific step. Replace `--full-pipeline` with one of these:

| Flag                 | Operator tested |
|----------------------|-----------------|
| `--test-scene-prep`  | `prepare_scene_simple` |
| `--test-collections` | `create_vehicle_collections` |
| `--test-sorting`     | `add_selected_to_vehicle_collection` |
| `--test-prep`        | `prep_vehicle_for_unreal` |
| `--test-rig`         | `rig_vehicle` |
| `--test-export`      | `export_ue_vehicle_fbx` |
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

## 4. Options

| Option | Description |
|--------|-------------|
| `--full-pipeline` | Run the full Simple workflow (prep scene → sort → simple export) |
| `--axle-count N` | Number of axles for the synthetic scene (default: 2) |
| `--file scene.blend` | Test an existing saved `.blend` instead of the generated one |
| `--body-meshes a,b,c` | Body mesh names to sort (only for `--file`) |
| `--wheel-meshes a,b,c` | Wheel mesh names to sort (only for `--file`) |
| `--decimate` | Enable proxy decimation during rig |
| `--decimate-ratio F` | Decimation ratio (default: 0.5) |

Non-default axle counts (e.g. `--axle-count 4`) exercise the advanced operators,
since `prepare_scene_simple` hardcodes 2 axles.

---

## 5. Where the output goes

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

## 6. Interpreting results

- The run ends with `ALL TESTS PASSED` (exit code `0`) or `SOME TESTS FAILED`
  (exit code `1`).
- `[OK]` / `[PASS]` lines indicate a check succeeded; `[FAIL]` / `[ERROR]` lines
  indicate a failure.
- After a successful `--full-pipeline`, confirm the exported files exist on disk:
  `ls test_scenes/<major.minor>/export_test_self_contained/` should list 3 `.fbx`
  files and 1 `.json`.
