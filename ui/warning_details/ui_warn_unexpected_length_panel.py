# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy

from ...utils.ui_helpers import label_multiline


class RUSHHOURVP_PT_warn_unexpected_vehicle_length_panel(bpy.types.Panel):
    """Creates a Panel to warn about wrong_facing of vehicle"""
    bl_label = "Unexpected Vehicle Length"
    bl_idname = "RUSHHOURVP_PT_warn_unexpected_vehicle_length_panel"
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
        safe_length = context.scene.vehicle_checks.has_safe_length
        return not safe_length

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='ERROR')

    def draw(self, context):
        layout: bpy.types.UILayout = self.layout.box()
        # get the width of the layout in pixels

        row = layout.row()
        row.label(text="Unexpected Vehicle Length", icon='ERROR')
        row = layout.row()
        length = context.scene.vehicle_checks.vehicle_length
        length_text = f'{(length / 100):.2f}'
        description_text = f'The vehicle is currently {length_text}m long. Typically vehicles are within 2m to 20m in length depending on type. Make sure the vehicle is the correct size.'
        label_multiline(
            context=context,
            text=description_text,
            parent=layout
        )

        row = layout.row()
        row = layout.row()

        warning_text = "This is only a warning, you can proceed anyway. This is just a quick sanity check in case you forgot to scale the vehicle. If you're sure the vehicle is the correct size, you can ignore this warning. However the templates in Rush Hour may not be appropriately configured for a vehicle of this size."
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
    bpy.utils.register_class(RUSHHOURVP_PT_warn_unexpected_vehicle_length_panel)


def unregister():
    print("Un-Registering Nanite Material Warning Panel UI")
    bpy.utils.unregister_class(RUSHHOURVP_PT_warn_unexpected_vehicle_length_panel)


if __name__ == "__main__":
    register()
