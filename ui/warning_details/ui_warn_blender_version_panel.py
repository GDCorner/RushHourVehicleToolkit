# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy

from ...utils.ui_helpers import label_multiline
from ... import rhvtinfo


class RUSHHOURVP_PT_warn_blender_version_panel(bpy.types.Panel):
    """Creates a Panel to warn about incompatible blender versions"""
    bl_label = "Unsupported Blender Version"
    bl_idname = "RUSHHOURVP_PT_warn_blender_version_panel"
    bl_category = "Rush Hour Unreal Vehicle"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Warnings'
    bl_parent_id = "RUSHHOURVP_PT_prep_warnings_panel"
    bl_options = {'DEFAULT_CLOSED'}
    bl_icon = 'ERROR'

    @classmethod
    def poll(cls, context):
        should_draw = not rhvtinfo.is_supported_blender_version()
        return should_draw

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='ERROR')

    def draw(self, context):
        layout: bpy.types.UILayout = self.layout.box()
        # get the width of the layout in pixels

        row = layout.row()
        row.label(text="Unsupported Blender Version", icon='ERROR')
        row = layout.row()
        description_text = "Only LTS versions of Blender are supported. The version of Blender you are using has not been tested with the Rush Hour Vehicle Toolkit. The toolkit may not work as expected. Please check for a newer plugin version or use a supported Blender Version."
        label_multiline(
            context=context,
            text=description_text,
            parent=layout
        )

        row = layout.row()
        row = layout.row()

        warning_text = "This is only a warning, you can proceed anyway, but be aware that the toolkit may not work as expected."
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
    print("Registering Rush Hour Version Warning Panel UI")
    bpy.utils.register_class(RUSHHOURVP_PT_warn_blender_version_panel)


def unregister():
    print("Un-Registering Rush Hour Version Warning Panel UI")
    bpy.utils.unregister_class(RUSHHOURVP_PT_warn_blender_version_panel)


if __name__ == "__main__":
    register()
