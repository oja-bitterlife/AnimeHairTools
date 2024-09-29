# Naming Utility

# name utility
# =================================================================================================
# Bone
# *****************************************************************************
BONE_PREFIX = "AHT_Hair@"

def make_bone_basename(curve_name):
    return BONE_PREFIX + curve_name + "@"

def make_bone_name(curve_name, spline_no, point_no, LR=None):
    if LR == None:
        return make_bone_basename(curve_name) + "{:0=3}.{:0=3}".format(spline_no, point_no)
    else:
        return make_bone_basename(curve_name) + "{:0=3}.{:0=3}.{}".format(spline_no, point_no, LR)


# Bone Collection
# *****************************************************************************
BONE_COLLECTION_PREFIX = "AHT_Bones_"

def make_bone_collection_name(collection_name):
    return BONE_COLLECTION_PREFIX + collection_name


# Constraint
# *****************************************************************************
CONSTRAINT_PREFIX = "AHT_const_"

def make_constraint_name(base_name):
    return CONSTRAINT_PREFIX + base_name
