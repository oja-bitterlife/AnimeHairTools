# Naming Utility

# base define
# =================================================================================================
# ChildBone
BONE_SEPALATER = "@"
BONE_SUFFIX = "bone"

# Mesh
MESH_SEPALATER = "@"
MESH_SUFFIX = "mesh"


# name utility
# =================================================================================================
# Bone
# *****************************************************************************
def make_bone_basename(base_name):
    return base_name + BONE_SEPALATER + BONE_SUFFIX

def make_bone_name(base_name, spline_no, point_no, LR=None):
    if LR == None:
        return make_bone_basename(base_name) + "-{:0=3}.{:0=3}".format(spline_no, point_no)
    else:
        return make_bone_basename(base_name) + "-{:0=3}.{:0=3}.{}".format(spline_no, point_no, LR)


# Mesh
# *****************************************************************************
def make_mesh_name(base_name):
    return base_name + MESH_SEPALATER + MESH_SUFFIX

def make_tmp_mesh_name(base_name, spline_no, LR=None):
    return make_mesh_name(base_name) + ".{:0=3}".format(spline_no)
