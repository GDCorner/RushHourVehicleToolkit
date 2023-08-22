# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy

from ...utils.ui_helpers import label_multiline


from ...utils.vehicle_checks import are_all_meshes_under_nanite_material_limit, is_vehicle_prepped


class RUSHHOURVP_PT_warn_exceed_nanite_material_panel(bpy.types.Panel):
    """Creates a Panel to warn about exceeding nanite materials"""
    bl_label = "Max Number of Nanite Materials"
    bl_idname = "RUSHHOURVP_PT_warn_exceed_nanite_material_panel"
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
        under_material_limit = context.scene.vehicle_checks.are_all_meshes_under_nanite_material_limit
        return not under_material_limit
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='ERROR')

    def draw(self, context):
        layout: bpy.types.UILayout = self.layout.box()
        # get the width of the layout in pixels

        row = layout.row()
        row.label(text="Max Number of Nanite Materials", icon='ERROR')
        row = layout.row()
        description_text = "Nanite can only support a maximum of 64 material slots per mesh. This is typically solved by sorting your geometry into the 'body' and 'body_interior' collections appropriately. Make use of all the additional collections available."
        label_multiline(
            context=context,
            text=description_text,
            parent=layout
        )

        row = layout.row()
        row = layout.row()

        warning_text = "This is only a warning, you can proceed anyway. Just make sure to uncheck 'Use Nanite' in the import options in Unreal."
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
    bpy.utils.register_class(RUSHHOURVP_PT_warn_exceed_nanite_material_panel)


def unregister():
    print("Un-Registering Nanite Material Warning Panel UI")
    bpy.utils.unregister_class(RUSHHOURVP_PT_warn_exceed_nanite_material_panel)


if __name__ == "__main__":
    register()
