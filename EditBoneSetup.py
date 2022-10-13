import bpy
import math

from .Util.ListupUtil import ListupProperty


# 選択中BoneのBendyBoneの設定
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_setup_bendy_bone(bpy.types.Operator):
    bl_idname = "anime_hair_tools.setup_bendy_bone"
    bl_label = "Setup Bendy Bone"

    # execute
    def execute(self, context):
        # 編集対象ボーンの回収
        armature = context.active_object
        selected_bones = []
        for bone in armature.data.edit_bones:
            if bone.select and is_layer_enable(armature, bone):
                selected_bones.append(bone)

        if context.scene.AHT_bbone < 1:
            context.scene.AHT_bbone = 1

        # connect
        for bone in selected_bones:
            bone.bbone_segments = context.scene.AHT_bbone

        return{'FINISHED'}


# 選択中のBoneのRollを設定する
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_reset_bone_roll(bpy.types.Operator):
    bl_idname = "anime_hair_tools.reset_bone_roll"
    bl_label = "Rset Bone Roll"

    # execute
    def execute(self, context):
        # 編集対象ボーンの回収
        armature = context.active_object
        selected_bones = []
        for bone in armature.data.edit_bones:
            if bone.select and is_layer_enable(armature, bone):
                selected_bones.append(bone)

        for bone in selected_bones:
            bone.roll = 0

        return{'FINISHED'}

class ANIME_HAIR_TOOLS_OT_setup_bone_roll(bpy.types.Operator):
    bl_idname = "anime_hair_tools.setup_bone_roll"
    bl_label = "Setup Bone Roll"

    # execute
    def execute(self, context):
        # 編集対象ボーンの回収
        armature = context.active_object
        selected_bones = []
        for bone in armature.data.edit_bones:
            if bone.select and is_layer_enable(armature, bone):
                selected_bones.append(bone)

        SetupBoneRoll(selected_bones)

        return{'FINISHED'}

def SetupBoneRoll(selected_bones):
    # 最近点を探る
    for bone in selected_bones:
        if bone.parent == None:
            continue  # 起点のボーンはそのまま

        vec = bone.y_axis.cross(bone.parent.y_axis).normalized()
        if vec.length == 0:
            bone.roll = bone.parent.roll  # 一直線なので親と同じRollになる
            continue

        # 角度計算
        cs = max(-1, min(1, vec.dot(bone.x_axis)))
        rad = math.acos(cs)  # 角度差分(CW/CCWはわからない)
        dir = vec.cross(bone.x_axis).dot(bone.y_axis)  # 3重積で方向
        if dir > 0:
            rad = -rad
        bone.roll += rad



# 選択中BoneのConnect/Disconnect
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_setup_bone_connect(bpy.types.Operator):
    bl_idname = "anime_hair_tools.setup_bone_connect"
    bl_label = "Connect All"

    # execute
    def execute(self, context):
        # 編集対象ボーンの回収
        armature = context.active_object
        selected_bones = []
        for bone in armature.data.edit_bones:
            if bone.select_head and is_layer_enable(armature, bone):
                selected_bones.append(bone)

        # connect
        for bone in selected_bones:
            bone.use_connect = True

        return{'FINISHED'}


class ANIME_HAIR_TOOLS_OT_setup_bone_disconnect(bpy.types.Operator):
    bl_idname = "anime_hair_tools.setup_bone_disconnect"
    bl_label = "Disconnect All"

    # execute
    def execute(self, context):
        # 編集対象ボーンの回収
        armature = context.active_object
        selected_bones = []
        for bone in armature.data.edit_bones:
            if bone.select_head and is_layer_enable(armature, bone):
                selected_bones.append(bone)

        # disconnect
        for bone in selected_bones:
            bone.use_connect = False

        return{'FINISHED'}


# boneが含まれているレイヤーがArmatureの表示レイヤーになっているかどうか
def is_layer_enable(armature, edit_bone):
    for i, b in enumerate(edit_bone.layers):
        if b:
            return armature.data.layers[i]
    return False


# UI描画設定
# =================================================================================================
def ui_draw(context, layout):
    # 選択中BoneのBendyBoneの設定
    layout.label(text="Bendy Bone Setting:")
    box = layout.box()
    box.prop(context.scene, "AHT_bbone", text="BendyBones")
    box.operator("anime_hair_tools.setup_bendy_bone")

    # 選択中BoneのRollの設定
    layout.label(text="Bone Roll Setting:")
    box = layout.box()
    box.operator("anime_hair_tools.reset_bone_roll")
    box.operator("anime_hair_tools.setup_bone_roll")

    # 選択中BoneのConnect/Disconnect
    layout.label(text="Bone Connect Setting:")
    box = layout.box()
    box.operator("anime_hair_tools.setup_bone_connect")
    box.operator("anime_hair_tools.setup_bone_disconnect")

