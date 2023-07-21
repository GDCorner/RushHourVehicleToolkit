# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy


class RUSHHOURVP_PT_rush_hour_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Rush Hour Vehicle Prep"
    bl_idname = "RUSHHOURVP_PT_rush_hour_panel"
    bl_category = "Rush Hour Unreal Vehicle"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout


def register():
    print("Registering Rush Hour Panel")
    bpy.utils.register_class(RUSHHOURVP_PT_rush_hour_panel)


def unregister():
    print("Un-Registering Rush Hour Panel")
    bpy.utils.unregister_class(RUSHHOURVP_PT_rush_hour_panel)


if __name__ == "__main__":
    register()