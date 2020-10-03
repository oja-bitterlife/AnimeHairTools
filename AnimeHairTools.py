import bpy, math
from mathutils import Vector

from . import ArmatureManager


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

# create bones with armature
# -------------------------------------------------------------------------------------------
class ANIME_HAIR_TOOLS_create_bone:
    @classmethod
    def create_bone_name(cls, base_name, no):
        return base_name + ".hook_bone.{:0=3}".format(no)

    def __init__(self, selected_curves):
        self.selected_curves = selected_curves

    # execute create auto-hook-bones
    def execute(self, context):
        self.root_armature = bpy.data.objects[context.scene.AHT_armature_name]

        # create bones for each selected curves
        apply_each_curves(self.selected_curves, self.create_bones)

        return{'FINISHED'}

    # create bone for selected curves
    def create_bones(self, curve):
        # to edit-mode
        bpy.context.view_layer.objects.active = self.root_armature
        bpy.ops.object.mode_set(mode='EDIT')

        # get points in edit mode
        hook_points = get_curve_all_points(curve)

        # create bone chain
        # -------------------------------------------------------------------------
        root_matrix = self.root_armature.matrix_world.inverted() @ curve.matrix_world

        parent = None  # hair root is free
        for i in range(len(hook_points)-1):
            bgn = root_matrix @ hook_points[i].co
            end = root_matrix @ hook_points[i+1].co
            parent = self._create_child_bone(curve.name, i, parent, bgn, end)

        bpy.ops.object.mode_set(mode='OBJECT')

    # create chain child bone
    def _create_child_bone(self, base_name, i, parent, bgn, end):
        bone_name = ANIME_HAIR_TOOLS_create_bone.create_bone_name(base_name, i)

        # create bone if not exists
        # -------------------------------------------------------------------------
        if bone_name not in self.root_armature.data.bones.keys():
            bpy.ops.armature.bone_primitive_add(name=bone_name)

        # (re)setup
        # -------------------------------------------------------------------------
        child_bone = self.root_armature.data.edit_bones[bone_name]

        child_bone.parent = parent
        child_bone.use_connect = i != 0  # not connect to root
        if i == 0:
            child_bone.head = bgn.xyz  # disconnected head setup
        child_bone.tail = end.xyz
    
        return child_bone

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
            curve.modifiers.new(hook_name, type="HOOK");

        # (re)setup
        # -------------------------------------------------------------------------
        modifier = curve.modifiers[hook_name]

        modifier.object = bpy.data.objects[ANIME_HAIR_TOOLS_ARMATURE_NAME]
        if(segment_count-1 <= no):
            no = segment_count-2  # edge limit
        modifier.subtarget = ANIME_HAIR_TOOLS_create_bone.create_bone_name(curve.name, no)

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
            constraint.name = "AHT_rotation";
            constraint.target = bpy.data.objects[ANIME_HAIR_TOOLS_ARMATURE_NAME]
            constraint.subtarget = ANIME_HAIR_TOOLS_ROOTBONE_NAME

# create constraints and controll bone
# -------------------------------------------------------------------------------------------
class ANIME_HAIR_TOOLS_OT_create_bone_and_hook(bpy.types.Operator):
    bl_idname = "anime_hair_tools.create_bone_and_hook"
    bl_label = "Create Bone and Hook"

    # execute ok
    def execute(self, context):
        # no active object
        if bpy.context.view_layer.objects.active == None:
            return{'FINISHED'}

        backup_active_object = bpy.context.view_layer.objects.active

        bpy.ops.object.mode_set(mode='OBJECT')
        selected_curves = get_selected_curve_objects()
        
        # create bones
        ANIME_HAIR_TOOLS_create_bone(selected_curves).execute(context)

        # create hook
        ANIME_HAIR_TOOLS_create_hook(selected_curves).execute(context)

        # create constraint
        ANIME_HAIR_TOOLS_create_constraint(selected_curves).execute(context)

        # restore active object
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = backup_active_object

        return{'FINISHED'}

    # use dialog
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# Delete the constraints added for management
# *******************************************************************************************
class ANIME_HAIR_TOOLS_OT_remove_bone_and_hook(bpy.types.Operator):
    bl_idname = "anime_hair_tools.remove_bone_and_hook"
    bl_label = "Remove AHT Bone and Hook"

    # execute ok
    def execute(self, context):
        # no active object
        if bpy.context.view_layer.objects.active == None:
            return{'FINISHED'}

        backup_active_object = bpy.context.view_layer.objects.active

        bpy.ops.object.mode_set(mode='OBJECT')

        selected_curves = get_selected_curve_objects()

        # remove added constraints
        apply_each_curves(selected_curves, self.remove_constraints)

        # remove added modifiers
        apply_each_curves(selected_curves, self.remove_modifiers)

        # remove added bones
        apply_each_curves(selected_curves, self.remove_bones)

        # restore active object
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = backup_active_object

        return{'FINISHED'}

    # remove all constraint
    def remove_constraints(self, curve):
        c = curve.constraints["AHT_rotation"]
        curve.constraints.remove(c)

    # remove all hook modifiers
    def remove_modifiers(self, curve):
        bpy.context.view_layer.objects.active = curve

        # create remove name
        hook_name = ANIME_HAIR_TOOLS_create_hook.create_modifier_name(curve.name, 0)
        hook_name_base = hook_name[:-4]  # remove .000

        # remove
        for modifier in curve.modifiers:
            if modifier.name.startswith(hook_name_base):
                bpy.ops.object.modifier_remove(modifier=modifier.name)

    # remove all hook bones
    def remove_bones(self, curve):
        root_armature = None
        if ANIME_HAIR_TOOLS_ARMATURE_NAME in bpy.data.objects.keys():
            root_armature = bpy.data.objects[ANIME_HAIR_TOOLS_ARMATURE_NAME]

        # if not exists noting to do
        if root_armature == None:
            return

        # to edit-mode
        bpy.context.view_layer.objects.active = root_armature
        bpy.ops.object.mode_set(mode='EDIT')

        # create remove name
        bone_name = ANIME_HAIR_TOOLS_create_bone.create_bone_name(curve.name, 0)
        bone_name_base = bone_name[:-4]  # remove .000

        # select remove target bones
        bpy.ops.armature.select_all(action='DESELECT')
        for edit_bone in root_armature.data.edit_bones:
            if edit_bone.name.startswith(bone_name_base):
                edit_bone.select = True

        # remove selected bones
        bpy.ops.armature.delete()

        # out of edit-mode
        bpy.ops.object.mode_set(mode='OBJECT')

    # use dialog
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


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

        self.layout.operator("anime_hair_tools.create_bone_and_hook")
        self.layout.operator("anime_hair_tools.remove_bone_and_hook")


