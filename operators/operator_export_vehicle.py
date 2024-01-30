# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy
import os
import json

from ..utils import mesh_helpers

import logging

log = logging.getLogger(__name__)


def export_skeletal_fbx_selected(filepath: str):
    bpy.ops.export_scene.fbx(filepath=filepath, check_existing=False, mesh_smooth_type='FACE',
                             use_selection=True, add_leaf_bones=False, path_mode='COPY', embed_textures=False)


def export_static_fbx_selected(filepath: str):
    bpy.ops.export_scene.fbx(filepath=filepath, check_existing=False, mesh_smooth_type='FACE',
                             use_active_collection=False, use_selection=True, path_mode='COPY',
                             embed_textures=True)


def export_static_usd_selected(filepath: str):
    bpy.ops.wm.usd_export(filepath=filepath, check_existing=False, selected_objects_only=True, overwrite_textures=True,
                          export_textures=True)


def export_static_gltf_selected(filepath: str):
    bpy.ops.export_scene.gltf(filepath=filepath, check_existing=False, use_selection=True)


def export_skeletal_usd_selected(filepath: str):
    bpy.ops.wm.usd_export(filepath=filepath, check_existing=False, selected_objects_only=True, overwrite_textures=False,
                          export_textures=False, export_materials=False)


def export_vehicle_static_meshes(context, scene_filename: str, export_dir: str, export_format: str = "usd"):
    static_mesh_filename = os.path.join(export_dir, f'{scene_filename}_static')

    if export_format == "fbx":
        static_mesh_filename = static_mesh_filename + ".fbx"
        log.info("Exporting static meshes as FBX")
    elif export_format == "usd":
        static_mesh_filename = static_mesh_filename + ".usd"
        log.info("Exporting static meshes as USD")
    elif export_format == "gltf":
        static_mesh_filename = static_mesh_filename + ".glb"
        log.info("Exporting static meshes as GLTF")
    else:
        static_mesh_filename = static_mesh_filename + ".usd"
        log.warning("Unknown export format, defaulting to USD")

    ############
    # Static Meshes
    ############

    # Deselect everything
    bpy.ops.object.select_all(action='DESELECT')

    # Get the export collection
    export_collection = bpy.data.collections["export"]
    # Get the static_meshes collection from export_collection
    static_meshes_collection = export_collection.children["static_meshes"]

    exported_meshes = []

    # Select all static meshes
    for mesh in static_meshes_collection.objects:
        if mesh.type == 'MESH':
            # Set the active object
            context.view_layer.objects.active = mesh
            # Select the mesh
            mesh.select_set(True)
            exported_meshes.append(mesh.name + ":" + mesh.data.name)

    if export_format == "fbx":
        export_static_fbx_selected(filepath=static_mesh_filename)
    elif export_format == "gltf":
        export_static_gltf_selected(filepath=static_mesh_filename)
    else:
        export_static_usd_selected(filepath=static_mesh_filename)

    # Deselect everything
    bpy.ops.object.select_all(action='DESELECT')

    exported_files = [static_mesh_filename]

    return exported_files, exported_meshes


def export_vehicle_skeletal_meshes(context, scene_filename, export_dir, export_format: str = "fbx"):
    if  export_format == "fbx":
        log.info("Exporting skeletal meshes as FBX")
    elif export_format == "usd":
        log.info("Exporting skeletal meshes as USD")
    else:
        log.warning("Unknown export format, defaulting to FBX")

    exported_meshes = []

    # Deselect everything
    bpy.ops.object.select_all(action='DESELECT')

    # Get the export collection
    export_collection = bpy.data.collections["export"]
    # Get the static_meshes collection from export_collection
    skeletal_meshes_collection = export_collection.children["skeleton"]

    # Get the object "SK_phys_mesh" from skeletal_meshes_collection
    skel_body_mesh = skeletal_meshes_collection.objects["SK_phys_mesh"]
    exported_meshes.append(skel_body_mesh.name + ":" + skel_body_mesh.data.name)
    skel_body_mesh.select_set(True)
    context.view_layer.objects.active = skel_body_mesh

    # Select the armature
    armature = skeletal_meshes_collection.objects["Armature"]
    armature.select_set(True)

    skel_body_mesh_filename = os.path.join(export_dir, f'{skel_body_mesh.name}-{scene_filename}')
    if export_format == "usd":
        skel_body_mesh_filename = skel_body_mesh_filename + ".usd"
        export_skeletal_usd_selected(filepath=skel_body_mesh_filename)
    else:
        skel_body_mesh_filename = skel_body_mesh_filename + ".fbx"
        export_skeletal_fbx_selected(filepath=skel_body_mesh_filename)

    skel_body_mesh.select_set(False)

    # Get the object "SK_proxy" from skeletal_meshes_collection
    skel_proxy_mesh = skeletal_meshes_collection.objects["SK_proxy"]
    exported_meshes.append(skel_proxy_mesh.name + ":" + skel_proxy_mesh.data.name)
    skel_proxy_mesh.select_set(True)
    context.view_layer.objects.active = skel_proxy_mesh

    skel_proxy_mesh_filename = os.path.join(export_dir, f'{skel_proxy_mesh.name}-{scene_filename}')
    if export_format == "usd":
        skel_proxy_mesh_filename = skel_proxy_mesh_filename + ".usd"
        export_skeletal_usd_selected(filepath=skel_proxy_mesh_filename)
    else:
        skel_proxy_mesh_filename = skel_proxy_mesh_filename + ".fbx"
        export_skeletal_fbx_selected(filepath=skel_proxy_mesh_filename)

    exported_files = [skel_body_mesh_filename, skel_proxy_mesh_filename]
    return exported_files, exported_meshes


def get_single_wheel_json(wheel_name, static_meshes):
    # Get the vehicle collection
    vehicle_collection = bpy.data.collections["prepped"]
    all_wheels_collection = vehicle_collection.children["prepped_wheels"]
    # get the mesh from the vehicle collection
    wheel_obj = all_wheels_collection.objects[wheel_name]

    wheel_radius = wheel_obj["wheel_radius"]
    wheel_width = wheel_obj["wheel_width"]
    rim_radius = wheel_obj["rim_radius"]

    # Get export collection static mesh collection
    export_collection = bpy.data.collections["export"]
    static_meshes_collection = export_collection.children["static_meshes"]
    caliper_name = "SM_" + wheel_name.replace("wheel", "brake_caliper")
    has_caliper = False
    for obj in static_meshes_collection.objects:
        if obj.name == caliper_name:
            has_caliper = True
            break

    # This is a list comprehension to find appropriate wheel filename
    # but also to just get the single element, as it should only return 1 element
    wheel_export_name = [x for x in static_meshes if wheel_name in x][0]
    caliper_filename = None
    if has_caliper:
        caliper_filename = [x for x in static_meshes if caliper_name in x][0]

    wheel_json = {
        "wheel_radius": wheel_radius,
        "rim_radius": rim_radius,
        "wheel_width": wheel_width,
        "wheel_filename": wheel_export_name,
        "brake_caliper_filename": caliper_filename
    }

    return wheel_json


def get_wheel_collection_json(static_meshes, scene_filename):
    # Get the "wheels" collection, and get the wheel collections from it
    wheels_collection = bpy.data.collections["wheels"]
    wheel_collections = wheels_collection.children
    wheels_json = {}
    for wheel in wheel_collections:
        wheels_json[wheel.name] = get_single_wheel_json(wheel.name, static_meshes)

    return wheels_json


def write_export_json(static_meshes, static_mesh_files, skeletal_meshes, skeletal_mesh_files, scene_filename, export_dir):
    try:
        skel_body_filename = [x for x in skeletal_mesh_files if "SK_phys_mesh" in x][0]
        skel_proxy_filename = [x for x in skeletal_mesh_files if "SK_proxy" in x][0]
    except:
        skel_body_filename = ""
        skel_proxy_filename = ""

    export_json = {
        "manifest_version": 2.0,
        "name": scene_filename,
        "body_dimensions": get_body_dimensions(),
        "wheels": get_wheel_collection_json(static_meshes, scene_filename),
        "skel_phys_mesh": skel_body_filename,
        "skel_proxy_mesh": skel_proxy_filename,
        "skeletal_mesh_files": skeletal_mesh_files,
        "static_mesh_files": static_mesh_files,
        "static_mesh_names": static_meshes,
        "skeletal_mesh_names": skeletal_meshes
    }

    # write export_json to file
    export_json_filename = os.path.join(export_dir, f'export_{scene_filename}.json')
    with open(export_json_filename, 'w') as outfile:
        json.dump(export_json, outfile, indent=4)


def get_body_dimensions():
    """Measures the size of the body for drag calculations in-engine.
    This is actually an approximation that should be good enough for the vast majority of vehicles. It measures all
    export static meshes which are centered on the origin. So most wheels should be contained entirely within the
    vehicle body mesh. This is not true for all vehicles, but it should be good enough for most."""
    # get the export collection
    export_collection = bpy.data.collections["export"]
    # get the static meshes collection from the export collection
    static_meshes_collection = export_collection.children["static_meshes"]
    body_bounds = mesh_helpers.get_bounds_of_meshes(static_meshes_collection.objects)

    dimensions = {
        "width": mesh_helpers.get_y_size_of_bounds(body_bounds),
        "height": mesh_helpers.get_z_size_of_bounds(body_bounds),
        "length": mesh_helpers.get_x_size_of_bounds(body_bounds)
    }

    return dimensions


def force_sub_layer_collection_visible(collection, parent_layer_collection, original_visibilities):
    layer_collection = parent_layer_collection.children[collection.name]
    # Store original visibility for after export
    original_visibilities[layer_collection] = layer_collection.hide_viewport
    layer_collection.hide_viewport = False

    # Recurse through other sub collections
    for sub_collection in collection.children:
        force_sub_layer_collection_visible(sub_collection, layer_collection, original_visibilities)

    # Set all objects to visible
    for obj in collection.objects:
        # Store original visibility for after export
        original_visibilities[obj] = obj.hide_get()
        obj.hide_set(False)


def force_export_collection_visible():
    original_visibilities = {}

    view_layer = bpy.context.view_layer
    export_layer_collection = view_layer.layer_collection.children['export']
    # Store original visibility for after export
    original_visibilities[export_layer_collection] = export_layer_collection.hide_viewport
    export_layer_collection.hide_viewport = False

    export_collection = bpy.data.collections["export"]
    # Get the static_meshes collection from export_collection
    for collection in export_collection.children:
        force_sub_layer_collection_visible(collection, export_layer_collection, original_visibilities)

    return original_visibilities


def fix_forbidden_chars(name):
    forbidden_chars = [" ", ".", "-"]
    for char in forbidden_chars:
        name = name.replace(char, "_")

    return name


def export_process(context):
    # Force all objects in the export collection to be visible or export will be blank meshes
    original_visibilities = force_export_collection_visible()

    scene_filename_full = bpy.path.basename(context.blend_data.filepath)
    scene_filename = os.path.splitext(scene_filename_full)[0]
    scene_filename = fix_forbidden_chars(scene_filename)

    # Make a directory called "export" in the same directory as the blend file
    export_dir = f'{bpy.path.abspath("//")}export_{scene_filename}'
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    exported_sm_files, exported_static_meshes = export_vehicle_static_meshes(context, scene_filename, export_dir, export_format="fbx")
    exported_sm_files = [os.path.basename(x) for x in exported_sm_files]

    exported_sk_files, exported_skeletal_meshes = export_vehicle_skeletal_meshes(context, scene_filename, export_dir, export_format="fbx")
    exported_sk_files = [os.path.basename(x) for x in exported_sk_files]

    write_export_json(exported_static_meshes, exported_sm_files, exported_skeletal_meshes, exported_sk_files, scene_filename, export_dir)

    # Restore visibility states after export
    for item in original_visibilities:
        visibility = original_visibilities[item]
        # check if item is a layer_collection or an object
        if isinstance(item, bpy.types.LayerCollection):
            item.hide_viewport = visibility
        else:
            item.hide_set(visibility)

    print("Vehicle Export Complete")


class RUSHHOURVP_OT_export_vehicle(bpy.types.Operator):
    """Export all appropriate model files and json for Rush Hour Vehicle Importer"""
    bl_idname = "rushhourvp.export_ue_vehicle_fbx"
    bl_label = "Export UE Vehicle"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        export_process(context)
        return {'FINISHED'}


def register():
    print("Registering rush hour export operator")
    bpy.utils.register_class(RUSHHOURVP_OT_export_vehicle)


def unregister():
    print("Un-Registering rush hour export operator")
    bpy.utils.unregister_class(RUSHHOURVP_OT_export_vehicle)


if __name__ == "__main__":
    register()
