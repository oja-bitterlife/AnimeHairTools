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


class ANIME_HAIR_TOOLS_OT_copy_rotate_keys(bpy.types.Operator):
    bl_idname = "anime_hair_tools.copy_rotate_keys"
    bl_label = "Copy Rotate Keys"

    # execute
    def execute(self, context):
        active_bone = context.active_pose_bone
        if not active_bone.bone.select:
            return{'FINISHED'}

        # gather children
        children_list = BoneManager.pose_bone_gather_children(active_bone)

        action = bpy.data.actions["AHT_ArmatureAction"]

        # 一旦子Boneからキーを削除する
        remove_all_keys_from_children(action, children_list)

        # active_boneのキーフレームを取得
        keyframes = {}
        for fcurve in action.fcurves:
            # ボーン名と適用対象の取得
            match = re.search(r'pose.bones\["(.+?)"\].+?([^.]+$)', fcurve.data_path)
            if match:
                bone_name, target = match.groups()

            # ActiveBoneだけ処理
            if bone_name == active_bone.name:
                # 回転だけコピー
                if target != "rotation_quaternion" and target != "rotation_euler" and target != "rotation_axis_angle":
                    continue
                keyframes["%s:%d" % (target, fcurve.array_index)] = fcurve.keyframe_points

        # 子Boneにkeyframeを突っ込む
        for child_bone in children_list:
            for keyname in keyframes:
                # まずは突っ込み先のFCurveを作成
                target, index = keyname.split(":")
                data_path = 'pose.bones["%s"].%s' % (child_bone.name, target)
                new_fcurve = action.fcurves.new(data_path=data_path, index=int(index))

                # keyframe_pointsのコピー
                for point in keyframes[keyname]:
                    offset = 5
                    new_point = new_fcurve.keyframe_points.insert(point.co[0]+offset, point.co[1])
                    # co以外の残りをコピー
                    self.copy_key(point, new_point)

        return{'FINISHED'}    

    # keyの内容をコピーする
    def copy_key(self, src_point, dest_point):
        dest_point.amplitude = src_point.amplitude
        dest_point.back = src_point.back
        # new_point.co
        # new_point.co_ui
        dest_point.easing = src_point.easing
        dest_point.handle_left = src_point.handle_left
        dest_point.handle_left_type = src_point.handle_left_type
        dest_point.handle_right = src_point.handle_right
        dest_point.handle_right_type = src_point.handle_right_type
        dest_point.interpolation = src_point.interpolation
        dest_point.period = src_point.period

class ANIME_HAIR_TOOLS_OT_remove_children_keys(bpy.types.Operator):
    bl_idname = "anime_hair_tools.remove_children_keys"
    bl_label = "Remove Children Keys"

    # execute
    def execute(self, context):
        active_bone = context.active_pose_bone
        if not active_bone.bone.select:
            return{'FINISHED'}

        # gather children
        children_list = BoneManager.pose_bone_gather_children(active_bone)

        action = bpy.data.actions["AHT_ArmatureAction"]

        # 一旦子Boneからキーを削除する
        remove_all_keys_from_children(action, children_list)

        return{'FINISHED'}


# 子Boneからキーを削除する
def remove_all_keys_from_children(action, children_list):
    children_dict = {bone.name: bone for bone in children_list}

    # 子Boneからキーフレームを削除する
    for fcurve in action.fcurves:
        # ボーン名と適用対象の取得
        match = re.search(r'pose.bones\["(.+?)"\].+?([^.]+$)', fcurve.data_path)
        if match:
            bone_name, target = match.groups()

            # 子のBoneだけ処理
            if bone_name in children_dict:
                # キーを削除
                action.fcurves.remove(fcurve)


# UI描画設定
# =================================================================================================
def ui_draw(context, layout):
    # 選択中ボーンの子ボーンを選択
    layout.label(text="Select Bones:")
    box = layout.box()
    box.operator("anime_hair_tools.select_child_bones")
    box.operator("anime_hair_tools.deselect_child_bones")

    # Actionを子BoneにCopyする
    layout.label(text="Propagate Action:")
    box = layout.box()
    box.operator("anime_hair_tools.copy_rotate_keys")
    box.operator("anime_hair_tools.remove_children_keys")
