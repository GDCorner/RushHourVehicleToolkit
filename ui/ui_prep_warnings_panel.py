# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy


class RUSHHOURVP_PT_prep_warnings_panel(bpy.types.Panel):
    """Creates a Panel to display warnings about the vehicle preparation"""
    bl_label = "Warnings/Errrors"
    bl_idname = "RUSHHOURVP_PT_prep_warnings_panel"
    bl_category = "Rush Hour Unreal Vehicle"
    bl_space_type = 'VIEW_3D'
    bl_parent_id = "RUSHHOURVP_PT_rush_hour_panel"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="None at this time", icon='WORLD_DATA')


def register():
    print("Registering Prep Warnings Panel UI")
    bpy.utils.register_class(RUSHHOURVP_PT_prep_warnings_panel)


def unregister():
    print("Un-Registering Prep Warnings Panel UI")
    bpy.utils.unregister_class(RUSHHOURVP_PT_prep_warnings_panel)


if __name__ == "__main__":
    register()
