# Copyright © 2024 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy


def get_all_collections_in_scene():
    collections_in_scene = [
        c for c in bpy.data.collections
        if bpy.context.scene.user_of_id(c) and c.hide_render == False
    ]

    return collections_in_scene


def set_active_collection_by_name(collection_name):
    layer_collection = bpy.context.view_layer.layer_collection.children[collection_name]
    bpy.context.view_layer.active_layer_collection = layer_collection


def create_top_level_collection(collection_name):
    # check if collection already exists
    if collection_name in bpy.data.collections:
        return bpy.data.collections[collection_name]

    new_collection = bpy.context.blend_data.collections.new(name=collection_name)
    bpy.context.scene.collection.children.link(new_collection)
    return new_collection


def create_collection(collection_name, parent_collection):
    # check if collection exists in parent collection
    if collection_name in parent_collection.children:
        return parent_collection.children[collection_name]

    new_collection = bpy.context.blend_data.collections.new(name=collection_name)
    parent_collection.children.link(new_collection)

    return new_collection


def register():
    pass


def unregister():
    pass
