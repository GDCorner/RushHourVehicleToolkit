# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy

import logging

log = logging.getLogger(__name__)


class RUSHHOURVP_OT_simple_prepare_scene(bpy.types.Operator):
    """Simple Prepare Scene
This operator automatically creates the necessary collections and sets the scene scale for the Rush Hour Vehicle Toolkit addon"""
    bl_idname = "rushhourvp.prepare_scene_simple"
    bl_label = "Simple Prepare Scene for Rush Hour Vehicles"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        # Create collections
        bpy.ops.rushhourvp.create_vehicle_collections(axle_count=2)
        # Set scene scale
        bpy.ops.rushhourvp.set_scene_cm_scale()
        return {'FINISHED'}


def register():
    print("Registering rush hour simple export operator")
    bpy.utils.register_class(RUSHHOURVP_OT_simple_prepare_scene)


def unregister():
    print("Un-Registering rush hour simple export operator")
    bpy.utils.unregister_class(RUSHHOURVP_OT_simple_prepare_scene)


if __name__ == "__main__":
    register()
