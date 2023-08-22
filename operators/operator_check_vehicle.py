# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy
from ..utils import vehicle_checks


def check_vehicle(context):
    vehicle_checks.update_all_checks()


class RUSHHOURVP_OT_check_vehicle(bpy.types.Operator):
    """Centers the vehicle so it sits on the floor"""
    bl_idname = "rushhourvp.check_vehicle"
    bl_label = "Check Vehicle"

    def execute(self, context):
        check_vehicle(context)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(RUSHHOURVP_OT_check_vehicle)


def unregister():
    bpy.utils.unregister_class(RUSHHOURVP_OT_check_vehicle)
