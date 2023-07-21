# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy

from ..utils import mesh_helpers, collection_helpers

from mathutils import Vector

from ..utils import mesh_helpers

import logging

# Create proxy mesh with single tiny triangle at 0,0,0.
# This allows usage of a skeletal mesh in unreal, while having all the geometry be static meshes
def create_proxy_mesh(context, parent_bone_name):
    mesh = bpy.data.meshes.new("proxy")
    mesh.from_pydata([(0.0001, 0, 0), (0, 0.0001, 0), (0, 0, 0)], [], [(0, 1, 2)])
    mesh.update()

    # Add mesh to new object at 0,0,0
    mesh_obj = bpy.data.objects.new("proxy", mesh)

    # Add mesh to prepped collection
    prepped_collection = bpy.data.collections["prepped"]
    prepped_collection.objects.link(mesh_obj)

    return mesh_obj


def merge_objects(context, objects, new_name):
    # Deselect any objects that might still be selected
    bpy.ops.object.select_all(action='DESELECT')

    # Apply split normals to resolve any issue with auto-smoothing differences between meshes
    # Split the normals to ensure that surfaces aren't messed up during the merge process
    if bpy.app.version >= (3, 4, 0):
        # if blender 3.4 or newer, use the new operator
        for obj in objects:
            print("obj: ", obj.name, obj.type)
            bpy.context.view_layer.objects.active = obj
            if obj.type == "MESH":
                obj.select_set(True)
                mesh_helpers.apply_all_modifiers(context)
                if not obj.data.has_bevel_weight_vertex:
                    bpy.ops.mesh.customdata_bevel_weight_vertex_add()
                if not obj.data.has_bevel_weight_edge:
                    bpy.ops.mesh.customdata_bevel_weight_edge_add()
                if not obj.data.has_crease_vertex:
                    bpy.ops.mesh.customdata_crease_vertex_add()
                if not obj.data.has_crease_edge:
                    bpy.ops.mesh.customdata_crease_edge_add()
                mesh_helpers.apply_split_normals(obj)
                obj.select_set(False)
    else:
        # If older then blender 3.4, use the old method
        for obj in objects:
            print("obj: ", obj.name, obj.type)
            if obj.type == "MESH":
                obj.select_set(True)
                mesh_helpers.apply_all_modifiers(context)
                obj.data.use_customdata_vertex_bevel = True
                obj.data.use_customdata_edge_bevel = True
                obj.data.use_customdata_edge_crease = True
                mesh_helpers.apply_split_normals(obj)
                obj.select_set(False)

    # Select all meshes in preparation for join operation
    for obj in objects:
        print("obj: ", obj.name, obj.type)
        if obj.type == "MESH":
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

    # Join meshes in collection
    bpy.ops.object.join()

    # get the currently selected meshes
    new_objects = bpy.context.selected_objects

    bpy.ops.object.select_all(action='DESELECT')
    for curr_object in new_objects:
        recenter_object_origin(curr_object)

    # Change object name to collection name, for consistency
    for obj in new_objects:
        obj.name = new_name

    for object in new_objects:
        deduplicate_material_slots(context, object)

    return new_objects


def recenter_object_origin(target_object):
    """Applies all transforms and then sets the object origin to the center of the geometry."""
    bpy.ops.object.select_all(action='DESELECT')
    target_object.select_set(True)
    bpy.context.view_layer.objects.active = target_object
    # Apply transform for new object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Set the origin to the geometry
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    target_object.select_set(False)


def deduplicate_material_slots(context, target_object):
    # deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    # select object
    target_object.select_set(True)
    # for each material slot in object, find duplicates and remove them, assigning all faces to the first slot
    # This used to not be enumerate as Blender offers slot_index in MaterialSlot struct in later versions.
    # For now enumerate is used to support older versions
    for slot1idx, slot in enumerate(target_object.material_slots):
        for slot2idx, slot2 in enumerate(target_object.material_slots):
            if slot1idx == slot2idx:
                # Skip the same slot
                continue
            if slot.material == slot2.material:
                # Assign all faces that have this slot to the first slot
                for poly in target_object.data.polygons:
                    if poly.material_index == slot2idx:
                        poly.material_index = slot1idx

    # Remove all unused slots
    bpy.ops.object.material_slot_remove_unused()

    # deselect object
    target_object.select_set(False)


def prep_collection(context, collection, new_parent_collection):
    if collection.hide_render:
        # Skip this collection as it's likely booleans and other stuff that we don't want
        return

    if collection.name in ["prepped", "wheels"]:
        # Skip this collection as these are special groups
        return

    objects_to_process = []
    for obj in collection.all_objects:
        if obj.type == "CAMERA":
            # Don't operate on cameras
            continue
        if obj.hide_render:
            # Don't operate on hidden objects
            continue
        if obj.data is None:
            # Don't operate on objects without data
            continue
        objects_to_process.append(obj)

    new_objects = prep_objects(context, objects_to_process, collection.name, new_parent_collection)

    return new_objects


def prep_objects(context, objects, new_name, new_parent_collection):
    new_objs = []

    # for each object in collection
    for obj in objects:
        # duplicate obj
        new_obj = obj.copy()
        if obj.data:
            new_obj.data = obj.data.copy()
        new_obj.animation_data_clear()
        new_parent_collection.objects.link(new_obj)
        new_objs.append(new_obj)
        new_obj.name = new_name + "_" + obj.name

    # Deselect everything
    bpy.ops.object.select_all(action='DESELECT')

    mesh_helpers.fix_negative_scales(new_objs)

    mesh_helpers.remove_blank_materials(new_objs)

    # Deselect everything
    bpy.ops.object.select_all(action='DESELECT')
    # Selected each of the new objects
    for obj in new_objs:
        obj.select_set(True)
        # set active object
        context.view_layer.objects.active = obj

    # UV all the new objects
    bpy.ops.rushhourvp.auto_uv_worldspace(selected_objects_only=True)

    # Deselect everything
    bpy.ops.object.select_all(action='DESELECT')

    new_objects = merge_objects(context, new_objs, new_name)

    return new_objects


def prep_wheel(context, wheel_collection, new_parent_collection):
    if wheel_collection.hide_render:
        # Skip this collection as it's likely booleans and other stuff that we don't want
        return

    wheel_name_split = wheel_collection.name.split("_")
    axle = int(wheel_name_split[1])
    side = wheel_name_split[2]
    caliper_name = "brake_caliper_" + str(axle) + "_" + side
    rim_name = "rim_" + str(axle) + "_" + side
    # Get the brake caliper collection from the wheel_collection
    caliper_collection = wheel_collection.children[caliper_name]
    rim_collection = wheel_collection.children[rim_name]

    rim_objects = []
    for obj in rim_collection.all_objects:
        if obj.hide_render:
            # Don't operate on hidden objects
            continue
        rim_objects.append(obj)
        # deselect all
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        mesh_helpers.apply_all_modifiers(context)
        obj.select_set(False)
        recenter_object_origin(obj)

    caliper_objects = []
    for obj in caliper_collection.all_objects:
        if obj.hide_render:
            # Don't operate on hidden objects
            continue
        caliper_objects.append(obj)

    wheel_objects = []
    for obj in wheel_collection.all_objects:
        if obj.hide_render:
            # Don't operate on hidden objects
            continue
        # deselect all
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        mesh_helpers.apply_all_modifiers(context)
        obj.select_set(False)
        wheel_objects.append(obj)
        recenter_object_origin(obj)

    wheel_size = mesh_helpers.get_bounds_of_meshes(wheel_objects)
    wheel_radius = mesh_helpers.get_x_size_of_bounds(wheel_size) / 2
    wheel_width = mesh_helpers.get_y_size_of_bounds(wheel_size)
    rim_radius = wheel_radius

    if len(rim_objects) > 0:
        rim_size = mesh_helpers.get_bounds_of_meshes(rim_objects)
        rim_radius = mesh_helpers.get_x_size_of_bounds(rim_size) / 2

    # Remove the brake caliper objects from the wheel objects
    for caliper_obj in caliper_objects:
        wheel_objects.remove(caliper_obj)

    wheel_objects = prep_objects(context, wheel_objects, wheel_collection.name, new_parent_collection)
    prep_objects(context, caliper_objects, caliper_collection.name, new_parent_collection)

    # Add wheel radius as custom property to new merged wheel
    for obj in wheel_objects:
        obj["wheel_radius"] = wheel_radius
        obj["wheel_width"] = wheel_width
        obj["rim_radius"] = rim_radius



def prep_vehicle_process(context):
    # Deselect everything
    bpy.ops.object.select_all(action='DESELECT')

    # Create collection "prepped"
    prepped_collection = collection_helpers.create_top_level_collection('prepped')

    # make prepped collection layer visible in viewport so selection works as expected
    prepped_collection.hide_viewport = False
    view_layer = bpy.context.view_layer
    layer_collection = view_layer.layer_collection.children['prepped']
    original_layer_visibility = layer_collection.hide_viewport
    layer_collection.hide_viewport = False

    # Deselect everything
    bpy.ops.object.select_all(action='DESELECT')

    # Delete everything in the prepped collection
    for obj in prepped_collection.all_objects:
        obj.select_set(True)
    bpy.ops.object.delete()

    # Create proxy mesh for the empty skeleton rig
    proxy_mesh_obj = create_proxy_mesh(context, "body")
    proxy_mesh_obj.select_set(True)
    context.view_layer.objects.active = proxy_mesh_obj

    # UV the proxy mesh
    bpy.ops.rushhourvp.auto_uv_worldspace(selected_objects_only=True)
    proxy_mesh_obj.select_set(False)

    # Get collection "vehicle"
    vehicle_collection = bpy.data.collections["vehicle"]

    # for each collection in the parent "vehicle" collection
    for collection in vehicle_collection.children:
        if collection.name == "wheels":
            # Skip wheels for now, they are processed separately
            continue
        prep_collection(context, collection, prepped_collection)

    # Get the wheel collection from vehicle_collection
    wheel_collection = vehicle_collection.children["wheels"]
    # Create a new parent collection for the wheels
    prepped_wheel_parent_collection = collection_helpers.create_collection("prepped_wheels", prepped_collection)
    for collection in wheel_collection.children:
        prep_wheel(context, collection, prepped_wheel_parent_collection)

    # Gather meshes to center
    prepped_meshes = []
    for obj in prepped_collection.all_objects:
        if obj.name == "proxy":
            # Skip the proxy mesh for centering
            continue
        if obj.type == 'MESH':
            obj.select_set(True)
            prepped_meshes.append(obj)
    mesh_helpers.center_meshes_on_floor(context, prepped_meshes)

    # re-hide the prepped collection from the viewport if necessary
    layer_collection.hide_viewport = original_layer_visibility


class RUSHHOURVP_OT_prepare_vehicle_for_unreal(bpy.types.Operator):
    """Prepares the vehicle for unreal.
     - Duplicates and merges meshes, material slots, etc.
     - Takes measurements for all parts."""
    bl_idname = "rushhourvp.prep_vehicle_for_unreal"
    bl_label = "Prepare Vehicle For Unreal"

    def execute(self, context):
        prep_vehicle_process(context)
        return {'FINISHED'}


def register():
    print("Registering UE4 Vehicle prep operator")
    bpy.utils.register_class(RUSHHOURVP_OT_prepare_vehicle_for_unreal)


def unregister():
    print("Un-Registering UE4 Vehicle prep operator")
    bpy.utils.unregister_class(RUSHHOURVP_OT_prepare_vehicle_for_unreal)


if __name__ == "__main__":
    register()
