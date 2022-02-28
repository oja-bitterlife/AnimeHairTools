import bpy

from .Util import BoneManager

class ANIME_HAIR_TOOLS_OT_setup_bone_connect(bpy.types.Operator):
    bl_idname = "anime_hair_tools.select_child_bones"
    bl_label = "Select Children"

    # execute
    def execute(self, context):
        # 編集対象ボーンの回収
        armature = bpy.context.active_object
        selected_bones = []
        for pose_bone in armature.pose.bones:
            if pose_bone.bone.select:
                selected_bones.append(pose_bone)

        # gather children
        children_list = []
        for pose_bone in selected_bones:
            children_list.extend(BoneManager.pose_bone_gather_children(pose_bone))

        # まとめてselect
        for child_pose_bone in children_list:
            child_pose_bone.bone.select = True

        return{'FINISHED'}


# UI描画設定
# =================================================================================================
def ui_draw(context, layout):
    # 選択中ボーンの子ボーンを選択
    layout.label(text="Delay Bone:")
    box = layout.box()
    box.operator("anime_hair_tools.select_child_bones")
