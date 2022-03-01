import bpy, re

from .Util import BoneManager

class ANIME_HAIR_TOOLS_OT_select_child_bones(bpy.types.Operator):
    bl_idname = "anime_hair_tools.select_child_bones"
    bl_label = "Select Children"

    # execute
    def execute(self, context):
        active_bone = context.active_pose_bone
        if not active_bone.bone.select:
            return{'FINISHED'}

        # gather children
        children_list = BoneManager.pose_bone_gather_children(active_bone)

        # まとめてselect
        for child_pose_bone in children_list:
            child_pose_bone.bone.select = True

        return{'FINISHED'}


class ANIME_HAIR_TOOLS_OT_deselect_child_bones(bpy.types.Operator):
    bl_idname = "anime_hair_tools.deselect_child_bones"
    bl_label = "Deselect Children"

    # execute
    def execute(self, context):
        active_bone = context.active_pose_bone
        if not active_bone.bone.select:
            return{'FINISHED'}

        # gather children
        children_list = BoneManager.pose_bone_gather_children(active_bone)

        # まとめてdeselect
        for child_pose_bone in children_list:
            child_pose_bone.bone.select = False

        return{'FINISHED'}


class ANIME_HAIR_TOOLS_OT_delay_setup(bpy.types.Operator):
    bl_idname = "anime_hair_tools.delay_setup"
    bl_label = "Copy Rotate Keys"

    # execute
    def execute(self, context):
        active_bone = context.active_pose_bone
        if not active_bone.bone.select:
            return{'FINISHED'}

        # gather children
        children_list = BoneManager.pose_bone_gather_children(active_bone)
        children_dict = {bone.name: bone for bone in children_list}

        src_action = bpy.data.actions["AHT_ArmatureAction"]
        dest_action = bpy.data.actions["AHT_ArmatureAction"]

        # 選択中Boneから一旦キーフレームを削除する
        for fcurve in dest_action.fcurves:
            # ボーン名と適用対象の取得
            match = re.search(r'pose.bones\["(.+?)"\].+?([^.]+$)', fcurve.data_path)
            if match:
                bone_name, target = match.groups()

                # 子のBoneだけ処理
                if bone_name in children_dict:
                    # 一旦キーを削除
                    dest_action.fcurves.remove(fcurve)

        # active_boneのキーフレームを取得
        for fcurve in dest_action.fcurves:
            # ボーン名と適用対象の取得
            match = re.search(r'pose.bones\["(.+?)"\].+?([^.]+$)', fcurve.data_path)
            if match:
                bone_name, target = match.groups()

            # ActiveBoneだけ処理
            if bone_name == active_bone.name:
                print(target)

                    # # 回転をコピー
                    # if target == "rotation_quaternion":
                    #     fcurve
                    #     pass
                    # elif target == "rotation_euler":
                    #     pass
                    # else:  # axis
                    #     pass


        return{'FINISHED'}

    def find_root_parent(self, pose_bone):
        if pose_bone.parent == None:
            return None
        # 親も選択中ならその親を見に行く
        if pose_bone.parent.bone.select:
            return self.find_root_parent(pose_bone.parent)
        return pose_bone.parent
        

# UI描画設定
# =================================================================================================
def ui_draw(context, layout):
    # 選択中ボーンの子ボーンを選択
    layout.label(text="Select Bones:")
    box = layout.box()
    box.operator("anime_hair_tools.select_child_bones")
    box.operator("anime_hair_tools.deselect_child_bones")
    layout.label(text="Propagate Action:")
    box = layout.box()
    box.operator("anime_hair_tools.delay_setup")
