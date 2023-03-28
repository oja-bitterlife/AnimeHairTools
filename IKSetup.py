import bpy, mathutils
from .Util import ConstraintUtil, Naming


# IK Setup
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_ik_setup(bpy.types.Operator):
    bl_idname = "anime_hair_tools.ik_setup"
    bl_label = "IK Setup"

    # execute ok
    def execute(self, context):
        armature = context.active_object

        # すでにあるIK関連を消しておく
        remove_selected_pose_bones(armature, context.selected_pose_bones)

        for pose_bone in context.selected_pose_bones:
            # 親のいないボーン(非連結ボーン)は何もしない
            if pose_bone.parent == None:
                continue

            # 終端だったらセットアップ
            if len(pose_bone.children) == 0:
                self.IK_setup(context, armature, pose_bone)

        return {'FINISHED'}

    def IK_setup(self, context, armature, end_bone):
        # 生成するBone名
        ik_target_bone_name = Naming.make_ik_target_bone_name(end_bone.name)

        # ターゲットボーンセットアップ
        bpy.ops.object.mode_set(mode='EDIT')
        new_edit_bone = armature.data.edit_bones.new(name=ik_target_bone_name)
        new_edit_bone.head = end_bone.tail
        new_edit_bone.tail = end_bone.tail + armature.matrix_world.inverted() @ mathutils.Vector((0,0,-context.scene.AHT_ik_target_size))
        new_edit_bone.use_deform = False
 
        bpy.ops.object.mode_set(mode='POSE')

        # IK constraintの追加
        ConstraintUtil.add_ik(armature, end_bone, ik_target_bone_name, 1)


# IK Remove
# =================================================================================================
def remove_selected_pose_bones(armature, selected_pose_bones):
    # 警告がでてしまうので、IK Constraintを先に消す
    subtargets = []
    for pose_bone in selected_pose_bones:
        subtargets += ConstraintUtil.remove_ik(armature, pose_bone)

    # TargetBoneの回収
    for pose_bone in selected_pose_bones:
        if pose_bone.name.startswith(Naming.IK_TARGET_BONE_PREFIX):
            subtargets.append(pose_bone.name)
    subtargets = set(subtargets)  # unique

    # TargetBoneを消す
    bpy.ops.object.mode_set(mode='EDIT')
    for pose_bone_name in subtargets:
        edit_bone = armature.data.edit_bones.get(pose_bone_name)
        if edit_bone:
            armature.data.edit_bones.remove(edit_bone)
    bpy.ops.object.mode_set(mode='POSE')

class ANIME_HAIR_TOOLS_OT_ik_remove(bpy.types.Operator):
    bl_idname = "anime_hair_tools.ik_remove"
    bl_label = "IK Remove"

    # execute ok
    def execute(self, context):
        armature = context.active_object
        remove_selected_pose_bones(armature, context.selected_pose_bones)
        return {'FINISHED'}


# IK Enable
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_ik_enable(bpy.types.Operator):
    bl_idname = "anime_hair_tools.ik_enable"
    bl_label = "IK Enable All"

    # execute ok
    def execute(self, context):
        armature = context.active_object
        for pose_bone in armature.pose.bones:
            for constraint in pose_bone.constraints:
                if constraint.name.startswith(Naming.CONSTRAINT_PREFIX + "ik_"):
                    constraint.mute = False

        return {'FINISHED'}


# IK Disable
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_ik_disable(bpy.types.Operator):
    bl_idname = "anime_hair_tools.ik_disable"
    bl_label = "IK Dsiable All"

    # execute ok
    def execute(self, context):
        armature = context.active_object
        for pose_bone in armature.pose.bones:
            for constraint in pose_bone.constraints:
                if constraint.name.startswith(Naming.CONSTRAINT_PREFIX + "ik_"):
                    constraint.mute = True

        return {'FINISHED'}


# UI描画設定
# =================================================================================================
class ANIME_HAIR_TOOLS_PT_ik_setup(bpy.types.Panel):
    bl_label = "IK Setup"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "APT_HAIR_PT_UI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        if context.mode != "POSE":
            self.layout.enabled = False

        box = self.layout.box()
        box.prop(context.scene, "AHT_ik_target_size", text="IK Target Size")
        box.operator("anime_hair_tools.ik_setup")
        box.operator("anime_hair_tools.ik_remove")
        box = self.layout.box()
        box.operator("anime_hair_tools.ik_enable")
        box.operator("anime_hair_tools.ik_disable")


# =================================================================================================
def register():
    # Bone設定
    bpy.types.Scene.AHT_ik_target_size = bpy.props.FloatProperty(name = "IK Target Size", default=0.1)
