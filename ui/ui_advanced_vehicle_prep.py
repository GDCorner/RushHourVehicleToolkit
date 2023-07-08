# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy


class RUSHHOURVP_PT_advanced_vehicle_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Rush Hour Advanced Vehicle Prep"
    bl_idname = "RUSHHOURVP_PT_advanced_vehicle_panel"
    bl_category = "Rush Hour Unreal Vehicle"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_parent_id = "RUSHHOURVP_PT_rush_hour_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Create Standard Collections", icon='WORLD_DATA')
        row = layout.row()
        row.prop(context.scene, "axle_count")
        row = layout.row()
        vehicle_col_op = row.operator("rushhourvp.create_vehicle_collections", text="Create Standard Collections")
        vehicle_col_op.axle_count = context.scene.axle_count

        layout.separator(factor=2)

        row = layout.row()
        row.label(text="Setup Scene", icon='WORLD_DATA')
        row = layout.row()
        row.operator("rushhourvp.set_scene_cm_scale", text="Setup Scene Scale")
        row = layout.row()
        row.operator("rushhourvp.center_vehicle", text="Center Vehicle")
        row = layout.row()
        show_bounds_true = row.operator("rushhourvp.show_object_bounds", text="Show Bounds")
        show_bounds_true.show_bounds = True
        show_bounds_false = row.operator("rushhourvp.show_object_bounds", text="Hide Bounds")
        show_bounds_false.show_bounds = False

        layout.separator(factor=2)
        row = layout.row()
        row.label(text="Prep Vehicle", icon='WORLD_DATA')
        row = layout.row()
        row.operator("rushhourvp.prep_vehicle_for_unreal", text="Prepare Vehicle for Unreal")

        layout.separator(factor=2)
        row = layout.row()
        row.label(text="Rig Vehicle", icon='WORLD_DATA')


        row = layout.row()
        row.prop(context.scene, "rh_decimate_proxy_mesh")
        row = layout.row()
        row.prop(context.scene, "rh_decimate_amount")
        row = layout.row()
        rig_op = row.operator("rushhourvp.rig_vehicle", text="Rig Vehicle For Export")
        rig_op.decimate_proxy_mesh = context.scene.rh_decimate_proxy_mesh
        rig_op.decimate_amount = context.scene.rh_decimate_amount

        layout.separator(factor=2)

        row = layout.row()
        row.label(text="Export", icon='WORLD_DATA')

        row = layout.row()
        row.operator("rushhourvp.export_ue_vehicle_fbx", text="Export Prepped Vehicle")


def register():
    print("Registering UE4 Vehicle Exporter UI")
    bpy.utils.register_class(RUSHHOURVP_PT_advanced_vehicle_panel)


def unregister():
    print("Un-Registering UE4 Vehicle Exporter UI")
    bpy.utils.unregister_class(RUSHHOURVP_PT_advanced_vehicle_panel)


if __name__ == "__main__":
    register()
