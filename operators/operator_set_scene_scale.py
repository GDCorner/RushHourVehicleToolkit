# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy
import math

from ..utils import message_helpers


def set_scene_scale_to_cm(context):
    # Set the scene unit to meters and set the unit scale to 0.01
    was_scene_default_metre_scale = False
    if bpy.context.scene.unit_settings.system == 'METRIC' and \
            math.isclose(bpy.context.scene.unit_settings.scale_length, 1.0, rel_tol=1e-07):
        was_scene_default_metre_scale = True

    was_scene_already_cm_scale = False
    if bpy.context.scene.unit_settings.system == 'METRIC' and \
            math.isclose(bpy.context.scene.unit_settings.scale_length, 0.01, rel_tol=1e-07):
        was_scene_already_cm_scale = True

    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 0.01

    if was_scene_default_metre_scale is False and was_scene_already_cm_scale is False:
        print(
            "Warning: Scene unit scale was not set to meters, so existing objects will not be scaled to the new unit "
            "scale. You may need to manually rescale objects in the scene to the new unit scale.")
        message_helpers.show_warning_message(
            "Warning: Scene unit scale was not set to meters, so existing objects will not be scaled to the new unit "
            "scale. You may need to manually rescale objects in the scene to the new unit scale.")
    if was_scene_already_cm_scale:
        print("Scene is already the correct scale. No changes made.")
        message_helpers.show_info_message("Scene is already the correct scale. No changes made.")

    if was_scene_already_cm_scale is False and was_scene_default_metre_scale is True:
        # Rescale all objects in the scene to the new unit scale
        for obj in bpy.data.objects:
            # if object has a parent, skip it, as the scale will flow down
            if obj.parent is not None:
                continue
            # get existing object scale
            obj_scale = obj.scale
            # multiply object scale by 100 to convert to cm
            obj.scale = (obj_scale[0] * 100, obj_scale[1] * 100, obj_scale[2] * 100)
            # multiply object position by 100 to convert to cm
            obj.location = (obj.location[0] * 100, obj.location[1] * 100, obj.location[2] * 100)

        # Set the clip end difference to 1cm and 1000m
        bpy.context.space_data.clip_start = 1.0
        bpy.context.space_data.clip_end = 1000.0 * 100.0


def move_viewport_to_car():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.view3d.view_selected()
    bpy.ops.object.select_all(action='DESELECT')


class RUSHHOURVP_OT_set_scene_cm_scale(bpy.types.Operator):
    """Set Scene scale for Unreal. Rescales objects if scene was in default scale."""
    bl_idname = "rushhourvp.set_scene_cm_scale"
    bl_label = "Set the scene to centimeter scale"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        set_scene_scale_to_cm(context)
        move_viewport_to_car()
        return {'FINISHED'}


def register():
    print("Registering Set Scene CM Scale operator")
    bpy.utils.register_class(RUSHHOURVP_OT_set_scene_cm_scale)


def unregister():
    print("Un-Registering Set Scene CM Scale operator")
    bpy.utils.unregister_class(RUSHHOURVP_OT_set_scene_cm_scale)
