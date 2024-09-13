# Copyright © 2024 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import math
import bpy
import bmesh
import mathutils

from . import math_helpers


# Calculates the size of the area for the UVs of a single polygon
def get_uv_area_for_poly(poly, uv_layer):
    if len(poly.loop_indices) < 3:
        print("Warning: Polygon less than 3 sides detected, this mesh may produce inaccurate scaling")
        # A single sided polygon has no area
        return 0
    elif len(poly.loop_indices) == 3:
        val = math_helpers.triangle_area([uv_layer[i].uv for i in poly.loop_indices])
        if not math.isnan(val):
            return val
    else:
        # This supports quads and ngons, but warns for ngons
        if len(poly.loop_indices) > 4:
            # print(
            #    "Warning! Only quads or tris are fully supported, complex n-gons may produce incorrect area calculations")
            pass
        val = math_helpers.ngon_area([uv_layer[i].uv for i in poly.loop_indices])
        if not math.isnan(val):
            return val
    # If we get here, we have a polygon with an invalid area
    print("Warning: Polygon with invalid area detected, this mesh may produce inaccurate scaling")
    return 0


# calculates the total size of the UV area with usage of code
# from the below source, obtained under the GPL license
# https://github.com/amb/blender-scripts/blob/master/uv_area.py
def get_uv_area(curr_object):
    uv_layer = curr_object.data.uv_layers.active.data

    total_area = 0.0
    for poly in curr_object.data.polygons:
        total_area += get_uv_area_for_poly(poly, uv_layer)

    return total_area


# calculates the total size of the UV area for a given set of faces
# with usage of code from the below source, obtained under the GPL license
# https://github.com/amb/blender-scripts/blob/master/uv_area.py
def get_uv_area_for_island(curr_object, island_polys):
    uv_layer = curr_object.data.uv_layers.active.data

    total_area = 0.0
    for face_idx in island_polys:
        poly = curr_object.data.polygons[face_idx]
        total_area += get_uv_area_for_poly(poly, uv_layer)

    return total_area


def scale_uvs_object(curr_object, scale_factor):
    uv_layer = curr_object.data.uv_layers.active.data
    centerOffset = mathutils.Vector(((0.5 * scale_factor), (0.5 * scale_factor)))
    for poly in curr_object.data.polygons:
        for loop_idx in poly.loop_indices:
            uv_layer[loop_idx].uv = (uv_layer[loop_idx].uv * scale_factor) - centerOffset


def scale_uvs_island(curr_object, face_list, scale_factor):
    uv_layer = curr_object.data.uv_layers.active.data
    for face_idx in face_list:
        poly = curr_object.data.polygons[face_idx]
        for loop_idx in poly.loop_indices:
            uv_layer[loop_idx].uv = uv_layer[loop_idx].uv * scale_factor


def get_uv_islands(curr_object: bpy.types.Object):
    # create used_faces set
    used_faces = set()
    # create list of face sets
    islands = []

    mesh_data: bpy.types.Mesh = curr_object.data
    uv_layer: bpy.types.MeshUVLoopLayer = mesh_data.uv_layers.active
    uv_layer_data: bpy.types.MeshUVLoopLayer = mesh_data.uv_layers.active.data

    # Change to edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    # unselect all
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.uv.select(deselect_all=True)

    # create a bmesh
    bm: bmesh.types.BMesh = bmesh.from_edit_mesh(mesh_data)
    bm_uv_layer = bm.loops.layers.uv.verify()

    # for each face
    for face_idx, face in enumerate(bm.faces):
        # skip faces that are already in an existing island
        if face_idx in used_faces:
            continue

        face.select = True

        # update the mesh in blender with the new selection
        bmesh.update_edit_mesh(mesh_data)
        # select linked using blender operator
        bpy.ops.uv.select_linked()

        # build a set of all selected faces
        new_island = set()
        for face_idx2, bm_face2 in enumerate(bm.faces):
            if bm_face2.select:
                new_island.add(face_idx2)

        unique_island = True
        for existing_island in islands:
            if len(new_island.difference(existing_island)) == 0:
                print("Existing island - You probably don't want to see this. Something may have gone wrong")
                unique_island = False

        if unique_island:
            # store this as an island
            islands.append(new_island)
            # add all faces to global used faces set
            used_faces.update(new_island)

        # unselect faces in uv island
        face.select = False
        for selected_face_idx in new_island:
            bm.faces[selected_face_idx].select = False

    return islands


def register():
    pass


def unregister():
    pass
