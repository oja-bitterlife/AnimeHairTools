import bpy
from .CreateHair import ArmatureSetup, BoneManager

modules = [
    ArmatureSetup,
    BoneManager,
]

class ANIME_HAIR_TOOLS_PT_setup_armature(bpy.types.Panel):
    bl_label = "Setup Armature"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "APT_HAIR_PT_UI"
    bl_idname = "APT_HAIR_PT_CREATE_HAIR"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        # Armature生成
        # ---------------------------------------------------------------------
        self.layout.label(text="Armature and RootBone Setting:")
        box = self.layout.box()
        box.enabled = context.mode == "OBJECT"

        # ATHのArmatureの設定
        box.prop(context.scene, "AHT_armature_name", text="Armature")
        box.prop(context.scene, "AHT_root_bone_name", text="RootBone")
        box.prop(context.scene, "AHT_parent_armature_name", text="ParentArmature")
        row = box.row()
        row.prop(context.scene, "AHT_parent_bone_group", text="ParentBone")
        row.prop(context.scene, "AHT_parent_bone_name", text="")

        # 実行
        box.operator("anime_hair_tools.setup_armature")

        # Mesh化&Bone生成
        # ---------------------------------------------------------------------
        self.layout.label(text="Bones Setting:")
        box = self.layout.box()
        box.enabled = context.mode == "OBJECT" and (bpy.context.view_layer.objects.active != None and bpy.context.view_layer.objects.active.type == "CURVE")

        box.prop(context.scene, "AHT_create_layer", text="Create Layer")
        box.operator("anime_hair_tools.create")
        box.operator("anime_hair_tools.remove")


# Enumrateの設定
def get_armature_names(self, context):
    objs = context.blend_data.objects
    return [(armature.name, armature.name, "") for armature in objs if armature.type == "ARMATURE"]

def get_bone_names(self, context):
    if context.scene.AHT_parent_armature_name == "":
        return []

    bones = context.blend_data.objects[context.scene.AHT_parent_armature_name].data.bones
    if context.scene.AHT_parent_bone_group == "":  # 全部
        return [(bone.name, bone.name, "") for bone in bones]
    else:  # Boneコレクションでフィルタ
        return [(bone.name, bone.name, "") for bone in bones if context.scene.AHT_parent_bone_group in bone.collections]

def register():
    for module in modules:
        if hasattr(module, "register"):
            module.register()

    # Armature設定用
    bpy.types.Scene.AHT_armature_name = bpy.props.StringProperty(name = "armature name", default="AHT_Armature")
    bpy.types.Scene.AHT_root_bone_name = bpy.props.StringProperty(name = "root bone name", default="AHT_RootBone")
    bpy.types.Scene.AHT_parent_armature_name = bpy.props.EnumProperty(name = "parent armature name", items=get_armature_names)
    bpy.types.Scene.AHT_parent_bone_group = bpy.props.StringProperty(name = "parent bone group", default="Bones")
    bpy.types.Scene.AHT_parent_bone_name = bpy.props.EnumProperty(name = "parent bone name", items=get_bone_names)

    bpy.types.Scene.AHT_create_layer = bpy.props.StringProperty(name = "bone create layer", default="AHT_HairBones")

def unregister():
    for module in modules:
        if hasattr(module, "unregister"):
            module.unregister()
