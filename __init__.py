# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

# <pep8 compliant>

import bpy
import sys
import importlib

bl_info = {
    "name": "Rush Hour Unreal Vehicle Toolkit",
    "description": "Provides utilities and functions to easily create, setup and export vehicles for Unreal Engine 5 and Rush Hour",
    "author": "Philip Edwards (GDCorner) <philip@gdcorner.com>",
    "version": (1, 4, 0),
    "blender": (2, 90, 0),
    "category": "Vehicles",
    "doc_url": "https://www.gdcorner.com",
}

modulesNames = [
    'utils.math_helpers',
    'utils.mesh_helpers',
    'utils.message_helpers',
    'utils.collection_helpers',
    'utils.uv_helpers',
    'ui.ui_auto_uv_panel',
    'ui.ui_rush_hour_panel',
    'ui.ui_prep_warnings_panel',
    'ui.ui_simple_vehicle_prep_panel',
    'ui.ui_advanced_vehicle_prep_panel',
    'operators.operator_scale_UV_worldspace',
    'operators.operator_tag_auto_uv',
    'operators.operator_export_vehicle',
    'operators.operator_set_scene_scale',
    'operators.operator_center_vehicle',
    'operators.operator_prepare_vehicle_for_unreal',
    'operators.operator_create_vehicle_collections',
    'operators.operator_rig_vehicle',
    'operators.operator_show_object_bounds',
    'operators.operator_simple_export',
    'operators.operator_simple_prepare_scene',
    'operators.operator_clear_parents',
    'operators.operator_add_to_vehicle_sub_collection',
    'ui.warning_details.ui_warn_exceed_nanite_materials_panel',
    'ui.warning_details.ui_warn_wrong_facing_panel',
    'ui.warning_details.ui_warn_negative_scales_panel',
    'ui.warning_details.ui_warn_unexpected_length_panel',
    'ui.warning_details.ui_warn_wheel_sizes_panel',
]


# Registration block from https://b3d.interplanety.org/en/creating-multifile-add-on-for-blender/

def generate_full_module_names():
    full_names = {}
    for curr_module_name in modulesNames:
        full_names[curr_module_name] = ('{}.{}'.format(__name__, curr_module_name))
    return full_names


module_full_names = generate_full_module_names()

for current_module_full_name in module_full_names.values():
    if current_module_full_name in sys.modules:
        importlib.reload(sys.modules[current_module_full_name])
    else:
        globals()[current_module_full_name] = importlib.import_module(current_module_full_name)
        setattr(globals()[current_module_full_name], 'modulesNames', module_full_names)


def register():
    for currentModuleName in module_full_names.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'register'):
                sys.modules[currentModuleName].register()


def unregister():
    for currentModuleName in module_full_names.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'unregister'):
                sys.modules[currentModuleName].unregister()


if __name__ == "__main__":
    register()
