import bpy

from ..Util import Naming

# IK用
# *****************************************************************************
def add_ik(armature, setup_pose_bone, ik_target_name, level):
    # 新規
    constraint = setup_pose_bone.constraints.new("IK")
    constraint.name = Naming.make_constraint_name("ik_" + setup_pose_bone.name)
    constraint.chain_count = level
    constraint.target = armature    
    constraint.subtarget = ik_target_name


# IK Constraintを消す。ついでにTargetBoneも消す
def remove_ik(armature, pose_bone):
    # IK Constraintの削除
    subtargets = []
    for constraint in pose_bone.constraints:
        if constraint.name.startswith(Naming.CONSTRAINT_PREFIX + "ik_"):
            subtargets.append(constraint.subtarget)
            pose_bone.constraints.remove(constraint)

    return subtargets

