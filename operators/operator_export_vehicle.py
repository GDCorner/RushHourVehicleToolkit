# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy
import os
import json

from ..utils import mesh_helpers

import logging

log = logging.getLogger(__name__)


def export_vehicle_static_meshes(context, scene_filename, export_dir):
    # Deselect everything
    bpy.ops.object.select_all(action='DESELECT')

    # Get the export collection
    export_collection = bpy.data.collections["export"]
    # Get the static_meshes collection from export_collection
    static_meshes_collection = export_collection.children["static_meshes"]

    exports = []

    for mesh in static_meshes_collection.objects:
        if mesh.type == 'MESH':
            mesh_filename = os.path.join(export_dir, f'{mesh.name}-{scene_filename}.fbx')

            # Set the active object
            context.view_layer.objects.active = mesh
            # Select the mesh
            mesh.select_set(True)

            # Export collection as static mesh
            bpy.ops.export_scene.fbx(filepath=mesh_filename, check_existing=False, mesh_smooth_type='FACE',
                                     use_active_collection=False, use_selection=True)

            exports.append(mesh_filename)

            # Deselect the mesh
            mesh.select_set(False)

    return exports


def export_vehicle_skeletal_meshes(context, scene_filename, export_dir):
    # Deselect everything
    bpy.ops.object.select_all(action='DESELECT')

    # Get the export collection
    export_collection = bpy.data.collections["export"]
    # Get the static_meshes collection from export_collection
    skeletal_meshes_collection = export_collection.children["skeleton"]

    # Get the object "SK_phys_mesh" from skeletal_meshes_collection
    skel_body_mesh = skeletal_meshes_collection.objects["SK_phys_mesh"]
    skel_body_mesh.select_set(True)
    context.view_layer.objects.active = skel_body_mesh

    # Select the armature
    armature = skeletal_meshes_collection.objects["Armature"]
    armature.select_set(True)

    skel_body_mesh_filename = os.path.join(export_dir, f'{skel_body_mesh.name}-{scene_filename}.fbx')

    bpy.ops.export_scene.fbx(filepath=skel_body_mesh_filename, check_existing=False, mesh_smooth_type='FACE',
                             use_selection=True, add_leaf_bones=False)

    skel_body_mesh.select_set(False)

    # Get the object "SK_proxy" from skeletal_meshes_collection
    skel_proxy_mesh = skeletal_meshes_collection.objects["SK_proxy"]
    skel_proxy_mesh.select_set(True)
    context.view_layer.objects.active = skel_proxy_mesh

    skel_proxy_mesh_filename = os.path.join(export_dir, f'{skel_proxy_mesh.name}-{scene_filename}.fbx')
    bpy.ops.export_scene.fbx(filepath=skel_proxy_mesh_filename, check_existing=False, mesh_smooth_type='FACE',
                             use_selection=True, add_leaf_bones=False)

    exports = [skel_body_mesh_filename, skel_proxy_mesh_filename]
    return exports


def get_single_wheel_json(wheel_name, wheel_filename, scene_filename):
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

    caliper_filename = None
    if has_caliper:
        caliper_filename = caliper_name + "-" + scene_filename + ".fbx"

    wheel_json = {
        "wheel_radius": wheel_radius,
        "rim_radius": rim_radius,
        "wheel_width": wheel_width,
        "wheel_filename": wheel_filename,
        "brake_caliper_filename": caliper_filename
    }

    return wheel_json


def get_wheel_collection_json(static_meshes, scene_filename):
    # Get the "wheels" collection, and get the wheel collections from it
    wheels_collection = bpy.data.collections["wheels"]
    wheel_collections = wheels_collection.children
    wheels_json = {}
    for wheel in wheel_collections:
        # This is a list comprehension to find appropriate wheel filename
        # but also to just get the single element, as it should only return 1 element
        wheel_filename = [x for x in static_meshes if wheel.name in x][0]
        wheels_json[wheel.name] = get_single_wheel_json(wheel.name, wheel_filename, scene_filename)

    return wheels_json


def write_export_json(static_meshes, skeletal_meshes, scene_filename, export_dir):
    skel_body_filename = [x for x in skeletal_meshes if "SK_phys_mesh" in x][0]
    skel_proxy_filename = [x for x in skeletal_meshes if "SK_proxy" in x][0]

    export_json = {
        "manifest_version": 1.0,
        "name": scene_filename,
        "body_dimensions": get_body_dimensions(),
        "wheels": get_wheel_collection_json(static_meshes, scene_filename),
        "skel_phys_mesh": skel_body_filename,
        "skel_proxy_mesh": skel_proxy_filename,
        "static_meshes": static_meshes,
        "skeletal_meshes": skeletal_meshes
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


def export_process(context):
    scene_filename_full = bpy.path.basename(context.blend_data.filepath)
    scene_filename = os.path.splitext(scene_filename_full)[0]
    # Make a directory called "export" in the same directory as the blend file
    export_dir = f'{bpy.path.abspath("//")}export_{scene_filename}'
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    # delete all files in export_dir
    for file in os.listdir(export_dir):
        pass
        # Deleting has been disabled until further testing. It's high risk, low reward
        # os.remove(os.path.join(export_dir, file))

    exported_static_meshes = export_vehicle_static_meshes(context, scene_filename, export_dir)

    exported_sm_basenames = [os.path.basename(x) for x in exported_static_meshes]

    exported_skeletal_meshes = export_vehicle_skeletal_meshes(context, scene_filename, export_dir)

    exported_sk_basenames = [os.path.basename(x) for x in exported_skeletal_meshes]

    write_export_json(exported_sm_basenames, exported_sk_basenames, scene_filename, export_dir)

    print("Vehicle Export Complete")


class RUSHHOURVP_OT_export_vehicle(bpy.types.Operator):
    """UV Operator description"""
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
