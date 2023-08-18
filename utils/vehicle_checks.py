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