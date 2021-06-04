# Naming Utility

# base define
# =================================================================================================
# ChildBone
BONE_PREFIX = "AHT_Bone"
BONE_SEPALATER = "@"

# Mesh
MESH_SUFFIX = "@mesh"


# name utility
# =================================================================================================
# Bone
# *****************************************************************************
def make_bone_basename(base_name):
    return BONE_PREFIX + "." + base_name

def make_bone_name(base_name, spline_no, point_no):
    return make_bone_basename(base_name) + BONE_SEPALATER + "{}.{:0=3}".format(spline_no, point_no)


# Mesh
# *****************************************************************************
def make_mesh_basename(base_name):
    return base_name + MESH_SUFFIX

def make_tmp_mesh_name(base_name, spline_no):
    return make_mesh_basename(base_name) + ".{:0=3}".format(spline_no)
