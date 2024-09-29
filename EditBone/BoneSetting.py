import bpy
import math

# Utility
# =================================================================================================
# BoneCollectionが表示になっているかどうか(非表示レイヤーは処理しない)
def is_bone_collection_enable(armature, edit_bone):
    # 所属コレクションのどれかが有効なら処理対象
    for collection in edit_bone.collections:
        if collection.is_visible:
            return True
    return True


# 選択中のBoneのRollを設定する
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_reset_bone_roll(bpy.types.Operator):
    bl_idname = "anime_hair_tools.reset_bone_roll"
    bl_label = "Rset"

    # execute
    def execute(self, context):
        # 編集対象ボーンの回収
        armature = context.active_object
        selected_bones = []
        for bone in armature.data.edit_bones:
            if bone.select and is_bone_collection_enable(armature, bone):
                selected_bones.append(bone)

        for bone in selected_bones:
            bone.roll = 0

        return{'FINISHED'}

class ANIME_HAIR_TOOLS_OT_copy_active_roll(bpy.types.Operator):
    bl_idname = "anime_hair_tools.copy_active_roll"
    bl_label = "from Active"

    # execute
    def execute(self, context):
        # 編集対象ボーンの回収
        armature = context.active_object
        selected_bones = []
        for bone in armature.data.edit_bones:
            if bone.select and is_bone_collection_enable(armature, bone):
                selected_bones.append(bone)

        for bone in selected_bones:
            if bone == context.active_bone:
                continue  # Activeボーンはそのまま

            bone.roll = context.active_bone.roll

        return{'FINISHED'}



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
            if bone.select_head and is_bone_collection_enable(armature, bone):
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
            if bone.select_head and is_bone_collection_enable(armature, bone):
                selected_bones.append(bone)

        # disconnect
        for bone in selected_bones:
            bone.use_connect = False

        return{'FINISHED'}



# UI描画設定
# =================================================================================================
classes = [
    ANIME_HAIR_TOOLS_OT_reset_bone_roll,
    ANIME_HAIR_TOOLS_OT_copy_active_roll,
    ANIME_HAIR_TOOLS_OT_setup_bone_connect,
    ANIME_HAIR_TOOLS_OT_setup_bone_disconnect,
]

def draw(parent, context, layout):
    if context.mode != "EDIT_ARMATURE":
        layout.enabled = False

    # 選択中BoneのRollの設定
    layout.label(text="Bone Roll Setting:")
    box = layout.box()
    row = box.row()
    row.operator("anime_hair_tools.copy_active_roll")
    row.operator("anime_hair_tools.reset_bone_roll")

    # 選択中BoneのConnect/Disconnect
    layout.label(text="Bone Connect Setting:")
    box = layout.box()
    row = box.row()
    row.operator("anime_hair_tools.setup_bone_connect")
    row.operator("anime_hair_tools.setup_bone_disconnect")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
