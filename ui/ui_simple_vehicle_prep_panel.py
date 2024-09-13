# Copyright © 2024 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy


class RUSHHOURVP_PT_simple_vehicle_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Simple Vehicle Prep"
    bl_idname = "RUSHHOURVP_PT_simple_vehicle_panel"
    bl_category = "Rush Hour Unreal Vehicle"
    bl_space_type = 'VIEW_3D'
    bl_parent_id = "RUSHHOURVP_PT_rush_hour_panel"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Prep Scene", icon='WORLD_DATA')
        row = layout.row()
        # Create collections
        # Set scene scale
        vehicle_col_op = row.operator("rushhourvp.prepare_scene_simple", text="Prepare Scene")

        layout.separator(factor=2)
        row = layout.row()
        row.label(text="Setup Vehicle", icon='WORLD_DATA')
        row = layout.row()
        # Get selected meshes
        # - Apply transforms
        # - Clear parents
        # - Add body collection
        add_to_body_op = row.operator("rushhourvp.add_selected_to_vehicle_collection", text="Add To Body")
        add_to_body_op.collection_name = "body"
        row = layout.row()
        add_to_fl_wheel_op = row.operator("rushhourvp.add_selected_to_vehicle_collection", text="Add To FL Wheel")
        add_to_fl_wheel_op.collection_name = "wheel_0_L"
        add_to_fr_wheel_op = row.operator("rushhourvp.add_selected_to_vehicle_collection", text="Add To FR Wheel")
        add_to_fr_wheel_op.collection_name = "wheel_0_R"
        row = layout.row()
        add_to_rl_wheel_op = row.operator("rushhourvp.add_selected_to_vehicle_collection", text="Add To RL Wheel")
        add_to_rl_wheel_op.collection_name = "wheel_1_L"
        add_to_rr_wheel_op = row.operator("rushhourvp.add_selected_to_vehicle_collection", text="Add To RR Wheel")
        add_to_rr_wheel_op.collection_name = "wheel_1_R"
        row = layout.row()


        layout.separator(factor=2)
        row = layout.row()
        row.label(text="Export", icon='WORLD_DATA')
        row = layout.row()
        # Prep
        # Rig
        # Export
        row.operator("rushhourvp.export_vehicle_simple", text="Export Vehicle - Simple")


def register():
    print("Registering UE4 Vehicle Exporter UI")
    bpy.utils.register_class(RUSHHOURVP_PT_simple_vehicle_panel)


def unregister():
    print("Un-Registering UE4 Vehicle Exporter UI")
    bpy.utils.unregister_class(RUSHHOURVP_PT_simple_vehicle_panel)


if __name__ == "__main__":
    register()
