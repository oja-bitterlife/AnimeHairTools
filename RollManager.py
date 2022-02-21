import bpy

from .Util.ListupUtil import ListupProperty


# AHT用のArmatureのセットアップを行う
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_setup_bone_roll(bpy.types.Operator):
    bl_idname = "anime_hair_tools.setup_bone_roll"
    bl_label = "Setup Bone Roll"

    # execute
    def execute(self, context):
        scene = context.scene
        return{'FINISHED'}


# UI描画設定
# =================================================================================================
def ui_draw(context, layout):
    layout.label(text="Bone Roll Setting:")
    box = layout.box()

    # Roll参照先設定
    box.label(text="Roll Reference Object:")
    box.prop(context.scene.AHT_roll_reference, "roll_reference", text="Roll Reference Object")

    # 実行
    box.operator("anime_hair_tools.setup_bone_roll")


# =================================================================================================
def register():
    # Bone設定
    bpy.types.Scene.AHT_roll_reference = bpy.props.PointerProperty(type=ListupProperty)
