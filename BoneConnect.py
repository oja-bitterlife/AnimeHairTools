import bpy
import math

from .Util.ListupUtil import ListupProperty


# AHT用のArmatureのセットアップを行う
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_setup_bone_connect(bpy.types.Operator):
    bl_idname = "anime_hair_tools.setup_bone_connect"
    bl_label = "Connect"

    # execute
    def execute(self, context):
        # 編集対象ボーンの回収
        armature = bpy.context.active_object
        selected_bones = []
        for bone in armature.data.edit_bones:
            if bone.select:
                selected_bones.append(bone)

        # connect
        for bone in selected_bones:
            bone.use_connect = True

        return{'FINISHED'}

class ANIME_HAIR_TOOLS_OT_setup_bone_disconnect(bpy.types.Operator):
    bl_idname = "anime_hair_tools.setup_bone_disconnect"
    bl_label = "Disconnect"

    # execute
    def execute(self, context):
        # 編集対象ボーンの回収
        armature = bpy.context.active_object
        selected_bones = []
        for bone in armature.data.edit_bones:
            if bone.select:
                selected_bones.append(bone)

        # disconnect
        for bone in selected_bones:
            bone.use_connect = False

        return{'FINISHED'}


# UI描画設定
# =================================================================================================
def ui_draw(context, layout):
    layout.label(text="Bone Connect Setting:")
    box = layout.box()

    # 実行
    box.operator("anime_hair_tools.setup_bone_connect")
    box.operator("anime_hair_tools.setup_bone_disconnect")

