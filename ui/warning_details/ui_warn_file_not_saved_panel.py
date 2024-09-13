# Copyright © 2024 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy

from ...utils.ui_helpers import label_multiline


class RUSHHOURVP_PT_warn_file_not_saved_panel(bpy.types.Panel):
    """Creates a Panel to warn about wrong_facing of vehicle"""
    bl_label = "File Not Saved"
    bl_idname = "RUSHHOURVP_PT_warn_file_not_saved_panel"
    bl_category = "Rush Hour Unreal Vehicle"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Warnings'
    bl_parent_id = "RUSHHOURVP_PT_prep_warnings_panel"
    bl_options = {'DEFAULT_CLOSED'}
    bl_icon = 'ERROR'

    @classmethod
    def poll(cls, context):
        return len(bpy.data.filepath) == 0

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='ERROR')

    def draw(self, context):
        layout: bpy.types.UILayout = self.layout.box()
        # get the width of the layout in pixels

        row = layout.row()
        row.label(text="File Not Saved", icon='ERROR')
        row = layout.row()
        description_text = "The file has not yet been saved. Export will fail."
        label_multiline(
            context=context,
            text=description_text,
            parent=layout
        )


def register():
    print("Registering Nanite Material Warning Panel UI")
    bpy.utils.register_class(RUSHHOURVP_PT_warn_file_not_saved_panel)


def unregister():
    print("Un-Registering Nanite Material Warning Panel UI")
    bpy.utils.unregister_class(RUSHHOURVP_PT_warn_file_not_saved_panel)


if __name__ == "__main__":
    register()
