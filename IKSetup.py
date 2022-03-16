import bpy, mathutils
from .Util import BoneManager, ConstraintUtil, Naming


# IK Setup
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_ik_setup(bpy.types.Operator):
    bl_idname = "anime_hair_tools.ik_setup"
    bl_label = "IK Setup"

    # execute ok
    def execute(self, context):
        armature = context.active_object

        for root_bone in context.selected_pose_bones:
            # 一番上の親を探す
            root_parent = self.find_top_root(root_bone)

            # 終端を探す
            children_list = BoneManager.pose_bone_gather_children(root_bone, lambda pose_bone: not pose_bone.bone.select)
            for child in children_list:
                # 終端だったらセットアップ
                if len(child.children) == 0:
                    self.IK_setup(context, armature, root_parent, root_bone, child)

        return {'FINISHED'}

    # 一番上の親を返す
    def find_top_root(self, pose_bone):
        if pose_bone.parent:
            return self.find_top_root(pose_bone.parent)
        return pose_bone

    def IK_setup(self, context, armature, root_parent, root_bone, end_bone):
        # すでにあるIK関連を消しておく
        ConstraintUtil.remove_ik_and_target(armature, end_bone)

        # パラメータ取得
        level = self.check_level_distance(root_bone, end_bone)
        size = context.scene.AHT_ik_target_size

        # 生成するBone名
        ik_target_bone_name = Naming.make_ik_target_bone_name(end_bone.name)

        # ターゲットボーンセットアップ
        bpy.ops.object.mode_set(mode='EDIT')
        new_edit_bone = armature.data.edit_bones.new(name=ik_target_bone_name)
        new_edit_bone.head = end_bone.tail
        new_edit_bone.tail = end_bone.tail+mathutils.Vector((0,0,-size))
        new_edit_bone.use_deform = False
        new_edit_bone.parent = armature.data.edit_bones.get(root_parent.name)
 
        bpy.ops.object.mode_set(mode='POSE')

        # IK constraintの追加
        ConstraintUtil.add_ik(armature, end_bone, ik_target_bone_name, level)


    # end_boneからroot_boneまでの距離を計算
    def check_level_distance(self, root_bone, end_bone, level=1):
        if end_bone.name == root_bone.name:
            return level
        if end_bone.parent == None:
            return -1
        return self.check_level_distance(root_bone, end_bone.parent, level+1)


# IK Remove
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_ik_remove(bpy.types.Operator):
    bl_idname = "anime_hair_tools.ik_remove"
    bl_label = "IK Remove"

    # execute ok
    def execute(self, context):
        armature = context.active_object

        # 警告がでてしまうので、IK Constraintを先に消す
        subtargets = []
        for pose_bone in context.selected_pose_bones:
            subtargets += ConstraintUtil.remove_ik(armature, pose_bone)

        # TargetBoneの回収
        for pose_bone in context.selected_pose_bones:
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
def ui_draw(context, layout):
    layout.label(text="IK Setup:")
    box = layout.box()
    box.prop(context.scene, "AHT_ik_target_size", text="IK Target Size")
    box.operator("anime_hair_tools.ik_setup")
    box.operator("anime_hair_tools.ik_remove")
    box = layout.box()
    box.operator("anime_hair_tools.ik_enable")
    box.operator("anime_hair_tools.ik_disable")


# =================================================================================================
def register():
    # Bone設定
    bpy.types.Scene.AHT_ik_target_size = bpy.props.FloatProperty(name = "IK Target Size", default=1.0)