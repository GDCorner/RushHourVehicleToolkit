# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy
from ..utils import collection_helpers


class RUSHHOURVP_OT_show_object_bounds(bpy.types.Operator):
    """UV Operator description"""
    bl_idname = "rushhourvp.show_object_bounds"
    bl_label = "Show Object Bounds"

    show_bounds: bpy.props.BoolProperty(
        name='show',
        default=True
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        for obj in bpy.context.scene.objects:
            obj.show_bounds = self.show_bounds

        return {'FINISHED'}


def register():
    print("Registering show object bounds operator")
    bpy.utils.register_class(RUSHHOURVP_OT_show_object_bounds)


def unregister():
    print("Un-Registering show object bounds operator")
    bpy.utils.unregister_class(RUSHHOURVP_OT_show_object_bounds)


if __name__ == "__main__":
    register()
