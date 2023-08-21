# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy

from ...utils.ui_helpers import label_multiline

from ...utils.vehicle_checks import has_no_negative_scales, is_vehicle_prepped


class RUSHHOURVP_PT_warn_negative_scales_panel(bpy.types.Panel):
    """Creates a Panel to warn about wrong_facing of vehicle"""
    bl_label = "Meshes with Negative Scales"
    bl_idname = "RUSHHOURVP_PT_warn_negative_scales_panel"
    bl_category = "Rush Hour Unreal Vehicle"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Warnings'
    bl_parent_id = "RUSHHOURVP_PT_prep_warnings_panel"
    bl_options = {'DEFAULT_CLOSED'}
    bl_icon = 'ERROR'

    @classmethod
    def poll(cls, context):
        negative_scales = has_no_negative_scales()
        return not negative_scales

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='ERROR')

    def draw(self, context):
        layout: bpy.types.UILayout = self.layout.box()
        # get the width of the layout in pixels

        row = layout.row()
        row.label(text="Meshes have negative scales", icon='ERROR')
        row = layout.row()
        description_text = "Some meshes have a negative scale. The toolkit tries to compensate but it can lead to errors. Negative scales lead to inverted normals which appears as missing geometry or 'inside-out' meshes in Unreal. The best thing to do is apply all transforms on the meshes with negative scales, and check the 'face orientation' overlay to visualise any inverted normals."
        label_multiline(
            context=context,
            text=description_text,
            parent=layout
        )

        row = layout.row()
        row = layout.row()

        warning_text = "This is only a warning, you can proceed anyway but be aware of visual artifacts in Unreal."
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
    bpy.utils.register_class(RUSHHOURVP_PT_warn_negative_scales_panel)


def unregister():
    print("Un-Registering Nanite Material Warning Panel UI")
    bpy.utils.unregister_class(RUSHHOURVP_PT_warn_negative_scales_panel)


if __name__ == "__main__":
    register()
