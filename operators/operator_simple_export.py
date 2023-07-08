# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy

import logging

log = logging.getLogger(__name__)

class RUSHHOURVP_OT_simple_export_vehicle(bpy.types.Operator):
    """Simple Vehicle Export
This operator automatically runs the Prep, Rig and Export operators from the Rush Hour Vehicle Toolkit addon"""
    bl_idname = "rushhourvp.export_vehicle_simple"
    bl_label = "Simple Export RH Vehicle"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        #prep
        bpy.ops.rushhourvp.prep_vehicle_for_unreal()
        #rig
        bpy.ops.rushhourvp.rig_vehicle()
        #export
        bpy.ops.rushhourvp.export_ue_vehicle_fbx()

        # Hide rigged and prepped collections
        #bpy.data.collections["export"].hide_viewport = True
        #bpy.data.collections["prepped"].hide_viewport = True

        view_layer = bpy.context.view_layer
        export_layer_collection = view_layer.layer_collection.children['export']
        export_layer_collection.hide_viewport = True
        prepped_layer_collection = view_layer.layer_collection.children['prepped']
        prepped_layer_collection.hide_viewport = True
        return {'FINISHED'}


def register():
    print("Registering rush hour simple export operator")
    bpy.utils.register_class(RUSHHOURVP_OT_simple_export_vehicle)

def unregister():
    print("Un-Registering rush hour simple export operator")
    bpy.utils.unregister_class(RUSHHOURVP_OT_simple_export_vehicle)


if __name__ == "__main__":
    register()
