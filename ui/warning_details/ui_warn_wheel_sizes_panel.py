# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy

from ...utils.ui_helpers import label_multiline

from ...utils.vehicle_checks import are_wheel_sizes_round, is_vehicle_prepped


class RUSHHOURVP_PT_warn_wheel_sizes_panel(bpy.types.Panel):
    """Creates a Panel to warn about wrong_facing of vehicle"""
    bl_label = "Odd Wheel Sizes"
    bl_idname = "RUSHHOURVP_PT_warn_wheel_sizes_panel"
    bl_category = "Rush Hour Unreal Vehicle"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Warnings'
    bl_parent_id = "RUSHHOURVP_PT_prep_warnings_panel"
    bl_options = {'DEFAULT_CLOSED'}
    bl_icon = 'ERROR'

    @classmethod
    def poll(cls, context):
        if is_vehicle_prepped() is False:
            return False
        wheels_round = are_wheel_sizes_round()
        return not wheels_round

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='ERROR')

    def draw(self, context):
        layout: bpy.types.UILayout = self.layout.box()
        # get the width of the layout in pixels

        row = layout.row()
        row.label(text="Odd Wheel Sizes", icon='ERROR')
        row = layout.row()
        description_text = "The wheels appear to have non-uniform sizes. Check all wheels are properly round, that all wheels are similar size and wheels don't have any camber\slant. Press 'Show Bounds' for help visualising the wheel sizes. This could also be because the vehicle is facing the wrong direction."
        label_multiline(
            context=context,
            text=description_text,
            parent=layout
        )

        row = layout.row()
        row = layout.row()

        warning_text = "This is only a warning, you can proceed anyway. Wheels that are not round may appear to wobble or warp when in motion. If your wheels are different sizes to each other this could lead to an unstable vehicle and will require a bit of attention in tuning the physical properties of the vehicle."
        label_multiline(
            context=context,
            text=warning_text,
            parent=layout
        )

        meshes = []
        for mesh in meshes:
            row = layout.row()
            row.label(text=f' - {mesh}', icon='NONE')


def register():
    print("Registering Nanite Material Warning Panel UI")
    bpy.utils.register_class(RUSHHOURVP_PT_warn_wheel_sizes_panel)


def unregister():
    print("Un-Registering Nanite Material Warning Panel UI")
    bpy.utils.unregister_class(RUSHHOURVP_PT_warn_wheel_sizes_panel)


if __name__ == "__main__":
    register()
