# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy
from ..utils import collection_helpers


def create_wheel_collections(axle, side, parent_collection):
    suffix = "_".join([str(axle), side])
    wheel_fr_col = collection_helpers.create_collection(f'wheel_{suffix}', parent_collection)
    collection_helpers.create_collection(f'rim_{suffix}', wheel_fr_col)
    collection_helpers.create_collection(f'brake_caliper_{suffix}', wheel_fr_col)


def create_wheel_collections_for_axle(axle, parent_collection):
    create_wheel_collections(axle, "L", parent_collection)
    create_wheel_collections(axle, "R", parent_collection)


class RUSHHOURVP_OT_create_vehicle_collections(bpy.types.Operator):
    """Creates the default collections for processing vehicles with the Rush Hour toolkit"""
    bl_idname = "rushhourvp.create_vehicle_collections"
    bl_label = "Create Unreal Vehicle Collections"

    axle_count: bpy.props.IntProperty(
        name='axles_count',
        default=2
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        vehicle_col = collection_helpers.create_top_level_collection("vehicle")
        collection_helpers.create_collection("body", vehicle_col)
        collection_helpers.create_collection("body_interior", vehicle_col)
        collection_helpers.create_collection("body_transparent", vehicle_col)
        collection_helpers.create_collection("windows_interior", vehicle_col)
        collection_helpers.create_collection("windows_exterior", vehicle_col)

        wheels_collection = collection_helpers.create_collection("wheels", vehicle_col)
        for i in range(self.axle_count):
            create_wheel_collections_for_axle(i, wheels_collection)

        return {'FINISHED'}


def register():
    print("Registering create vehicles operator")
    bpy.types.Scene.axle_count = bpy.props.IntProperty(min=2, default=2, name="Axle Count", description="Number of axles on the vehicle")
    bpy.utils.register_class(RUSHHOURVP_OT_create_vehicle_collections)


def unregister():
    print("Un-Registering create vehicles operator")
    del bpy.types.Scene.axle_count
    bpy.utils.unregister_class(RUSHHOURVP_OT_create_vehicle_collections)


if __name__ == "__main__":
    register()
