# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import math

import bpy
from ..utils import mesh_helpers, uv_helpers


def apply_worldspace_uvs(context, curr_object: bpy.types.Object, apply_modifiers=True, apply_scale=True):
    if curr_object.enable_auto_uv is False:
        print("Skipping object marked for disabled auto UV " + curr_object.name)
        return
    bpy.context.view_layer.objects.active = curr_object
    curr_object.select_set(True)

    if apply_modifiers:
        # apply all modifiers to selected object
        mesh_helpers.apply_all_modifiers(context)
    if apply_scale:
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Smart project a set of UVs
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(island_margin=0.01)

    bpy.ops.object.mode_set(mode='OBJECT')

    num_faces = len(curr_object.data.polygons)
    total_surface_area = mesh_helpers.get_surface_area_of_mesh(curr_object)
    total_surface_area *= 0.0001
    total_uv_area = uv_helpers.get_uv_area(curr_object)
    # print("Face Area: " + str(total_surface_area))
    # print("UV Area: " + str(total_uv_area))
    if total_surface_area <= 0 or total_uv_area <= 0:
        # Skip this object
        return

    # Calculate scaling factor between world size and UV size
    # ProTip: Don't forget to get the square roots of both areas before working out scaling factor!
    scaling_factor = math.sqrt(total_surface_area / total_uv_area)
    # print("UV Scaling Factor: " + str(scaling_factor))

    uv_helpers.scale_uvs_object(curr_object, scaling_factor)

    total_uv_area_after_scaling = uv_helpers.get_uv_area(curr_object)
    # print("UV Area after scaling: " + str(total_uv_area_after_scaling))
    # Recenter UV islands

    curr_object.select_set(False)

    return


def apply_worldspace_uv_to_objects(context, apply_modifiers=True, apply_scale=True, selected_objects_only=True):
    selected_objects = bpy.context.selected_objects
    objects_to_process = selected_objects
    if selected_objects_only is False:
        objects_to_process = bpy.data.objects

    # Deselect everything
    bpy.ops.object.select_all(action='DESELECT')
    for obj in selected_objects:
        obj.select_set(False)

    # Process desired objects
    for sel_object in objects_to_process:
        if sel_object.type == 'MESH':
            apply_worldspace_uvs(context, sel_object, apply_modifiers, apply_scale)
        else:
            print("Skipping non-mesh object: " + sel_object.name)

    # Reselect the originally selected items
    for obj in selected_objects:
        obj.select_set(True)

    print("=============================")
    print("WorldSpace UV Complete")
    print("=============================")
    return


class RUSHHOURVP_OT_automatic_uv_unwrap_worldspace(bpy.types.Operator):
    """Scales UVs to worldspace"""
    bl_idname = "rushhourvp.auto_uv_worldspace"
    bl_label = "Scale UV To Worldspace operator"

    apply_modifiers: bpy.props.BoolProperty(
        name='apply_modifiers',
        default=True
    )

    apply_scale: bpy.props.BoolProperty(
        name='apply_scale',
        default=True
    )

    selected_objects_only: bpy.props.BoolProperty(
        name='selected_objects_only',
        default=True
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.mode == 'OBJECT'

    def execute(self, context):
        apply_worldspace_uv_to_objects(context, self.apply_modifiers, self.apply_scale, self.selected_objects_only)
        return {'FINISHED'}


def menu_apply_worldspace_uv_modifiers_and_scale(self, context):
    menu_item = self.layout.operator(RUSHHOURVP_OT_automatic_uv_unwrap_worldspace.bl_idname,
                                     text="Apply Worldspace UVs (Apply Modifiers & Scale)")
    menu_item.apply_modifiers = True


def menu_apply_worldspace_scale(self, context):
    menu_item = self.layout.operator(RUSHHOURVP_OT_automatic_uv_unwrap_worldspace.bl_idname, text="Apply Worldspace UVs (Apply Scale)")
    menu_item.apply_modifiers = False


def register():
    print("Registering Worldspace UV")
    bpy.utils.register_class(RUSHHOURVP_OT_automatic_uv_unwrap_worldspace)
    bpy.types.VIEW3D_MT_object.append(menu_apply_worldspace_uv_modifiers_and_scale)
    bpy.types.VIEW3D_MT_object.append(menu_apply_worldspace_scale)


def unregister():
    print("Un-Registering Worldspace UV")
    bpy.utils.unregister_class(RUSHHOURVP_OT_automatic_uv_unwrap_worldspace)
    bpy.types.VIEW3D_MT_object.remove(menu_apply_worldspace_uv_modifiers_and_scale)
    bpy.types.VIEW3D_MT_object.remove(menu_apply_worldspace_scale)
