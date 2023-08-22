# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy


def apply_transforms(context):
    bpy.ops.object.select_all(action='SELECT')
    # Apply transform for new object
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)
    bpy.ops.object.select_all(action='DESELECT')

def clear_parents(context):
    # Clear parents
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    bpy.ops.object.select_all(action='DESELECT')

class RUSHHOURVP_OT_clear_parents(bpy.types.Operator):
    """Clears object parents while preserving transform"""
    bl_idname = "rushhourvp.clear_parents"
    bl_label = "Clear Parents while keeping transform"

    def execute(self, context):
        # apply_transforms(context)
        clear_parents(context)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(RUSHHOURVP_OT_clear_parents)


def unregister():
    bpy.utils.unregister_class(RUSHHOURVP_OT_clear_parents)
