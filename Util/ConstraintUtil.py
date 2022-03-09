# pose_boneのlocationを固定する
def add_limit_location(pose_bone):
    constraint = pose_bone.constraints.new("LIMIT_LOCATION")
    constraint.owner_space = 'LOCAL'
    constraint.use_min_x = True
    constraint.use_min_y = True
    constraint.use_min_z = True
    constraint.use_max_x = True
    constraint.use_max_y = True
    constraint.use_max_z = True
