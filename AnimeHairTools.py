import bpy, math
from mathutils import Vector

from . import ArmatureManager, ChildBoneManager


# curve functions
# ===========================================================================================
# return the selected cuve objects
def get_selected_curve_objects():
    selected_curves = {}
    for object in bpy.context.selected_objects:
        if( object.type == "CURVE" ):
            selected_curves[object.name] = object
    return selected_curves


# return the all (users > 0) curve objects
def get_available_curve_objects():
    available_curves = {}
    for collection in bpy.data.collections:
        for object in collection.objects:
            if( object.type == "CURVE" ):
                available_curves[object.name] = object
    return available_curves

# apply callback at each curves
def apply_each_curves(selected_curves, callback):
    for curve_name in selected_curves:
        curve = selected_curves[curve_name]
        callback(curve)


# return points in curve
def get_curve_all_points(curve):
    # probably spline points is [0] only
    return curve.data.splines[0].points



# add bone and hook
# ===========================================================================================
# *******************************************************************************************
ANIME_HAIR_TOOLS_ARMATURE_NAME = "AHT_Armature"
ANIME_HAIR_TOOLS_ROOTBONE_NAME = "AHT_RootBone"


# create hook modifiers
# -------------------------------------------------------------------------------------------
class ANIME_HAIR_TOOLS_create_hook:
    @classmethod
    def create_modifier_name(cls, base_name, no):
        return base_name + ".hook_modifier.{:0=3}".format(no)

    def __init__(self, selected_curves):
        self.selected_curves = selected_curves

    # execute create constraints
    def execute(self, context):
        # create hook modifiers
        apply_each_curves(self.selected_curves, self.create_modifiers)

        # assign point to modifier
        apply_each_curves(self.selected_curves, self.assign_points)

        return{'FINISHED'}

    # create modifier
    def _create_modifier(self, segment_count, curve, no):
        hook_name = ANIME_HAIR_TOOLS_create_hook.create_modifier_name(curve.name, no)

        # create not exists hook modifier
        if hook_name not in curve.modifiers.keys():
            curve.modifiers.new(hook_name, type="HOOK")

        # (re)setup
        # -------------------------------------------------------------------------
        modifier = curve.modifiers[hook_name]

        modifier.object = bpy.data.objects[ANIME_HAIR_TOOLS_ARMATURE_NAME]
        if(segment_count-1 <= no):
            no = segment_count-2  # edge limit
#        modifier.subtarget = ANIME_HAIR_TOOLS_create_bone.create_bone_name(curve.name, no)
        ChildBone.create(bpy.context)

        return modifier

    # create modifier every segment and sort
    def create_modifiers(self, curve):
        # get segment locations in curve
        points = get_curve_all_points(curve)
        segment_count = len(points)  # bettween points

        # create modifier for segment
        for i in range(segment_count-1, -1, -1):  # asc sorting
            modifier = self._create_modifier(segment_count, curve, i)

            # sort modifier
            # -------------------------------------------------------------------------
            move_up_count = curve.modifiers.keys().index(modifier.name)

            bpy.context.view_layer.objects.active = curve  # for modifier_move_up
            for j in range(move_up_count):
                bpy.ops.object.modifier_move_up(modifier=modifier.name)

    def assign_points(self, curve):
        # assign segment
        bpy.context.view_layer.objects.active = curve
        bpy.ops.object.mode_set(mode='EDIT')

        # get points in edit mode
        segment_count = len(get_curve_all_points(curve))  # bettween points

        # assign hook
        for segment_no in range(segment_count):
            # need for each assign
            hook_points = get_curve_all_points(curve)

            # select is only assign target point
            for point_no, p in enumerate(hook_points):
                p.select = segment_no == point_no
                
            # assign to modifier
            hook_name = ANIME_HAIR_TOOLS_create_hook.create_modifier_name(curve.name, segment_no)
            bpy.ops.object.hook_assign(modifier=hook_name)

        bpy.ops.object.mode_set(mode='OBJECT')

# create constraint
# -------------------------------------------------------------------------------------------
class ANIME_HAIR_TOOLS_create_constraint:
    @classmethod
    def create_modifier_name(cls, base_name, no):
        return base_name + ".hook_modifier.{:0=3}".format(no)

    def __init__(self, selected_curves):
        self.selected_curves = selected_curves


    # execute create constraints
    def execute(self, context):
        # create hook modifiers
        apply_each_curves(self.selected_curves, self.create_constraint)

    # add constraint to root_bone
    def create_constraint(self, curve):
        if "AHT_rotation" not in curve.constraints:
            constraint = curve.constraints.new('COPY_ROTATION')
            constraint.name = "AHT_rotation"
            constraint.target = bpy.data.objects[ANIME_HAIR_TOOLS_ARMATURE_NAME]
            constraint.subtarget = ANIME_HAIR_TOOLS_ROOTBONE_NAME


# Main UI
# ===========================================================================================
NOTHING_ENUM = "(nothing)"  # noting selected item
REMOVE_ENUM = "(remove setted object)"  # noting selected item

# 3DView Tools Panel
class ANIME_HAIR_TOOLS_PT_ui(bpy.types.Panel):
    bl_label = "Anime Hair Tools (for Curve)"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AHT"
  
    def draw(self, context):
        ArmatureManager.ui_draw(context, self.layout)
        ChildBoneManager.ui_draw(context, self.layout)

    # オブジェクトモード時のみ利用可能に
    @classmethod
    def poll(cls, context):
        return (context.mode == "OBJECT")
