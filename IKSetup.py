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
            # 終端を探す
            children_list = BoneManager.pose_bone_gather_children(root_bone)
            for child in children_list:
                # 終端だったらセットアップ
                if len(child.children) == 0:
                    self.IK_setup(context, armature, root_bone, child)
        return {'FINISHED'}

    def IK_setup(self, context, armature, root_bone, end_bone):
        # パラメータ取得
        level = self.check_level_distance(root_bone, end_bone)
        size = context.scene.AHT_ik_target_size

        # 生成するBone名
        ik_target_bone_name = Naming.make_ik_target_bone_name(end_bone.name)

        bpy.ops.object.mode_set(mode='EDIT')
        new_bone = armature.data.edit_bones.new(name=ik_target_bone_name)
        new_bone.head = end_bone.tail
        new_bone.tail = end_bone.tail+mathutils.Vector((0,0,-size))
 
        bpy.ops.object.mode_set(mode='POSE')

        # IK constraintの設定
        ConstraintUtil.add_ik(armature, end_bone, new_bone, level)


    # end_boneからroot_boneまでの距離を計算
    def check_level_distance(self, root_bone, end_bone, level=1):
        if end_bone.name == root_bone.name:
            return level
        if end_bone.parent == None:
            return -1
        return self.check_level_distance(root_bone, end_bone.parent, level+1)


# IK Setup
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_ik_remove(bpy.types.Operator):
    bl_idname = "anime_hair_tools.ik_remove"
    bl_label = "IK Remove"

    # execute ok
    def execute(self, context):
        armature = context.active_object
        # 選択中のボーンでAHTのIK用に作られたものを消す
        for pose_bone in context.selected_pose_bones:
            self.IK_remove(armature, pose_bone)
        return {'FINISHED'}

    def IK_remove(self, armature, pose_bone):
        # IK constraintを削除
        ConstraintUtil.remove_ik(pose_bone)

        # constraint_target_boneも削除
        if pose_bone.name.startswith(Naming.IK_TARGET_BONE_PREFIX):
            remove_bone_from_pose(armature, pose_bone)


# POSEモードのpose_boneからedit_boneを削除する
def remove_bone_from_pose(armature, pose_bone):
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bone = armature.data.edit_bones[pose_bone.name]
    armature.data.edit_bones.remove(edit_bone)
    bpy.ops.object.mode_set(mode='POSE')


# UI描画設定
# =================================================================================================
def ui_draw(context, layout):
    layout.label(text="IK Setup:")
    box = layout.box()
    box.prop(context.scene, "AHT_ik_target_size", text="IK Target Size")
    box.operator("anime_hair_tools.ik_setup")
    box.operator("anime_hair_tools.ik_remove")


# =================================================================================================
def register():
    # Bone設定
    bpy.types.Scene.AHT_ik_target_size = bpy.props.FloatProperty(name = "IK Target Size", default=1.0)
