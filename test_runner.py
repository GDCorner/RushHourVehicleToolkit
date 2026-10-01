#!/usr/bin/env python3
"""
Blender addon test runner for Rush Hour Vehicle Toolkit.

Fully self-contained - creates its own test geometry. No external blend files needed.

The addon must be installed in your Blender user addons directory first, e.g.:
    ~/Library/Application Support/Blender/<version>/scripts/addons/RushHourVehicleToolkit

Output (scene + exported FBX/JSON) is written to a folder that matches the
major.minor Blender version it ran under:
    <repo>/test_scenes/<major.minor>/
        test_self_contained.blend          (the generated scene)
        export_test_self_contained/        (exported .fbx + .json)
e.g. Blender 5.2 writes to test_scenes/5.2/, Blender 4.5 to test_scenes/4.5/.

IMPORTANT: The '--' separates Blender's arguments from the test runner's arguments.
Everything after '--' is passed to this script.

Usage:
    blender -b --python test_runner.py -- [options]

Examples:
    # Full pipeline with auto-generated test scene
    blender -b --python test_runner.py -- --full-pipeline

    # Full pipeline with 4 axles (e.g. truck)
    blender -b --python test_runner.py -- --full-pipeline --axle-count 4

    # Just test collection creation and sorting
    blender -b --python test_runner.py -- --test-collections --test-sorting

    # Test individual operators
    blender -b --python test_runner.py -- --test-prep
    blender -b --python test_runner.py -- --test-rig
    blender -b --python test_runner.py -- --test-export

    # Test with an existing blend file (must be saved for export to work)
    blender -b --python test_runner.py -- --file scene.blend --full-pipeline
"""

import bpy
import sys
import os
import math
import argparse
import glob as glob_mod
import time
import tempfile

# Path to the addon (used only for locating test scene output)
ADDON_DIR = os.path.dirname(os.path.abspath(__file__))
# The addon module name (folder name in Blender's user addons directory)
ADDON_MODULE = "RushHourVehicleToolkit"


def blender_version_tag():
    """Return the major.minor Blender version tag of the running Blender, e.g. '5.2'."""
    return f"{bpy.app.version[0]}.{bpy.app.version[1]}"


def output_dir():
    """Return the version-specific test output directory: <repo>/test_scenes/<major.minor>/."""
    return os.path.join(ADDON_DIR, "test_scenes", blender_version_tag())


def ensure_addon_enabled():
    """Ensure the addon is enabled.

    The addon must already be installed in Blender's user addons directory,
    e.g. ~/Library/Application Support/Blender/<version>/scripts/addons/RushHourVehicleToolkit
    """
    if ADDON_MODULE in bpy.context.preferences.addons:
        print(f"[OK] Addon {ADDON_MODULE} is enabled")
        return

    print(f"[INFO] Addon {ADDON_MODULE} not enabled, attempting to enable...")
    bpy.ops.preferences.addon_enable(module=ADDON_MODULE)

    if ADDON_MODULE in bpy.context.preferences.addons:
        print(f"[OK] Addon {ADDON_MODULE} is enabled")
    else:
        print(f"[FAIL] Could not enable addon {ADDON_MODULE}.")
        print(f"       Ensure it is installed in your Blender user addons directory:")
        print(f"       ~/Library/Application Support/Blender/<version>/scripts/addons/{ADDON_MODULE}")
        sys.exit(1)


def deselect_all():
    """Deselect all objects in the scene."""
    bpy.ops.object.select_all(action='DESELECT')


def select_object(name):
    """Select a single object by name."""
    deselect_all()
    obj = bpy.data.objects.get(name)
    if obj:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        return True
    else:
        print(f"[WARN] Object '{name}' not found in scene")
        return False


def select_objects(names):
    """Select multiple objects by name."""
    deselect_all()
    found = []
    for name in names:
        obj = bpy.data.objects.get(name.strip())
        if obj:
            obj.select_set(True)
            found.append(name)
        else:
            print(f"[WARN] Object '{name}' not found")
    if found:
        bpy.context.view_layer.objects.active = bpy.data.objects[found[0]]
    return len(found) > 0


def get_mesh_objects():
    """Get all mesh objects in the scene."""
    return [obj for obj in bpy.data.objects if obj.type == 'MESH']


def verify_collection_exists(name, parent=None):
    """Check if a collection exists, optionally under a parent."""
    col = bpy.data.collections.get(name)
    if not col:
        return False
    if parent:
        parent_col = bpy.data.collections.get(parent)
        if not parent_col:
            return False
        child_names = [c.name for c in parent_col.children]
        if col.name not in child_names:
            return False
    return True


def clear_collections(*names):
    """Remove collections by name (safe - ignores missing ones)."""
    for name in names:
        col = bpy.data.collections.get(name)
        if col:
            bpy.data.collections.remove(col)


def save_scene(filepath):
    """Save the current scene to a file. Returns True on success."""
    try:
        # Ensure directory exists
        dir_path = os.path.dirname(filepath)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        bpy.ops.wm.save_as_mainfile(filepath=filepath)
        print(f"[OK] Scene saved to: {filepath}")
        return True
    except Exception as e:
        print(f"[FAIL] Could not save scene: {e}")
        return False


def create_test_scene(axle_count=2):
    """Create a self-contained test scene with synthetic vehicle geometry.

    Creates:
    - Multiple body-part cubes (chassis, hood, doors) to exercise the merge logic
    - For each wheel position: tire, rim, and brake_caliper cubes
    - All objects placed in the scene root, unsorted

    Returns the path to the saved temp scene file.
    """
    print("\nCreating self-contained test scene...")
    print(f"  Axle count: {axle_count}")

    # Clear default scene
    for obj in bpy.data.objects[:]:
        bpy.data.objects.remove(obj, do_unlink=True)
    for col in bpy.data.collections[:]:
        bpy.data.collections.remove(col)

    side_labels = ["L", "R"]
    object_defs = []

    # Create body parts (multiple meshes so the prep merge/join logic is exercised,
    # matching a real vehicle scene where the body is composed of several meshes)
    body_parts = [
        ("body_chassis", (0.0, 0.0, 0.9), (4.0, 1.8, 0.9)),   # main body block
        ("body_hood", (1.5, 0.0, 1.6), (1.4, 1.6, 0.4)),       # hood
        ("body_door_l", (-0.3, -0.9, 1.4), (1.2, 0.1, 0.7)),   # left doors
        ("body_door_r", (-0.3, 0.9, 1.4), (1.2, 0.1, 0.7)),    # right doors
    ]
    for name, loc, scale in body_parts:
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
        part = bpy.context.active_object
        part.name = name
        part.scale = scale
        object_defs.append(name)
        print(f"  Created {name} at {part.location} scale {part.scale}")

    # Create wheel assemblies for each axle
    wheel_positions = []
    wheel_length = 2.4  # Distance between front and rear axles
    wheel_offset_x = wheel_length / 2
    wheel_offset_z = 0.6  # Wheel radius equivalent

    for axle_idx in range(axle_count):
        for side_idx, side in enumerate(side_labels):
            axle = axle_idx
            x = wheel_offset_x if axle_idx == 0 else -(axle_idx - 1) * 1.5
            y = 0.9 if side == "R" else -0.9  # L/R offset

            wheel_pos = (x, y, wheel_offset_z)
            wheel_positions.append((axle, side, wheel_pos))

            # Tire (scaled cube to represent tire)
            bpy.ops.mesh.primitive_cube_add(size=1, location=wheel_pos)
            tire = bpy.context.active_object
            tire.name = f"tire_{axle}_{side}"
            tire.scale = (0.6, 0.4, 0.6)  # Wheel dimensions
            object_defs.append(tire.name)
            print(f"  Created {tire.name} at {tire.location}")

            # Rim (smaller cube inside tire)
            rim_loc = (wheel_pos[0], wheel_pos[1] + 0.15, wheel_pos[2])
            bpy.ops.mesh.primitive_cube_add(size=1, location=rim_loc)
            rim = bpy.context.active_object
            rim.name = f"rim_{axle}_{side}"
            rim.scale = (0.35, 0.1, 0.35)
            object_defs.append(rim.name)
            print(f"  Created {rim.name} at {rim.location}")

            # Brake caliper (small cube)
            caliper_loc = (wheel_pos[0], wheel_pos[1] + 0.25, wheel_pos[2] + 0.15)
            bpy.ops.mesh.primitive_cube_add(size=1, location=caliper_loc)
            caliper = bpy.context.active_object
            caliper.name = f"brake_caliper_{axle}_{side}"
            caliper.scale = (0.2, 0.15, 0.2)
            object_defs.append(caliper.name)
            print(f"  Created {caliper.name} at {caliper.location}")

    # Save the scene into a version-specific, visible output folder, e.g.
    #   <repo>/test_scenes/5.2/test_self_contained.blend
    # The export operator derives its output dir from the blend file location
    # (bpy.path.abspath("//")), so exports land in the same folder:
    #   <repo>/test_scenes/5.2/export_test_self_contained/
    temp_dir = output_dir()
    os.makedirs(temp_dir, exist_ok=True)
    scene_file = os.path.join(temp_dir, "test_self_contained.blend")

    # Remove old test file if it exists
    if os.path.exists(scene_file):
        # Blender may have it locked, try to remove anyway
        try:
            os.remove(scene_file)
        except OSError:
            pass

    print(f"\n  Saving scene to: {scene_file}")
    if not save_scene(scene_file):
        print("  [ERROR] Failed to save scene, trying alternative path...")
        scene_file = os.path.join(tempfile.gettempdir(), "rhvt_test_scene.blend")
        save_scene(scene_file)

    print(f"\n  Total objects created: {len(object_defs)}")
    print(f"  Objects: {', '.join(object_defs)}")

    return scene_file


def run_test(test_name, test_func):
    """Run a single test and report results."""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    start = time.time()
    try:
        result = test_func()
        elapsed = time.time() - start
        if result:
            print(f"\n[PASS] {test_name} ({elapsed:.1f}s)")
            return True
        else:
            print(f"\n[FAIL] {test_name}")
            return False
    except Exception as e:
        elapsed = time.time() - start if 'start' in locals() else 0
        print(f"\n[ERROR] {test_name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scene_prep(context, args):
    """Test: prepare_scene_simple operator."""
    bpy.ops.rushhourvp.prepare_scene_simple()

    checks = [
        ("vehicle collection", lambda: verify_collection_exists("vehicle")),
        ("prepped collection", lambda: verify_collection_exists("prepped")),
        ("scene scale is cm", lambda: math.isclose(bpy.context.scene.unit_settings.scale_length, 0.01, rel_tol=1e-6)),
    ]

    passed = 0
    for name, check in checks:
        if check():
            print(f"  [OK] {name}")
            passed += 1
        else:
            print(f"  [FAIL] {name}")

    return passed == len(checks)


def test_collection_creation(context, args):
    """Test: create_vehicle_collections operator."""
    clear_collections("vehicle", "prepped", "prepped_wheels", "export")

    axle_count = args.axle_count if hasattr(args, 'axle_count') else 2
    bpy.ops.rushhourvp.create_vehicle_collections(axle_count=axle_count)

    checks = [
        ("vehicle collection", lambda: verify_collection_exists("vehicle")),
        ("body collection", lambda: verify_collection_exists("body", "vehicle")),
        ("body_interior collection", lambda: verify_collection_exists("body_interior", "vehicle")),
        ("body_transparent collection", lambda: verify_collection_exists("body_transparent", "vehicle")),
        ("windows_interior collection", lambda: verify_collection_exists("windows_interior", "vehicle")),
        ("windows_exterior collection", lambda: verify_collection_exists("windows_exterior", "vehicle")),
        ("wheels collection", lambda: verify_collection_exists("wheels", "vehicle")),
    ]

    for i in range(axle_count):
        checks.append((f"wheel_{i}_L collection", lambda ax=i: verify_collection_exists(f"wheel_{ax}_L", "wheels")))
        checks.append((f"wheel_{i}_R collection", lambda ax=i: verify_collection_exists(f"wheel_{ax}_R", "wheels")))
        checks.append((f"rim_{i}_L collection", lambda ax=i: verify_collection_exists(f"rim_{ax}_L", f"wheel_{ax}_L")))
        checks.append((f"rim_{i}_R collection", lambda ax=i: verify_collection_exists(f"rim_{ax}_R", f"wheel_{ax}_R")))
        checks.append((f"brake_caliper_{i}_L collection", lambda ax=i: verify_collection_exists(f"brake_caliper_{ax}_L", f"wheel_{ax}_L")))
        checks.append((f"brake_caliper_{i}_R collection", lambda ax=i: verify_collection_exists(f"brake_caliper_{ax}_R", f"wheel_{ax}_R")))

    passed = 0
    for name, check in checks:
        if check():
            print(f"  [OK] {name}")
            passed += 1
        else:
            print(f"  [FAIL] {name}")

    return passed == len(checks)


def test_sort_objects(context, args):
    """Test: add_selected_to_vehicle_collection operator."""
    if not verify_collection_exists("vehicle"):
        print("  [INFO] Creating vehicle collections first...")
        bpy.ops.rushhourvp.create_vehicle_collections(axle_count=args.axle_count)

    # Parse object lists from args (for external blend files)
    body_objs = [o.strip() for o in args.body_meshes.split(",")] if hasattr(args, 'body_meshes') and args.body_meshes else []
    wheel_objs = [o.strip() for o in args.wheel_meshes.split(",")] if hasattr(args, 'wheel_meshes') and args.wheel_meshes else []

    # For self-contained mode, auto-detect our test objects
    if not body_objs and not wheel_objs:
        body_objs = [obj.name for obj in bpy.data.objects if obj.name.startswith("body")]
        wheel_objs = [obj.name for obj in bpy.data.objects if obj.name.startswith(("tire_", "rim_", "brake_caliper_"))]

    if not body_objs and not wheel_objs:
        print("  [SKIP] No object lists provided")
        return True

    passed = 0
    total = 0

    # Add to body
    if body_objs:
        total += 1
        if select_objects(body_objs):
            bpy.ops.rushhourvp.add_selected_to_vehicle_collection(collection_name="body")
            body_col = bpy.data.collections.get("body")
            if body_col:
                moved = [obj for obj in body_col.objects if obj.name in body_objs]
                if len(moved) == len(body_objs):
                    print(f"  [OK] Moved {len(moved)}/{len(body_objs)} body objects")
                    passed += 1
                else:
                    print(f"  [FAIL] Expected {len(body_objs)} body objects, found {len(moved)}")
            else:
                print("  [FAIL] Body collection not found")
        else:
            print("  [FAIL] Could not select body objects")

    # Add to wheels
    if wheel_objs:
        wheel_groups = {}
        for obj_name in wheel_objs:
            parts = obj_name.rsplit("_", 2)
            if len(parts) >= 3 and parts[0] in ("tire", "rim", "brake_caliper"):
                key = f"wheel_{parts[1]}_{parts[2]}"
            else:
                key = "wheel_0_L"
            wheel_groups.setdefault(key, []).append(obj_name)

        for wheel_col_name, objs in wheel_groups.items():
            total += 1
            if select_objects(objs):
                bpy.ops.rushhourvp.add_selected_to_vehicle_collection(collection_name=wheel_col_name)
                target_col = bpy.data.collections.get(wheel_col_name)
                if target_col:
                    moved = [obj for obj in target_col.objects if obj.name in objs]
                    if len(moved) == len(objs):
                        print(f"  [OK] Moved {len(moved)}/{len(objs)} objects to {wheel_col_name}")
                        passed += 1
                    else:
                        print(f"  [FAIL] Expected {len(objs)} objects in {wheel_col_name}, found {len(moved)}")
                else:
                    print(f"  [FAIL] Collection {wheel_col_name} not found")
            else:
                print(f"  [FAIL] Could not select objects for {wheel_col_name}")

    return passed == total if total > 0 else True


def _vehicle_tree_objects():
    """Get all objects in the vehicle collection tree (recursively)."""
    vehicle = bpy.data.collections.get("vehicle")
    if not vehicle:
        return set()
    result = set()
    def walk(col):
        for obj in col.objects:
            result.add(obj)
        for child in col.children:
            walk(child)
    walk(vehicle)
    return result


def prepare_scene_for(context, stage, args):
    """Build up scene state incrementally so individual operator tests can run
    standalone on a fresh scene. stage is one of 'sorted', 'prepped', 'rigged'."""
    # Ensure vehicle collections exist
    if not verify_collection_exists("vehicle"):
        print("  [SETUP] Creating vehicle collections...")
        bpy.ops.rushhourvp.create_vehicle_collections(axle_count=args.axle_count)

    # Sort any test objects still outside the vehicle tree
    vehicle_objs = _vehicle_tree_objects()
    unsorted = [obj for obj in bpy.data.objects
                if obj.type == 'MESH'
                and obj.name.startswith(("body", "tire_", "rim_", "brake_caliper_"))
                and obj not in vehicle_objs]
    if unsorted:
        print(f"  [SETUP] Sorting {len(unsorted)} objects into vehicle collections...")
        args.body_meshes = ",".join(o.name for o in unsorted if o.name.startswith("body"))
        args.wheel_meshes = ",".join(o.name for o in unsorted if o.name.startswith(("tire_", "rim_", "brake_caliper_")))
        test_sort_objects(context, args)

    if stage in ("prepped", "rigged") and not verify_collection_exists("prepped"):
        print("  [SETUP] Running prep_vehicle_for_unreal...")
        bpy.ops.rushhourvp.prep_vehicle_for_unreal()

    if stage == "rigged" and not verify_collection_exists("export"):
        print("  [SETUP] Running rig_vehicle...")
        bpy.ops.rushhourvp.rig_vehicle(decimate_proxy_mesh=False, decimate_amount=0.5)


def test_prep_vehicle(context, args):
    """Test: prep_vehicle_for_unreal operator."""
    prepare_scene_for(context, "sorted", args)

    bpy.ops.rushhourvp.prep_vehicle_for_unreal()

    checks = [
        ("prepped collection created", lambda: verify_collection_exists("prepped")),
        ("prepped_wheels collection created", lambda: verify_collection_exists("prepped_wheels", "prepped")),
    ]

    prepped = bpy.data.collections.get("prepped")
    if prepped:
        checks.append(("body mesh in prepped", lambda: "body" in prepped.objects))
        checks.append(("proxy mesh in prepped", lambda: "proxy" in prepped.objects))

    # Check wheel meshes
    prepped_wheels = bpy.data.collections.get("prepped_wheels")
    if prepped_wheels:
        wheel_meshes = [obj for obj in prepped_wheels.objects if obj.name.startswith("wheel_")]
        checks.append((f"wheel meshes in prepped_wheels ({len(wheel_meshes)})", lambda: len(wheel_meshes) > 0))

    passed = sum(1 for _, check in checks if check())
    for name, check in checks:
        status = "[OK]" if check() else "[FAIL]"
        print(f"  {status} {name}")

    return passed == len(checks)


def test_rig_vehicle(context, args):
    """Test: rig_vehicle operator."""
    prepare_scene_for(context, "prepped", args)

    decimate = args.decimate if hasattr(args, 'decimate') and args.decimate else False
    ratio = args.decimate_ratio if hasattr(args, 'decimate_ratio') else 0.5

    bpy.ops.rushhourvp.rig_vehicle(decimate_proxy_mesh=decimate, decimate_amount=ratio)

    checks = [
        ("export collection created", lambda: verify_collection_exists("export")),
        ("skeleton collection in export", lambda: verify_collection_exists("skeleton", "export")),
        ("static_meshes collection in export", lambda: verify_collection_exists("static_meshes", "export")),
    ]

    skel = bpy.data.collections.get("skeleton")
    if skel:
        armatures = [obj for obj in skel.objects if obj.type == 'ARMATURE']
        checks.append(("armature created", lambda: len(armatures) > 0))

        skel_meshes = [obj for obj in skel.objects if obj.type == 'MESH']
        checks.append(("skeletal meshes created", lambda: len(skel_meshes) > 0))

        # Check for expected skeletal mesh names
        checks.append(("SK_phys_mesh exists", lambda: "SK_phys_mesh" in skel.objects))
        checks.append(("SK_proxy exists", lambda: "SK_proxy" in skel.objects))

    passed = sum(1 for _, check in checks if check())
    for name, check in checks:
        status = "[OK]" if check() else "[FAIL]"
        print(f"  {status} {name}")

    return passed == len(checks)


def test_export_vehicle(context, args):
    """Test: export_ue_vehicle_fbx operator."""
    prepare_scene_for(context, "rigged", args)

    scene_name = os.path.splitext(os.path.basename(bpy.data.filepath))[0] if bpy.data.filepath else "test"

    bpy.ops.rushhourvp.export_ue_vehicle_fbx()

    export_dir = os.path.join(bpy.path.abspath("//"), f"export_{scene_name}")
    if os.path.isdir(export_dir):
        files = os.listdir(export_dir)
        print(f"  [OK] Export directory: {export_dir}")
        print(f"  [OK] Files: {files}")
        fbx_count = len([f for f in files if f.endswith('.fbx')])
        json_count = len([f for f in files if f.endswith('.json')])
        print(f"  [OK] FBX files: {fbx_count}, JSON files: {json_count}")
        return fbx_count >= 2 and json_count >= 1
    else:
        print(f"  [FAIL] Export directory not found: {export_dir}")
        return False


def _scene_prep_simple(context, args):
    """Run the 'Prepare Scene' simple button. Falls back to the equivalent
    advanced operators when a non-default axle count is requested, since
    prepare_scene_simple hardcodes 2 axles."""
    if args.axle_count == 2:
        bpy.ops.rushhourvp.prepare_scene_simple()
    else:
        bpy.ops.rushhourvp.create_vehicle_collections(axle_count=args.axle_count)
        bpy.ops.rushhourvp.set_scene_cm_scale()
        bpy.ops.rushhourvp.clear_parents()

    checks = [
        ("vehicle collection", lambda: verify_collection_exists("vehicle")),
        ("wheels collection", lambda: verify_collection_exists("wheels", "vehicle")),
        ("scene scale is cm", lambda: math.isclose(bpy.context.scene.unit_settings.scale_length, 0.01, rel_tol=1e-6)),
    ]
    passed = 0
    for name, check in checks:
        if check():
            print(f"  [OK] {name}")
            passed += 1
        else:
            print(f"  [FAIL] {name}")
    return passed == len(checks)


def _export_simple(context, args):
    """Run the 'Export Vehicle - Simple' button (prep + rig + export + check)."""
    scene_name = os.path.splitext(os.path.basename(bpy.data.filepath))[0] if bpy.data.filepath else "test"

    result = bpy.ops.rushhourvp.export_vehicle_simple()
    if "CANCELLED" in result:
        print(f"  [FAIL] export_vehicle_simple returned {result}")
        return False

    export_dir = os.path.join(bpy.path.abspath("//"), f"export_{scene_name}")
    if os.path.isdir(export_dir):
        files = os.listdir(export_dir)
        fbx_count = len([f for f in files if f.endswith('.fbx')])
        json_count = len([f for f in files if f.endswith('.json')])
        print(f"  [OK] Exported to {export_dir}: {fbx_count} FBX, {json_count} JSON")
        return fbx_count >= 2 and json_count >= 1
    else:
        print(f"  [FAIL] Export directory not found: {export_dir}")
        return False


def test_full_pipeline(context, args):
    """Test: run the full 'Simple' panel workflow (Prepare Scene -> Add To Collections -> Export Simple)."""
    results = {}

    results["scene_prep"] = run_test("Prepare Scene (simple)",
                                      lambda: _scene_prep_simple(context, args))

    results["sorting"] = run_test("Add To Vehicle Collections",
                                   lambda: test_sort_objects(context, args))

    results["export_simple"] = run_test("Export Vehicle - Simple",
                                         lambda: _export_simple(context, args))

    return all(results.values())


def test_check_vehicle(context, args):
    """Test: check_vehicle operator."""
    prepare_scene_for(context, "prepped", args)

    bpy.ops.rushhourvp.check_vehicle()
    checks = bpy.context.scene.vehicle_checks
    print(f"  [OK] Vehicle checks ran successfully")
    print(f"    is_passing_all_checks: {checks.is_passing_all_checks}")
    return True


def test_center_vehicle(context, args):
    """Test: center_vehicle operator."""
    prepare_scene_for(context, "sorted", args)
    vehicle = bpy.data.collections.get("vehicle")
    meshes = [o for o in vehicle.all_objects if o.type == 'MESH'] if vehicle else []
    if not meshes:
        print("  [SKIP] No meshes in vehicle collection")
        return True

    bpy.ops.rushhourvp.center_vehicle()

    # Verify the vehicle now sits on the floor (min Z ~ 0)
    z_values = [(o.matrix_world @ v.co).z for o in meshes for v in o.data.vertices]
    z_min = min(z_values) if z_values else 0.0
    print(f"  [OK] Centered {len(meshes)} meshes, min Z = {z_min:.4f}")
    return math.isclose(z_min, 0.0, abs_tol=1e-2)


def test_show_bounds(context, args):
    """Test: show_object_bounds operator."""
    meshes = get_mesh_objects()
    if not meshes:
        print("  [SKIP] No mesh objects in scene")
        return True

    bpy.ops.rushhourvp.show_object_bounds()
    print(f"  [OK] Bounds toggled for {len(meshes)} objects")
    bpy.ops.rushhourvp.show_object_bounds()
    return True


def main():
    parser = argparse.ArgumentParser(
        prog="test_runner.py",
        description="Test runner for Rush Hour Vehicle Toolkit addon",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
The '--' is required to separate Blender's args from the test runner's args.

Examples:
  # Fully self-contained test (creates its own geometry)
  blender -b --python test_runner.py -- --full-pipeline

  # With different axle counts
  blender -b --python test_runner.py -- --full-pipeline --axle-count 4

  # Test individual steps
  blender -b --python test_runner.py -- --test-collections
  blender -b --python test_runner.py -- --test-sorting
  blender -b --python test_runner.py -- --test-prep
  blender -b --python test_runner.py -- --test-rig
  blender -b --python test_runner.py -- --test-export

  # With an existing blend file
  blender -b --python test_runner.py -- --file scene.blend --full-pipeline
        """
    )

    # Scene input (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("--file", "-f", help="Path to an existing .blend file to test (optional, defaults to self-contained test scene)")
    input_group.add_argument("--self-contained", action="store_true", help="Create a self-contained test scene with synthetic geometry (default if no --file specified)")

    # Test modes
    parser.add_argument("--full-pipeline", action="store_true", help="Run full pipeline: scene prep -> sort -> prep -> rig -> export")
    parser.add_argument("--test-scene-prep", action="store_true", help="Test scene prep operator")
    parser.add_argument("--test-collections", action="store_true", help="Test collection creation operator")
    parser.add_argument("--test-sorting", action="store_true", help="Test object sorting into collections")
    parser.add_argument("--test-prep", action="store_true", help="Test vehicle prep operator")
    parser.add_argument("--test-rig", action="store_true", help="Test rig vehicle operator")
    parser.add_argument("--test-export", action="store_true", help="Test export operator")
    parser.add_argument("--test-check", action="store_true", help="Test vehicle check operator")
    parser.add_argument("--test-center", action="store_true", help="Test center vehicle operator")
    parser.add_argument("--test-bounds", action="store_true", help="Test show bounds operator")
    parser.add_argument("--test-operator", help="Test a specific operator by bl_idname")

    # Test data options
    parser.add_argument("--body-meshes", help="Comma-separated list of mesh names to add to body collection (for external blend files)")
    parser.add_argument("--wheel-meshes", help="Comma-separated list of mesh names to add to wheel collections (for external blend files)")
    parser.add_argument("--axle-count", type=int, default=2, help="Number of axles for test scene (default: 2)")
    parser.add_argument("--decimate", action="store_true", help="Enable decimation during rig (default: off)")
    parser.add_argument("--decimate-ratio", type=float, default=0.5, help="Decimation ratio (default: 0.5)")

    # Blender passes its full command line in sys.argv (e.g. ['Blender', '-b', '--python',
    # 'test_runner.py', '--', '--full-pipeline']). Only parse args after the last '--'.
    if '--' in sys.argv:
        last_sep = len(sys.argv) - 1 - sys.argv[::-1].index('--')
        script_args = sys.argv[last_sep + 1:]
    else:
        script_args = sys.argv[1:]
    args = parser.parse_args(script_args)

    # Determine if using self-contained mode or external file
    use_self_contained = not args.file
    blend_file = args.file

    if use_self_contained:
        print("="*60)
        print("RUSH HOUR VEHICLE TOOLKIT - TEST RUNNER")
        print("Mode: Self-contained (creating synthetic test scene)")
        print(f"Blender version: {bpy.app.version_string}")
        print(f"Output directory: {output_dir()}")
        print("="*60)

        # Create the test scene
        blend_file = create_test_scene(axle_count=args.axle_count)
        print(f"\nUsing test scene: {blend_file}")

        # Re-open the saved scene to start fresh
        bpy.ops.wm.open_mainfile(filepath=blend_file)

    # Ensure addon is enabled
    ensure_addon_enabled()

    # Determine test mode
    test_mode = None
    if args.full_pipeline:
        test_mode = "full_pipeline"
    elif args.test_scene_prep:
        test_mode = "scene_prep"
    elif args.test_collections:
        test_mode = "collections"
    elif args.test_sorting:
        test_mode = "sorting"
    elif args.test_prep:
        test_mode = "prep"
    elif args.test_rig:
        test_mode = "rig"
    elif args.test_export:
        test_mode = "export"
    elif args.test_check:
        test_mode = "check"
    elif args.test_center:
        test_mode = "center"
    elif args.test_bounds:
        test_mode = "bounds"
    elif args.test_operator:
        test_mode = "operator"

    if not test_mode:
        print("No test specified.")
        print("\nAvailable tests:")
        print("  --full-pipeline    Full pipeline: scene prep -> sort -> prep -> rig -> export")
        print("  --test-scene-prep  Test prepare_scene_simple operator")
        print("  --test-collections Test create_vehicle_collections operator")
        print("  --test-sorting     Test add_selected_to_vehicle_collection operator")
        print("  --test-prep        Test prep_vehicle_for_unreal operator")
        print("  --test-rig         Test rig_vehicle operator")
        print("  --test-export      Test export_ue_vehicle_fbx operator")
        print("  --test-check       Test check_vehicle operator")
        print("  --test-center      Test center_vehicle operator")
        print("  --test-bounds      Test show_object_bounds operator")
        print("  --test-operator    Test a specific operator by bl_idname")
        print("\nExamples (note the required '--' before test runner args):")
        print("  blender -b --python test_runner.py -- --full-pipeline")
        print("  blender -b --python test_runner.py -- --full-pipeline --axle-count 4")
        print("  blender -b --python test_runner.py -- --file scene.blend --test-prep")
        sys.exit(1)

    # Map test modes to functions
    test_map = {
        "scene_prep": lambda: test_scene_prep(bpy.context, args),
        "collections": lambda: test_collection_creation(bpy.context, args),
        "sorting": lambda: test_sort_objects(bpy.context, args),
        "prep": lambda: test_prep_vehicle(bpy.context, args),
        "rig": lambda: test_rig_vehicle(bpy.context, args),
        "export": lambda: test_export_vehicle(bpy.context, args),
        "full_pipeline": lambda: test_full_pipeline(bpy.context, args),
        "check": lambda: test_check_vehicle(bpy.context, args),
        "center": lambda: test_center_vehicle(bpy.context, args),
        "bounds": lambda: test_show_bounds(bpy.context, args),
    }

    all_passed = True

    if test_mode == "operator":
        op_id = args.test_operator
        print(f"\nTesting operator: {op_id}")
        try:
            op = getattr(bpy.ops, op_id.replace(".", ","))
            op()
            print(f"[PASS] Operator {op_id} executed successfully")
        except Exception as e:
            print(f"[FAIL] Operator {op_id} failed: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    else:
        all_passed = test_map[test_mode]()

    # Print summary
    print(f"\n{'='*60}")
    if all_passed:
        print("ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
