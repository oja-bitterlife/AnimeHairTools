import bpy
from .CreateHair import ArmatureSetup

modules = [
    ArmatureSetup,
]

class ANIME_HAIR_TOOLS_PT_create_hair(bpy.types.Panel):
    bl_label = "Setup hair Armature"
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


def register():
    for module in modules:
        if hasattr(module, "register"):
            module.register()

    # Armature設定用
    bpy.types.Scene.AHT_armature_name = bpy.props.StringProperty(name = "armature name", default="AHT_Armature")
    bpy.types.Scene.AHT_root_bone_name = bpy.props.StringProperty(name = "bone root name", default="AHT_RootBone")

    # Bone設定
    bpy.types.Scene.AHT_bbone = bpy.props.IntProperty(name = "BendyBone split", default=3, min=1, max=32)
    bpy.types.Scene.AHT_create_layer = bpy.props.IntProperty(name = "Bone Create Layer", default=1, min=1, max=32)

    # モディファイア設定
    bpy.types.Scene.AHT_subdivision = bpy.props.BoolProperty(name = "With Subdivision", default=True)

def unregister():
    for module in modules:
        if hasattr(module, "unregister"):
            module.unregister()
