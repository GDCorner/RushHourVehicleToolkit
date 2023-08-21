# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bmesh
import bpy
import array
import logging

from mathutils import Vector
from . import message_helpers


# Copies a bmesh from an object
# Copied under GPL from:
# https://developer.blender.org/diffusion/BA/browse/master/object_print3d_utils/mesh_helpers.py
def bmesh_copy_from_object(obj, transform=True, triangulate=True, apply_modifiers=False):
    """Returns a transformed, triangulated copy of the mesh"""

    assert obj.type == 'MESH'

    if apply_modifiers and obj.modifiers:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(depsgraph)
        me = obj_eval.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(me)
        obj_eval.to_mesh_clear()
    else:
        me = obj.data
        if obj.mode == 'EDIT':
            bm_orig = bmesh.from_edit_mesh(me)
            bm = bm_orig.copy()
        else:
            bm = bmesh.new()
            bm.from_mesh(me)

    # TODO. remove all customdata layers.
    # would save ram

    if transform:
        bm.transform(obj.matrix_world)

    if triangulate:
        bmesh.ops.triangulate(bm, faces=bm.faces)

    return bm


# Calculates the area of a bmesh
# Copied under GPL from:
# https://developer.blender.org/diffusion/BA/browse/master/object_print3d_utils/mesh_helpers.py
def bmesh_calc_area(bm):
    """Calculate the surface area."""
    return sum(f.calc_area() for f in bm.faces)


# Calculates the area of specific faces in a bmesh
# Adapted under GPL from:
# https://developer.blender.org/diffusion/BA/browse/master/object_print3d_utils/mesh_helpers.py
def bmesh_calc_area_of_faces(bm, face_list):
    """Calculate the surface area."""
    if hasattr(bm.faces, "ensure_lookup_table"):
        bm.faces.ensure_lookup_table()
    faces = [bm.faces[i] for i in face_list]
    return sum(f.calc_area() for f in faces)


def get_surface_area_of_mesh(curr_object, apply_scaling=False):
    face_total_world_area = 0

    if apply_scaling == False:
        for face_idx in range(len(curr_object.data.polygons)):
            face_total_world_area += curr_object.data.polygons[face_idx].area
    else:
        bm = bmesh_copy_from_object(curr_object, apply_modifiers=False, triangulate=False)
        face_total_world_area = bmesh_calc_area(bm)
        bm.free()

    return face_total_world_area


def get_surface_area_of_faces_from_mesh(curr_object, face_list, apply_scaling=False):
    face_total_world_area = 0

    if apply_scaling == False:
        for face_idx in face_list:
            face_total_world_area += curr_object.data.polygons[face_idx].area
    else:
        bm = bmesh_copy_from_object(curr_object, apply_modifiers=False, triangulate=False)
        face_total_world_area = bmesh_calc_area_of_faces(bm, face_list)
        bm.free()

    return face_total_world_area


def apply_all_transforms(context, meshes):
    # Apply all transforms to selected object
    bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes:
        obj.select_set(True)
        context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        obj.select_set(False)

def apply_all_modifiers(context, meshes):
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    # bpy.ops.object.apply_all_modifiers()
    for ob in meshes:
        ob.select_set(True)
        context.view_layer.objects.active = ob
        for mod in ob.modifiers:
            try:
                bpy.ops.object.modifier_apply(modifier=mod.name)
            except:
                # Modifier is likely disabled, remove it
                logging.log(logging.ERROR, f'Unable to apply modifier. Likely disable, deleting it instead. OBJ: {ob.name}, MOD: {mod.name}')
                bpy.ops.object.modifier_remove(modifier=mod.name)
        ob.select_set(False)


# https://github.com/Aadjou/blender-scripts/blob/master/utils_split_normals.py
# No explicit license, but all source that uses blender APIs must be GPL compatible licenses.
def apply_split_normals(obj):
    # Write the blender internal smoothing as custom split vertex normals
    me = obj.data
    me.calc_normals_split()
    cl_nors = array.array('f', [0.0] * (len(me.loops) * 3))
    me.loops.foreach_get('normal', cl_nors)
    # me.polygons.foreach_set('use_smooth', [False] * len(me.polygons))
    nors_split_set = tuple(zip(*(iter(cl_nors),) * 3))
    me.normals_split_custom_set(nors_split_set)
    # Enable the use custom split normals data
    me.use_auto_smooth = True


def fix_negative_scales(objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(False)

    # Force selection update
    bpy.context.view_layer.update()
    for obj in objects:
        if obj.scale.x < 0 or obj.scale.y < 0 or obj.scale.z < 0:
            obj.select_set(True)
            # Show warning dialog to user
            message_helpers.show_warning_message(
                message="Negative scale detected on object: " + obj.name + ". Negative scales can produce unexpected results. Recommend removing or fixing the negative scale before prep process",
                title="Negative Scale Detected")

            # Apply the scale operator
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

            # Flip the normals on the mesh
            if obj.data:
                obj.data.flip_normals()
            obj.select_set(False)


def remove_blank_materials(objects):
    # Blank material slots on meshes causes issues when importing an FBX into unreal, causing all kinds of material reassignment chaos
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        for slot in obj.material_slots:
            if slot.material is None:
                message_helpers.show_warning_message(
                    message="Blank material slot on object: " + obj.name + ". Blank material slots can cause material assignment issues in Unreal",
                    title="Blank Material Slot Detected")
                obj.active_material_index = obj.material_slots.find(slot.name)
                bpy.ops.object.material_slot_remove({'object': obj})


def get_bounds_of_meshes(meshes):
    # Open for writing and append

    # Get the bounds of all meshes
    xs = [(mesh.matrix_world @ Vector(vert))[0] for mesh in meshes for vert in mesh.bound_box]
    ys = [(mesh.matrix_world @ Vector(vert))[1] for mesh in meshes for vert in mesh.bound_box]
    zs = [(mesh.matrix_world @ Vector(vert))[2] for mesh in meshes for vert in mesh.bound_box]

    min_x = min(xs)
    max_x = max(xs)
    min_y = min(ys)
    max_y = max(ys)
    min_z = min(zs)
    max_z = max(zs)

    absolute_bounds = ((min_x, min_y, min_z), (max_x, max_y, max_z))

    return absolute_bounds


def get_x_size_of_bounds(bounds):
    return bounds[1][0] - bounds[0][0]


def get_y_size_of_bounds(bounds):
    return bounds[1][1] - bounds[0][1]


def get_z_size_of_bounds(bounds):
    return bounds[1][2] - bounds[0][2]


def get_center_of_meshes(meshes):
    bounds = get_bounds_of_meshes(meshes)
    min_vert = bounds[0]
    max_vert = bounds[1]

    bb_center = ((min_vert[0] + max_vert[0]) / 2, (min_vert[1] + max_vert[1]) / 2, (min_vert[2] + max_vert[2]) / 2)
    return bb_center

def center_meshes_on_floor(context, meshes):
    """Centers the meshes on the floor. Assumes the floor is at Z=0"""
    bounds = get_bounds_of_meshes(meshes)
    min_vert = bounds[0]
    max_vert = bounds[1]

    bb_center = ((min_vert[0] + max_vert[0]) / 2, (min_vert[1] + max_vert[1]) / 2, (min_vert[2] + max_vert[2]) / 2)
    height = max_vert[2] - min_vert[2]

    # invert the bb location and add on half the height on the Z axis
    negative_location = Vector((-bb_center[0], -bb_center[1], -(bb_center[2]) + (height / 2)))

    # Move objects by negative_location
    for mesh in meshes:
        mesh.location += negative_location


def delete_vertices_with_no_faces(mesh):
    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = mesh

    bpy.ops.object.mode_set(mode='EDIT')

    # Select all vertices with no faces
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_loose()
    bpy.ops.mesh.delete(type='VERT')

    bpy.ops.object.mode_set(mode='OBJECT')


def delete_vertices_with_no_faces_from_meshes(meshes):
    for mesh in meshes:
        delete_vertices_with_no_faces(mesh)


def register():
    pass


def unregister():
    pass
