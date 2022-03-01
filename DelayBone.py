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

        # 子Boneから一旦キーフレームを削除する
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
        keyframes = {}
        for fcurve in dest_action.fcurves:
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
                # print(target, fcurve.array_index)
                # print(dir(fcurve.keyframe_points[0]))
                # print(fcurve.keyframe_points[0].amplitude)
                # print(fcurve.keyframe_points[0].back)
                # print(fcurve.keyframe_points[0].co)
                # print(fcurve.keyframe_points[0].co_ui)
                # print(fcurve.keyframe_points[0].easing)
                # print(fcurve.keyframe_points[0].handle_left)
                # print(fcurve.keyframe_points[0].handle_left_type)
                # print(fcurve.keyframe_points[0].handle_right)
                # print(fcurve.keyframe_points[0].handle_right_type)
                # print(fcurve.keyframe_points[0].interpolation)
                # print(fcurve.keyframe_points[0].period)

        # 子Boneにkeyframeを突っ込む
        for child_bone in children_list:
            for keyname in keyframes:
                # まずは突っ込み先のFCurveを作成
                target, index = keyname.split(":")
                data_path = 'pose.bones["%s"].%s' % (child_bone.name, target)
                dest_action.fcurves.new(data_path=data_path, index=int(index))


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
