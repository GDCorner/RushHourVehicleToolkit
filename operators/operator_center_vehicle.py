# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy
from ..utils import mesh_helpers


def center_vehicle(context):
    # Deselect everything
    bpy.ops.object.select_all(action='DESELECT')

    vehicle_collection = bpy.data.collections['vehicle']

    # get all meshes under all collections within vehicle_collection
    meshes = []
    for obj in vehicle_collection.all_objects:
        if obj.type == 'MESH':
            obj.select_set(True)
            meshes.append(obj)

    mesh_helpers.center_meshes_on_floor(context, meshes)


class RUSHHOURVP_OT_center_vehicle(bpy.types.Operator):
    bl_idname = "rushhourvp.center_vehicle"
    bl_label = "Center Vehicle"

    def execute(self, context):
        center_vehicle(context)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(RUSHHOURVP_OT_center_vehicle)


def unregister():
    bpy.utils.unregister_class(RUSHHOURVP_OT_center_vehicle)
