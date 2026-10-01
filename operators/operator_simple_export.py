# Copyright © 2024-2026 GDCorner
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
        try:
            bpy.ops.rushhourvp.prep_vehicle_for_unreal('EXEC_DEFAULT')
        except RuntimeError as ex:
            log.error(f"Vehicle prep was cancelled: {ex}")
            return {'FINISHED'}

        #rig
        try:
            bpy.ops.rushhourvp.rig_vehicle('EXEC_DEFAULT', decimate_proxy_mesh=True, decimate_amount=0.5)
        except RuntimeError as ex:
            log.error(f"Vehicle rig was cancelled: {ex}")
            return {'FINISHED'}

        #export
        try:
            bpy.ops.rushhourvp.export_ue_vehicle_fbx('EXEC_DEFAULT')
        except RuntimeError as ex:
            log.error(f"Vehicle export was cancelled: {ex}")
            return {'FINISHED'}

        # Hide rigged and prepped collections
        view_layer = bpy.context.view_layer
        export_layer_collection = view_layer.layer_collection.children['export']
        export_layer_collection.hide_viewport = True
        prepped_layer_collection = view_layer.layer_collection.children['prepped']
        prepped_layer_collection.hide_viewport = True

        bpy.ops.rushhourvp.check_vehicle()
        return {'FINISHED'}


def register():
    print("Registering rush hour simple export operator")
    bpy.utils.register_class(RUSHHOURVP_OT_simple_export_vehicle)


def unregister():
    print("Un-Registering rush hour simple export operator")
    bpy.utils.unregister_class(RUSHHOURVP_OT_simple_export_vehicle)


if __name__ == "__main__":
    register()
