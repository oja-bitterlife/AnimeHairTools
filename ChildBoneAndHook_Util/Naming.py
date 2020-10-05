# Naming Utility

# base define
# =================================================================================================
# ChildBone
HOOK_BONE_PREFIX = "AHT_HookBone"
HOOK_BONE_SEPALATER = "@"

# Hook Modifire
HOOK_MODIFIRE_PREFIX = "AHT_HookModifire"
HOOK_MODIFIRE_SEPALATER = "@"


# name utility
# =================================================================================================
# ChildBone
# *****************************************************************************
def make_bone_basename(base_name):
    return HOOK_BONE_PREFIX + "." + base_name

def make_bone_name(base_name, spline_no, point_no):
    return make_bone_basename(base_name) + HOOK_BONE_SEPALATER + "{}.{:0=3}".format(spline_no, point_no)


# Hook Modifire
# *****************************************************************************
def make_modifier_basename(base_name):
    return HOOK_MODIFIRE_PREFIX + "." + base_name

def make_modifier_name(base_name, spline_no, point_no):
    return make_modifier_basename(base_name) + HOOK_MODIFIRE_SEPALATER + "{}.{:0=3}".format(spline_no, point_no)
