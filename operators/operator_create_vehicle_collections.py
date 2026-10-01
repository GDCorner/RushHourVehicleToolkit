# Copyright © 2024-2026 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy
from ..utils import collection_helpers


class RUSHHOURVP_CreateCollectionsProps(bpy.types.PropertyGroup):
    axle_count: bpy.props.IntProperty(
        name="Axle Count",
        description="Number of axles on the vehicle",
        min=2,
        default=2
    )


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
        axle_count = self.axle_count
        vehicle_col = collection_helpers.create_top_level_collection("vehicle")
        collection_helpers.create_collection("body", vehicle_col)
        collection_helpers.create_collection("body_interior", vehicle_col)
        collection_helpers.create_collection("body_transparent", vehicle_col)
        collection_helpers.create_collection("windows_interior", vehicle_col)
        collection_helpers.create_collection("windows_exterior", vehicle_col)

        wheels_collection = collection_helpers.create_collection("wheels", vehicle_col)
        for i in range(axle_count):
            create_wheel_collections_for_axle(i, wheels_collection)

        return {'FINISHED'}


def register():
    print("Registering create vehicles operator")
    bpy.utils.register_class(RUSHHOURVP_CreateCollectionsProps)
    bpy.utils.register_class(RUSHHOURVP_OT_create_vehicle_collections)
    bpy.types.Scene.rushhourvp_create_collections_props = bpy.props.PointerProperty(type=RUSHHOURVP_CreateCollectionsProps)


def unregister():
    print("Un-Registering create vehicles operator")
    bpy.utils.unregister_class(RUSHHOURVP_OT_create_vehicle_collections)
    bpy.utils.unregister_class(RUSHHOURVP_CreateCollectionsProps)
    del bpy.types.Scene.rushhourvp_create_collections_props


if __name__ == "__main__":
    register()
