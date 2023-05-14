# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy


def enable_auto_uv_on_selected_objects(context, enable_auto_uv=True):
    for sel_object in bpy.context.selected_objects:
        sel_object.enable_auto_uv = enable_auto_uv


class RUSHHOURVP_OT_tag_objects_for_auto_uv(bpy.types.Operator):
    """UV Operator description"""
    bl_idname = "rushhourvp.tag_objects_for_auto_uv"
    bl_label = "Enable auto UV unwrap for the selected objects"

    enable_auto_uv: bpy.props.BoolProperty(
        name='enable_auto_uv',
        default=True
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.mode == 'OBJECT'

    def execute(self, context):
        enable_auto_uv_on_selected_objects(context, self.enable_auto_uv)
        return {'FINISHED'}


def menu_tag_disable_auto_uv(self, context):
    menu_item = self.layout.operator(RUSHHOURVP_OT_tag_objects_for_auto_uv.bl_idname, text="Disable Auto UV")
    menu_item.enable_auto_uv = False


def menu_tag_enable_auto_uv(self, context):
    menu_item = self.layout.operator(RUSHHOURVP_OT_tag_objects_for_auto_uv.bl_idname, text="Enable Auto UV")
    menu_item.enable_auto_uv = True


def register():
    print("Registering Auto UV Tag operator")
    bpy.utils.register_class(RUSHHOURVP_OT_tag_objects_for_auto_uv)
    bpy.types.VIEW3D_MT_object.append(menu_tag_enable_auto_uv)
    bpy.types.VIEW3D_MT_object.append(menu_tag_disable_auto_uv)
    bpy.types.Object.enable_auto_uv = bpy.props.BoolProperty(
        name="Enable Auto UV",
        default=False
    )


def unregister():
    print("Un-Registering Auto UV Tag operator")
    bpy.utils.unregister_class(RUSHHOURVP_OT_tag_objects_for_auto_uv)
    bpy.types.VIEW3D_MT_object.remove(menu_tag_enable_auto_uv)
    bpy.types.VIEW3D_MT_object.remove(menu_tag_disable_auto_uv)
    del bpy.types.Object.enable_auto_uv
