import bpy


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
            children_list.extend(self.gather_children_recursive(pose_bone))
        print(children_list)

        # まとめてselect
        for child_pose_bone in children_list:
            child_pose_bone.bone.select = True

        return{'FINISHED'}

    # 再帰的に選択する
    def gather_children_recursive(self, pose_bone):
        pose_bone_list = []
        for child_pose_bone in pose_bone.children:
            pose_bone_list.append(child_pose_bone)
            pose_bone_list.extend(self.gather_children_recursive(child_pose_bone))
        return pose_bone_list


# UI描画設定
# =================================================================================================
def ui_draw(context, layout):
    # 選択中ボーンの子ボーンを選択
    layout.label(text="Lazy Bone:")
    box = layout.box()
    box.operator("anime_hair_tools.select_child_bones")
