import bpy
import math


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
    bl_label = "Rset"

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

class ANIME_HAIR_TOOLS_OT_copy_active_roll(bpy.types.Operator):
    bl_idname = "anime_hair_tools.copy_active_roll"
    bl_label = "from Active"

    # execute
    def execute(self, context):
        # 編集対象ボーンの回収
        armature = context.active_object
        selected_bones = []
        for bone in armature.data.edit_bones:
            if bone.select and is_layer_enable(armature, bone):
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
class ANIME_HAIR_TOOLS_PT_bone_setting(bpy.types.Panel):
    bl_label = "Edit Bone Setting"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "APT_HAIR_PT_UI"
    bl_options = {'HEADER_LAYOUT_EXPAND'}

    def draw(self, context):
        if context.mode != "EDIT_ARMATURE":
            self.layout.enabled = False

        # 選択中BoneのBendyBoneの設定
        self.layout.label(text="Bendy Bone Setting:")
        box = self.layout.box()
        box.prop(context.scene, "AHT_bbone", text="BendyBones")
        box.operator("anime_hair_tools.setup_bendy_bone")

        # 選択中BoneのRollの設定
        self.layout.label(text="Bone Roll Setting:")
        box = self.layout.box()
        row = box.row()
        row.operator("anime_hair_tools.copy_active_roll")
        row.operator("anime_hair_tools.reset_bone_roll")

        # 選択中BoneのConnect/Disconnect
        self.layout.label(text="Bone Connect Setting:")
        box = self.layout.box()
        box.operator("anime_hair_tools.setup_bone_connect")
        box.operator("anime_hair_tools.setup_bone_disconnect")
