# Copyright © 2024 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy


class RUSHHOURVP_PT_object_auto_uv_properties_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window to show current AutoUV properties"""
    bl_label = "Auto UV"
    bl_idname = "RUSHHOURVP_PT_auto_uv_properties_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="Active object is: " + obj.name)
        row = layout.row()
        row.prop(obj, "enable_auto_uv")


def register():
    print("Registering Auto UV Details Panel")
    bpy.utils.register_class(RUSHHOURVP_PT_object_auto_uv_properties_panel)


def unregister():
    print("Un-Registering Auto UV Details Panel")
    bpy.utils.unregister_class(RUSHHOURVP_PT_object_auto_uv_properties_panel)


if __name__ == "__main__":
    register()
