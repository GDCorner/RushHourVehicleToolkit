# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy

from ...utils.ui_helpers import label_multiline

from ...utils.vehicle_checks import is_vehicle_facing_correct_direction, is_vehicle_prepped


class RUSHHOURVP_PT_warn_wrong_facing_panel(bpy.types.Panel):
    """Creates a Panel to warn about wrong_facing of vehicle"""
    bl_label = "Facing Wrong Direction"
    bl_idname = "RUSHHOURVP_PT_warn_wrong_facing_panel"
    bl_category = "Rush Hour Unreal Vehicle"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Warnings'
    bl_parent_id = "RUSHHOURVP_PT_prep_warnings_panel"
    bl_options = {'DEFAULT_CLOSED'}
    bl_icon = 'ERROR'

    @classmethod
    def poll(cls, context):
        if context.scene.vehicle_checks.is_vehicle_prepped is False:
            return False
        vehicle_facing = context.scene.vehicle_checks.is_vehicle_facing_correct_direction
        return not vehicle_facing

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='ERROR')

    def draw(self, context):
        layout: bpy.types.UILayout = self.layout.box()
        # get the width of the layout in pixels

        row = layout.row()
        row.label(text="Vehicle Facing Wrong Direction", icon='ERROR')
        row = layout.row()
        description_text = "The vehicle appears to be facing the wrong direction. Make sure it's facing the positive X axis with the positive Y axis pointing to the left."
        label_multiline(
            context=context,
            text=description_text,
            parent=layout
        )

        row = layout.row()
        row = layout.row()

        warning_text = "This is only a warning, you can proceed anyway. The test checks the dot product of the wheels on axle 0. In some circumstances this may produce an inaccurate warning"
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
    bpy.utils.register_class(RUSHHOURVP_PT_warn_wrong_facing_panel)


def unregister():
    print("Un-Registering Nanite Material Warning Panel UI")
    bpy.utils.unregister_class(RUSHHOURVP_PT_warn_wrong_facing_panel)


if __name__ == "__main__":
    register()
