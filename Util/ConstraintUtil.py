from . import Naming


# *****************************************************************************
# pose_boneのlocationを固定する
def add_limit_location(pose_bone):
    constraint = pose_bone.constraints.new("LIMIT_LOCATION")
    constraint.name = Naming.make_constraint_name("lim_loc_" + pose_bone.name)
    constraint.owner_space = 'LOCAL'
    constraint.use_min_x = True
    constraint.use_min_y = True
    constraint.use_min_z = True
    constraint.use_max_x = True
    constraint.use_max_y = True
    constraint.use_max_z = True


def remove_all(pose_bone):
    for constraint in pose_bone.constraints:
        if constraint.name.startswith(Naming.CONSTRAINT_PREFIX):
            pose_bone.constraints.remove(constraint)


# IK用
# *****************************************************************************
def add_ik(armature, setup_pose_bone, ik_target_name, level):
    # ２重登録しないように
    remove_ik(setup_pose_bone)
    # 新規
    constraint = setup_pose_bone.constraints.new("IK")
    constraint.name = Naming.make_constraint_name("ik_" + setup_pose_bone.name)
    constraint.chain_count = level
    constraint.target = armature    
    constraint.subtarget = ik_target_name

def remove_ik(pose_bone):
    for constraint in pose_bone.constraints:
        if constraint.name.startswith(Naming.CONSTRAINT_PREFIX + "ik_"):
            pose_bone.constraints.remove(constraint)

