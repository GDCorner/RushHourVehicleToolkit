# Copyright © 2023 GDCorner
# This is licensed under the MIT license. See the LICENSE file for full details
# https://choosealicense.com/licenses/mit/

import bpy
from mathutils import Vector
from ..utils import collection_helpers


def add_child_bone(context, name, armature, location, parent, bone_length=1):
    bone = armature.edit_bones.new(name)
    bone.parent = parent
    bone.head = location
    print("=============================")
    print(name + str(location))
    bone.tail = (location[0], location[1] + bone_length, location[2])


def assign_mesh_to_vertex_group(context, mesh, vertex_group_name):
    # Deselect everything
    bpy.ops.object.select_all(action='DESELECT')

    unused_vertex_group_names = mesh.vertex_groups.keys()
    unused_vertex_group_names.remove(vertex_group_name)

    # Get the index of each vertex
    # Preallocate list
    vert_indices = [0] * len(mesh.data.vertices)
    # retrieve vertex indices
    mesh.data.vertices.foreach_get('index', vert_indices)

    # Assign the vertices to the vertex group
    mesh.vertex_groups[vertex_group_name].add(vert_indices, 1, 'REPLACE')

    # Unassign all other vert groups
    for vert_group in unused_vertex_group_names:
        mesh.vertex_groups[vert_group].add(vert_indices, 1, 'SUBTRACT')


def decimate_mesh(context, mesh, decimate_amount=0.1):
    # Add decimate modifier to wheel mesh
    decimate_mod = mesh.modifiers.new("Decimate", 'DECIMATE')
    decimate_mod.decimate_type = 'COLLAPSE'
    decimate_mod.ratio = decimate_amount
    mesh.select_set(True)

    bpy.context.view_layer.objects.active = mesh
    # Clear custom normals
    bpy.ops.mesh.customdata_custom_splitnormals_clear()
    # Apply decimate modifier to skeleton wheel mesh
    bpy.ops.object.modifier_apply(modifier="Decimate")
    mesh.select_set(False)


def duplicate_meshes_for_skeletal_mesh(context, skel_collection, decimate_proxy_mesh: bool = True, decimate_amount: float = 0.1):
    # Deselect everything
    bpy.ops.object.select_all(action='DESELECT')

    # Get the "prepped" collection
    prepped_collection = bpy.data.collections["prepped"]

    # duplicate body mesh into skel collection, unlinked
    body_mesh = prepped_collection.objects["body"]
    skel_body_mesh = body_mesh.copy()
    skel_body_mesh.data = body_mesh.data.copy()
    skel_body_mesh.animation_data_clear()
    skel_collection.objects.link(skel_body_mesh)
    skel_body_mesh.name = "SK_phys_mesh"
    if decimate_proxy_mesh:
        decimate_mesh(context, skel_body_mesh, decimate_amount)

    # Get the prepped_wheels collection
    prepped_wheels_collection = bpy.data.collections["prepped_wheels"]
    # get wheel meshes
    for obj in prepped_wheels_collection.objects:
        skel_wheel_mesh = obj.copy()
        skel_wheel_mesh.data = obj.data.copy()
        skel_wheel_mesh.animation_data_clear()
        skel_collection.objects.link(skel_wheel_mesh)
        skel_wheel_mesh.name = "SK_" + obj.name
        if decimate_proxy_mesh:
            decimate_mesh(context, skel_wheel_mesh, decimate_amount)

    # get proxy mesh
    proxy_mesh = prepped_collection.objects["proxy"]
    skel_proxy_mesh = proxy_mesh.copy()
    skel_proxy_mesh.data = proxy_mesh.data.copy()
    skel_proxy_mesh.animation_data_clear()
    skel_collection.objects.link(skel_proxy_mesh)
    skel_proxy_mesh.name = "SK_" + proxy_mesh.name


def duplicate_for_static_mesh_collection(context, parent_collection):
    # Get prepped collection
    prepped_collection = bpy.data.collections["prepped"]

    # Create collection "static_meshes" in prepped
    static_meshes_collection = collection_helpers.create_collection("static_meshes", parent_collection)

    # Get body mesh location from parent collection
    body_mesh = prepped_collection.objects["body"]
    body_mesh_location = body_mesh.location

    # Duplicate all body meshes in prepped collection
    for obj in prepped_collection.objects:
        if obj.name == "proxy":
            # Skip the proxy mesh for the static mesh export
            continue
        if obj.type == "MESH":
            new_obj = obj.copy()
            new_obj.data = obj.data.copy()
            new_obj.animation_data_clear()
            static_meshes_collection.objects.link(new_obj)
            new_obj.name = "SM_" + obj.name

    # Get the wheels collections
    prepped_wheels_collection = bpy.data.collections["prepped_wheels"]

    wheels_objs = []
    for obj in prepped_wheels_collection.objects:
        if obj.name.startswith("wheel"):
            wheels_objs.append(obj)

    caliper_objs = []
    for obj in prepped_wheels_collection.objects:
        if obj.name.startswith("brake_caliper"):
            caliper_objs.append(obj)

    # Duplicate all wheel meshes in prepped collection
    for obj in wheels_objs:
        wheel_location = obj.location
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        new_obj.animation_data_clear()
        static_meshes_collection.objects.link(new_obj)
        new_obj.name = "SM_" + obj.name
        # Recenter static mesh to the origin
        new_obj.location -= wheel_location

    for obj in caliper_objs:
        wheel_obj = [x for x in wheels_objs if x.name == obj.name.replace("brake_caliper", "wheel")][0]
        wheel_location = wheel_obj.location
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        new_obj.animation_data_clear()
        static_meshes_collection.objects.link(new_obj)
        new_obj.name = "SM_" + obj.name
        # Recenter caliper to the origin according to the wheel location, not the caliper location
        # This means the caliper keeps it's relative location to the wheel
        new_obj.location -= wheel_location

def join_skeletal_mesh(context, meshes):
    # Deselect everything
    bpy.ops.object.select_all(action='DESELECT')

    # Join wheels and body
    for mesh in meshes:
        mesh.select_set(True)
    # set active object
    context.view_layer.objects.active = meshes[0]

    # Join meshes in collection
    bpy.ops.object.join()


def rig_vehicle(context, decimate_proxy_mesh: bool = True, decimate_amount: float = 0.1):
    default_bone_length = 100

    # deselect everything
    bpy.ops.object.select_all(action='DESELECT')

    # Create an "Export" collection at the top level
    export_collection = collection_helpers.create_top_level_collection("export")

    # make export collection layer visible in viewport so selection works as expected
    export_collection.hide_viewport = False
    view_layer = bpy.context.view_layer
    layer_collection = view_layer.layer_collection.children['export']
    original_layer_visibility = layer_collection.hide_viewport
    layer_collection.hide_viewport = False

    # Delete everything in the export collection
    for obj in export_collection.all_objects:
        obj.select_set(True)
    bpy.ops.object.delete()

    # Create a skeleton collection within export
    skeleton_collection = collection_helpers.create_collection("skeleton", export_collection)

    # Duplicate and move static meshes to origin for export and attaching to skeleton
    duplicate_for_static_mesh_collection(context, export_collection)

    # Duplicate meshes for skeletal mesh "physics" mesh
    duplicate_meshes_for_skeletal_mesh(context, skeleton_collection, decimate_proxy_mesh=decimate_proxy_mesh, decimate_amount=decimate_amount)

    # Create an armature object
    # For unreal not to create a new bone at the root, the armature must be named "Armature"
    armature = bpy.data.armatures.new("Armature")
    armature_obj = bpy.data.objects.new("Armature", armature)

    # Add armature to skel_collection collection
    skeleton_collection.objects.link(armature_obj)

    # Set some viewport display options
    armature_obj.show_in_front = True
    armature_obj.show_axis = True
    armature_obj.data.show_axes = True

    # Deselect everything
    bpy.ops.object.select_all(action='DESELECT')

    # Select the armature object
    armature_obj.select_set(True)
    context.view_layer.objects.active = armature_obj

    # Enter edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    body_obj = skeleton_collection.objects["SK_phys_mesh"]

    # Create a root bone at the origin
    root_bone = armature.edit_bones.new("body")
    body_position = Vector((0, 0, 0))
    root_bone.head = body_position
    root_bone.tail = body_position + Vector((0, default_bone_length, 0))

    wheel_objs = []
    caliper_objs = []

    # Create a bone for wheel_fr
    for obj in skeleton_collection.objects:
        if obj.name.startswith("SK_brake_caliper_"):
            caliper_objs.append(obj)
            continue
        if obj.name.startswith("SK_wheel_"):
            wheel_objs.append(obj)
            add_child_bone(context, obj.name[3:], armature, obj.location, root_bone, default_bone_length)
            caliper_bone_name = "brake_caliper_" + obj.name[9:]
            add_child_bone(context, caliper_bone_name, armature, obj.location, root_bone, default_bone_length)

    # Get the proxy mesh object from within skel_collection
    proxy_mesh_obj = skeleton_collection.objects["SK_proxy"]

    # Exit edit mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Now parent to objects to the armature

    # Deselect everything
    bpy.ops.object.select_all(action='DESELECT')

    # Select all the wheels and the body
    for wheel_obj in wheel_objs:
        wheel_obj.select_set(True)
    for caliper_obj in caliper_objs:
        caliper_obj.select_set(True)
    proxy_mesh_obj.select_set(True)
    body_obj.select_set(True)

    # Set the armature to the active object
    context.view_layer.objects.active = armature_obj
    # Parent the meshes to the armature
    bpy.ops.object.parent_set(type='ARMATURE_NAME')

    # Deselect everything
    bpy.ops.object.select_all(action='DESELECT')

    # Assign vertex groups to the meshes
    assign_mesh_to_vertex_group(context, body_obj, "body")
    for wheel_obj in wheel_objs:
        assign_mesh_to_vertex_group(context, wheel_obj, wheel_obj.name[3:])
    for caliper_obj in caliper_objs:
        assign_mesh_to_vertex_group(context, caliper_obj, caliper_obj.name[3:])
    assign_mesh_to_vertex_group(context, proxy_mesh_obj, "body")

    # DO NOT ADD PROXY OBJECT TO THIS LIST
    # the proxy object should not be merged
    meshes_to_join = [body_obj] + wheel_objs + caliper_objs
    # Join the skeletal mesh for the physics object
    join_skeletal_mesh(context, meshes_to_join)

    # Change the layer collection visibility back to the original state
    layer_collection.hide_viewport = original_layer_visibility


class RUSHHOURVP_OT_rig_vehicle(bpy.types.Operator):
    """Rigs prepped vehicle for export to Unreal"""
    bl_idname = "rushhourvp.rig_vehicle"
    bl_label = "Rig Vehicle for Unreal"

    decimate_proxy_mesh: bpy.props.BoolProperty(
        name='decimate_proxy_mesh',
        default=True,
        description="Whether to decimate the proxy mesh before export"
    )

    decimate_amount: bpy.props.FloatProperty(
        name='decimate_amount',
        default=0.1,
        min=0.01,
        max=1.0,
        description="How much to decimate the proxy mesh by"
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        rig_vehicle(context, self.decimate_proxy_mesh, self.decimate_amount)
        return {'FINISHED'}


def register():
    print("Registering create vehicles operator")
    bpy.types.Scene.rh_decimate_proxy_mesh = bpy.props.BoolProperty(
        name='Decimate Proxy Mesh',
        default=True,
        description="Whether to decimate the proxy mesh before export"
    )
    bpy.types.Scene.rh_decimate_amount = bpy.props.FloatProperty(
        name='Decimate Amount',
        default=0.1,
        min=0.01,
        max=1.0,
        description="How much to decimate the proxy mesh by"
    )
    bpy.utils.register_class(RUSHHOURVP_OT_rig_vehicle)


def unregister():
    print("Un-Registering create vehicles operator")
    del bpy.types.Scene.rh_decimate_proxy_mesh
    del bpy.types.Scene.rh_decimate_amount
    bpy.utils.unregister_class(RUSHHOURVP_OT_rig_vehicle)


if __name__ == "__main__":
    register()
