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
        try:
            bpy.ops.rushhourvp.prep_vehicle_for_unreal()
        except RuntimeError as ex:
            log.error(f"Error while prepping vehicle: {ex}")
            self.report({'ERROR'}, f"Error while prepping vehicle: {ex}")
            return {'CANCELLED'}

        #rig
        try:
            bpy.ops.rushhourvp.rig_vehicle(decimate_proxy_mesh=True, decimate_amount=0.5)
        except RuntimeError as ex:
            log.error(f"Error while rigging vehicle: {ex}")
            return {'CANCELLED'}

        #export
        try:
            bpy.ops.rushhourvp.export_ue_vehicle_fbx()
        except RuntimeError as ex:
            log.error(f"Error while exporting vehicle: {ex}")
            return {'CANCELLED'}

        # Hide rigged and prepped collections
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
