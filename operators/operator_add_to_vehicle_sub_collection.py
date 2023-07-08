# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy
from ..utils import collection_helpers


class RUSHHOURVP_OT_add_selected_to_vehicle_collection(bpy.types.Operator):
    """UV Operator description"""
    bl_idname = "rushhourvp.add_selected_to_vehicle_collection"
    bl_label = "Add Selected Objects To Vehicle Collection"

    collection_name: bpy.props.StringProperty(
        name='collection_name',
        default="body"
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        vehicle_collection = bpy.data.collections["vehicle"]
        wheel_collection = vehicle_collection.children["wheels"]

        parent_collection = vehicle_collection

        if self.collection_name.startswith("wheel"):
            parent_collection = wheel_collection

        target_collection = parent_collection.children[self.collection_name]

        # for all selected objects
        for selected_obj in bpy.context.selected_objects:
            for old_collection in selected_obj.users_collection:
                old_collection.objects.unlink(selected_obj)
            target_collection.objects.link(selected_obj)

        return {'FINISHED'}


def register():
    print("Registering create vehicles operator")
    bpy.utils.register_class(RUSHHOURVP_OT_add_selected_to_vehicle_collection)


def unregister():
    print("Un-Registering create vehicles operator")
    bpy.utils.unregister_class(RUSHHOURVP_OT_add_selected_to_vehicle_collection)


if __name__ == "__main__":
    register()
