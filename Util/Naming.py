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

def make_bone_collection_name(collection_name):
    return "AHT_Bones_" + collection_name

# IK_TARGET_BONE_PREFIX = "AHT_ik_target_"
# def make_ik_target_bone_name(base_name):
#     return IK_TARGET_BONE_PREFIX + base_name


# Constraint
# *****************************************************************************
CONSTRAINT_PREFIX = "AHT_const_"

def make_constraint_name(base_name):
    return CONSTRAINT_PREFIX+base_name


# VertexGroup
# *****************************************************************************
# その頂点がどのBoneに影響されるかを保存するVertexGroupにつける名前(テンポラリ)
AHT_BONE_GEN_INFO_NAME = "AHT_MARK_BONE"
def get_bone_gen_info_name(point_no):
    return AHT_BONE_GEN_INFO_NAME + "_%d" % point_no
