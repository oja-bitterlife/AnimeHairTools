import bpy
from .CreateHair import ArmatureSetup

modules = [
    ArmatureSetup,
]

class ANIME_HAIR_TOOLS_PT_setup_armature(bpy.types.Panel):
    bl_label = "Setup Armature"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "APT_HAIR_PT_UI"
    bl_idname = "APT_HAIR_PT_CREATE_HAIR"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        for i, module in enumerate(modules):
            if hasattr(module, "draw"):
                if hasattr(module, "label"):
                    self.layout.label(text=module.label)
                module.draw(self, context, self.layout.box())


# Enumrateの設定
def get_armature_names(self, context):
    objs = context.blend_data.objects
    return [(armature.name, armature.name, "") for armature in objs if armature.type == "ARMATURE"]

def get_bone_names(self, context):
    bones = context.blend_data.objects[context.scene.AHT_parent_armature_name].data.bones
    # 変数aにAHT_parent_bone_groupを設定
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

def unregister():
    for module in modules:
        if hasattr(module, "unregister"):
            module.unregister()
