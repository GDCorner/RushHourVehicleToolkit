# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import math
import bpy
import bmesh
import mathutils

from . import math_helpers
from . import mesh_helpers

import logging

log = logging.getLogger(__name__)


def update_all_checks():
    vehicle_collection = bpy.data.collections.get("vehicle")
    if vehicle_collection is None:
        # The vehicle is not prepped yet, so return True
        return

    bpy.context.scene.vehicle_checks.has_no_negative_scales = has_no_negative_scales()

    bpy.context.scene.vehicle_checks.is_vehicle_prepped = is_vehicle_prepped()

    if bpy.context.scene.vehicle_checks.is_vehicle_prepped:
        bpy.context.scene.vehicle_checks.is_vehicle_facing_correct_direction = is_vehicle_facing_correct_direction()
        bpy.context.scene.vehicle_checks.are_wheels_round = are_wheel_sizes_round()
        bpy.context.scene.vehicle_checks.are_all_meshes_under_nanite_material_limit = are_all_meshes_under_nanite_material_limit()

        is_safe, length = has_safe_length()
        bpy.context.scene.vehicle_checks.has_safe_length = is_safe
        bpy.context.scene.vehicle_checks.vehicle_length = length

    is_passing_all_checks()


def is_vehicle_prepped():
    # Get "prepped" collection
    prepped_collection = bpy.data.collections.get("prepped")

    if prepped_collection is None:
        # The vehicle is not prepped yet, so return False
        return False

    return True


def is_vehicle_facing_correct_direction():
    """Check the vehicle facing by getting the average position of the front 2 wheels, and doing a dot product with a
    vector facing +x"""
    # Get "prepped" collection
    prepped_collection = bpy.data.collections.get("prepped")

    if prepped_collection is None:
        # The vehicle is not prepped yet, so return False
        return False

    # Get the "prepped_wheels" collection from "prepped"
    prepped_wheels_collection = prepped_collection.children.get("prepped_wheels")

    if prepped_wheels_collection is None:
        # The vehicle is not prepped yet, so return False
        return False

    # get the front 2 wheels
    front_wheels = []
    for obj in prepped_wheels_collection.objects:
        if obj.name.startswith("wheel_0_"):
            front_wheels.append(obj)

    # Get the average position of the front wheels
    avg_pos = mathutils.Vector((0, 0, 0))
    for wheel in front_wheels:
        avg_pos += wheel.location
    avg_pos /= len(front_wheels)
    # Normalise average position
    avg_pos.normalize()

    # Create a vector facing +x
    forward_vec = mathutils.Vector((1.0, 0, 0))

    # Dot product the vector with the average position of the front wheels
    dot = avg_pos.dot(forward_vec)

    # If the dot product is less than 0.9, the vehicle is facing the wrong way
    if dot < 0.9:
        return False

    return True


def are_wheel_sizes_round():
    """Checks wheels are round"""
    # Get "prepped" collection
    prepped_collection = bpy.data.collections.get("prepped")

    if prepped_collection is None:
        # The vehicle is not prepped yet, so return False
        return False

    # Get the "prepped_wheels" collection from "prepped"
    prepped_wheels_collection = prepped_collection.children.get("prepped_wheels")

    if prepped_wheels_collection is None:
        # The vehicle is not prepped yet, so return False
        return False

    wheels_round = True

    # for each wheel
    for obj in prepped_wheels_collection.objects:
        if obj.name.startswith("wheel_"):
            # Get the wheel bounds
            bounds = mesh_helpers.get_bounds_of_meshes([obj])
            x_size = mesh_helpers.get_x_size_of_bounds(bounds)
            z_size = mesh_helpers.get_z_size_of_bounds(bounds)
            # Check x and Z sizes are the same

            if math.isclose(x_size, z_size, rel_tol=0.001) is False:
                log.warning(f"Wheel {obj.name} is not round. X size: {x_size}, Z size: {z_size}")
                wheels_round = False

    return wheels_round


def are_all_meshes_under_nanite_material_limit():
    """Checks all meshes have less than the maximum number of supported nanite materials"""
    MAX_NANITE_MATERIALS = 64

    # Get "prepped" collection
    prepped_collection = bpy.data.collections.get("prepped")

    if prepped_collection is None:
        # The vehicle is not prepped yet, so return False
        return False

    all_within_limits = True

    for obj in prepped_collection.all_objects:
        # if it's a mesh object
        if obj.type == 'MESH':
            # Get the number of materials
            num_materials = len(obj.material_slots)
            if num_materials > MAX_NANITE_MATERIALS:
                all_within_limits = False
                log.warning(f"Mesh {obj.name} has {num_materials} materials. This exceeds the maximum number of supported nanite materials ({MAX_NANITE_MATERIALS})")

    return all_within_limits


def has_no_negative_scales():
    """Checks all meshes have postive scales"""

    # Get "prepped" collection
    vehicle_collection = bpy.data.collections.get("vehicle")

    if vehicle_collection is None:
        # The vehicle is not prepped yet, so return False
        return True

    all_within_limits = True

    for obj in vehicle_collection.all_objects:
        # if it's a mesh object
        if obj.type == 'MESH':
            # Get the number of materials
            if obj.scale.x < 0 or obj.scale.y < 0 or obj.scale.z < 0:
                all_within_limits = False
                log.warning(f"Mesh {obj.name} has negative scale.")

    return all_within_limits


def has_safe_length():
    """Checks vehicle is within safe length tolerance"""
    # Get "prepped" collection
    prepped_collection = bpy.data.collections.get("prepped")

    if prepped_collection is None:
        # The vehicle is not prepped yet, so return False
        return False

    meshes = []
    for obj in prepped_collection.all_objects:
        if obj.type == 'MESH':
            meshes.append(obj)

    # Get the bounds of all meshes
    bounds = mesh_helpers.get_bounds_of_meshes(meshes)
    x_size = mesh_helpers.get_x_size_of_bounds(bounds)

    within_limits = True

    if x_size > 20.0 * 100.0:
        within_limits = False
        log.warning(f"Vehicle is {x_size}m long.")

    if x_size < 2 * 100.0:
        within_limits = False
        log.warning(f"Vehicle is {x_size}m long.")

    return within_limits, x_size


def is_passing_all_checks():
    vehicle_collection = bpy.data.collections.get("vehicle")
    if vehicle_collection is None:
        # The vehicle is not prepped yet, so return True
        return True

    unprepped_checks_passed = bpy.context.scene.vehicle_checks.has_no_negative_scales
    prepped_checks_passed = True

    if bpy.context.scene.vehicle_checks.is_vehicle_prepped:
        prepped_checks_passed = bpy.context.scene.vehicle_checks.is_vehicle_facing_correct_direction and bpy.context.scene.vehicle_checks.are_wheels_round and \
                                    bpy.context.scene.vehicle_checks.are_all_meshes_under_nanite_material_limit and bpy.context.scene.vehicle_checks.has_safe_length
    else:
        prepped_checks_passed = True

    bpy.context.scene.vehicle_checks.is_passing_all_checks = unprepped_checks_passed and prepped_checks_passed
    log.warning("is_passing_all_checks: " + str(bpy.context.scene.vehicle_checks.is_passing_all_checks))


    # print all the checks
    if True:
        log.warning("======================")
        log.warning("The current vehicle check status:")
        log.warning("has_no_negative_scales: " + str(bpy.context.scene.vehicle_checks.has_no_negative_scales))
        log.warning("is_vehicle_prepped: " + str(bpy.context.scene.vehicle_checks.is_vehicle_prepped))
        log.warning("is_vehicle_facing_correct_direction: " + str(bpy.context.scene.vehicle_checks.is_vehicle_facing_correct_direction))
        log.warning("are_wheels_round: " + str(bpy.context.scene.vehicle_checks.are_wheels_round))
        log.warning("are_all_meshes_under_nanite_material_limit: " + str(bpy.context.scene.vehicle_checks.are_all_meshes_under_nanite_material_limit))
        log.warning("has_safe_length: " + str(bpy.context.scene.vehicle_checks.has_safe_length))
        log.warning("is_passing_all_checks: " + str(bpy.context.scene.vehicle_checks.is_passing_all_checks))



    return bpy.context.scene.vehicle_checks.is_passing_all_checks


class VehicleCheckResults(bpy.types.PropertyGroup):
    is_passing_all_checks: bpy.props.BoolProperty(name="Vehicle Is Passing All Checks")
    is_vehicle_prepped: bpy.props.BoolProperty(name="Vehicle Is Prepped")
    is_vehicle_facing_correct_direction: bpy.props.BoolProperty(name="Vehicle Is Facing Correct Direction")
    are_wheels_round: bpy.props.BoolProperty(name="Wheels Are Not Round")
    wheels_not_round: bpy.props.StringProperty(name="Wheels Not Round")
    are_all_meshes_under_nanite_material_limit: bpy.props.BoolProperty(name="All Meshes Under Nanite Material Limit")
    meshes_over_nanite_material_limit: bpy.props.StringProperty(name="Meshes Over Nanite Material Limit")

    has_no_negative_scales: bpy.props.BoolProperty(name="No Negative Scales")
    meshes_with_negative_scales: bpy.props.StringProperty(name="Meshes With Negative Scales")

    has_safe_length: bpy.props.BoolProperty(name="Vehicle Is Within Safe Length")
    vehicle_length: bpy.props.FloatProperty(name="Vehicle Length")


def register():
    print("Registering Vehicle Check Results")
    bpy.utils.register_class(VehicleCheckResults)
    bpy.types.Scene.vehicle_checks = bpy.props.PointerProperty(type=VehicleCheckResults)


def unregister():
    print("Un-Registering Vehicle Check Results")
    bpy.utils.unregister_class(VehicleCheckResults)
    del bpy.types.Scene.vehicle_checks
