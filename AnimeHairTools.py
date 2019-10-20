import bpy
from mathutils import Vector

# curve pickup functions
# *******************************************************************************************
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


# Main UI
# *******************************************************************************************
NOTHING_ENUM = "(nothing)"  # noting selected item
REMOVE_ENUM = "(remove setted object)"  # noting selected item

# 3DView Tools Panel
class ANIME_HAIR_TOOLS_PT_ui(bpy.types.Panel):
    bl_label = "Anime Hair Tools (for Curve)"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
  
    def draw(self, context):
        self.layout.operator("anime_hair_tools.bevel_taper")
        self.layout.operator("anime_hair_tools.material")
        self.layout.operator("anime_hair_tools.auto_hook")
        self.layout.operator("anime_hair_tools.remove_settings")


# Bebel & Taper Setting
# *******************************************************************************************
# find all curves for enum item
def create_curve_enum_items(self, context):
    curve_enum = [
        (NOTHING_ENUM, NOTHING_ENUM, ""),
        (REMOVE_ENUM, REMOVE_ENUM, ""),
    ]

    available_curves = get_available_curve_objects()
    for curve_name in available_curves:
        curve = available_curves[curve_name]
        curve_enum.append((curve.name, curve.name, ""))

    return curve_enum

class ANIME_HAIR_TOOLS_OT_bevel_taper(bpy.types.Operator):
    bl_idname = "anime_hair_tools.bevel_taper"
    bl_label = "Bevel & Taper Setting"

    # create curve enum list
    selected_bevel: bpy.props.EnumProperty(name="Bevel Curve", items=create_curve_enum_items)
    selected_taper: bpy.props.EnumProperty(name="Taper Curve", items=create_curve_enum_items)

    # execute ok
    def execute(self, context):
        # no active object
        if bpy.context.view_layer.objects.active == None:
            return{'FINISHED'}

        bpy.ops.object.mode_set(mode='OBJECT')
        selected_curves = get_selected_curve_objects()

        # enum selected
        available_curves = get_available_curve_objects()

        # set bevel & taper to selected curves
        for curve_name in selected_curves:
            curve = selected_curves[curve_name]

            # set selected bevel
            if curve.name != self.selected_bevel:  # not set myself
                if self.selected_bevel == NOTHING_ENUM:
                    pass
                elif self.selected_bevel == REMOVE_ENUM:
                    curve.data.bevel_object = None
                else:
                    curve.data.bevel_object = available_curves[self.selected_bevel]

            # set selected taper
            if curve.name != self.selected_taper:  # no set myself
                if self.selected_taper == NOTHING_ENUM:
                    pass
                elif self.selected_taper == REMOVE_ENUM:
                    curve.data.taper_object = None
                else:
                    curve.data.taper_object = available_curves[self.selected_taper]


        return{'FINISHED'}

    # use dialog
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# Material Setting
# *******************************************************************************************
# find all curves for enum item
def create_material_enum_items(self, context):
    material_enum = []

    for material in bpy.data.materials:
        material_enum.append( (material.name, material.name, "") )

    return material_enum

class ANIME_HAIR_TOOLS_OT_material(bpy.types.Operator):
    bl_idname = "anime_hair_tools.material"
    bl_label = "Material Setting"

    # create material enum list
    selected_material: bpy.props.EnumProperty(name="Material", items=create_material_enum_items)

    # execute ok
    def execute(self, context):
        # no active object
        if bpy.context.view_layer.objects.active == None:
            return{'FINISHED'}

        bpy.ops.object.mode_set(mode='OBJECT')
        selected_curves = get_selected_curve_objects()

        # save active object
        backup_active_object = bpy.context.active_object

        # set material to selected curves
        for curve_name in selected_curves:
            curve = selected_curves[curve_name]  # process curve
            selected_material_data = bpy.data.materials[self.selected_material]

            # already in use?
            use_slot_index = -1
            for i, material in enumerate(curve.data.materials):
                if material.name == selected_material_data.name:
                    use_slot_index = i  # find already used
                    break

            # first appear
            if use_slot_index == -1:
                # create slot
                bpy.context.view_layer.objects.active = curve
                bpy.ops.object.material_slot_add()

                # set material to empty slot
                use_slot_index = len(curve.material_slots)-1
                curve.data.materials[use_slot_index] = selected_material_data

            # apply material (select slot) to spline
            for spline in curve.data.splines:
                spline.material_index = use_slot_index

        # restore active object
        bpy.context.view_layer.objects.active = backup_active_object

        return{'FINISHED'}

    # use dialog
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# add hook object
# *******************************************************************************************
ANIME_HAIR_TOOLS_BONE_OBJ_NAME = "AHT_Armature"
ANIME_HAIR_TOOLS_BONE_ROOT_NAME = "AHT_BoneRoot"

# return points in curve
def get_curve_all_points(curve):
    # stock hook points
    points = []

    # process only splines (not process bezier_points)
    for spline in curve.data.splines:
        # process spline points
        for point in spline.points:
            points.append(point)

    return points

# apply callback at each curves
def apply_each_curves(selected_curves, callback):
    for curve_name in selected_curves:
        curve = selected_curves[curve_name]
        callback(curve)


# create bones with armature
class ANIME_HAIR_TOOLS_auto_hook_bone:
    @classmethod
    def create_bone_name(cls, base_name, no):
        return base_name + ".hook_bone.{:0=3}".format(no)

    def __init__(self, selected_curves):
        self.selected_curves = selected_curves

    # execute create auto-hook-bones
    def execute(self, context):
        # create root Armature for aht-bones
        self.root_armature = self.create_root_armature()

        # create bones for each selected curves
        apply_each_curves(self.selected_curves, self.create_bones)

        return{'FINISHED'}


    # find/create bone root for anime hair tools
    def create_root_armature(self):
        # already created?
        # -------------------------------------------------------------------------
        if ANIME_HAIR_TOOLS_BONE_OBJ_NAME in bpy.data.objects.keys():
            return bpy.data.objects[ANIME_HAIR_TOOLS_BONE_OBJ_NAME]

        # create new bone
        # -------------------------------------------------------------------------
        bpy.ops.object.armature_add(enter_editmode=False, location=(0, 0, 0))
        root_armature = bpy.context.active_object

        # set name
        root_armature.name = ANIME_HAIR_TOOLS_BONE_OBJ_NAME
        root_armature.data.name = ANIME_HAIR_TOOLS_BONE_OBJ_NAME
        root_armature.data.bones[0].name = ANIME_HAIR_TOOLS_BONE_ROOT_NAME

        # other setup
        root_armature.show_in_front = True
        root_armature.data.display_type = 'STICK'

        return root_armature


    # create bone for selected curves
    def create_bones(self, curve):
        # to edit-mode
        bpy.context.view_layer.objects.active = self.root_armature
        bpy.ops.object.mode_set(mode='EDIT')

        # get points in edit mode
        hook_points = get_curve_all_points(curve)

        parent = self.root_armature.data.edit_bones[0]  # find first bone in edit-mode
        for i in range(len(hook_points)-1):
            bgn = curve.matrix_world @ hook_points[i].co
            end = curve.matrix_world @ hook_points[i+1].co
            parent = self._create_child_bone(curve.name, i, parent, bgn, end)

        # out of edit-mode
        bpy.ops.object.mode_set(mode='OBJECT')

    # create chain child bone
    def _create_child_bone(self, base_name, i, parent, bgn, end):
        bone_name = ANIME_HAIR_TOOLS_auto_hook_bone.create_bone_name(base_name, i)
    
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
class ANIME_HAIR_TOOLS_auto_hook_modifier:
    @classmethod
    def create_modifier_name(cls, base_name, no):
        return base_name + ".hook_modifier.{:0=3}".format(no)

    def __init__(self, selected_curves):
        self.selected_curves = selected_curves

    # execute create auto-hook-modifier
    def execute(self, context):
        # create hook modifiers
        apply_each_curves(self.selected_curves, self.create_modifiers)

        # assign point to modifier
        apply_each_curves(self.selected_curves, self.assign_points)

        return{'FINISHED'}



    # create modifier
    def _create_modifier(self, segment_count, curve, no):
        hook_name = ANIME_HAIR_TOOLS_auto_hook_modifier.create_modifier_name(curve.name, no)

        # create not exists hook modifier
        if hook_name not in curve.modifiers.keys():
            curve.modifiers.new(hook_name, type="HOOK");

        # (re)setup
        # -------------------------------------------------------------------------
        modifier = curve.modifiers[hook_name]

        modifier.object = bpy.data.objects[ANIME_HAIR_TOOLS_BONE_OBJ_NAME]
        if(segment_count-1 <= no):
            no = segment_count-2  # edge limit
        modifier.subtarget = ANIME_HAIR_TOOLS_auto_hook_bone.create_bone_name(curve.name, no)

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
        hook_points = get_curve_all_points(curve)
        segment_count = len(hook_points)  # bettween points

        # assign hook
        for segment_no in range(segment_count):
            # select is only assign target point
            for point_no, p in enumerate(hook_points):
                p.select = point_no == segment_no

            # assign to modifier
            hook_name = ANIME_HAIR_TOOLS_auto_hook_modifier.create_modifier_name(curve.name, segment_no)
            bpy.ops.object.hook_assign(modifier=hook_name)

        bpy.ops.object.mode_set(mode='OBJECT')


# create auto hook bones
class ANIME_HAIR_TOOLS_OT_auto_hook(bpy.types.Operator):
    bl_idname = "anime_hair_tools.auto_hook"
    bl_label = "Create Auto Hook Bones"

    # execute ok
    def execute(self, context):
        # no active object
        if bpy.context.view_layer.objects.active == None:
            return{'FINISHED'}

        backup_active_object = bpy.context.view_layer.objects.active

        bpy.ops.object.mode_set(mode='OBJECT')
        selected_curves = get_selected_curve_objects()
        
        # create bones
        ANIME_HAIR_TOOLS_auto_hook_bone(selected_curves).execute(context)

        # create hook
        ANIME_HAIR_TOOLS_auto_hook_modifier(selected_curves).execute(context)

        # restore active object
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = backup_active_object

        return{'FINISHED'}

    # use dialog
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# Delete the setting added for management
class ANIME_HAIR_TOOLS_OT_remove_settings(bpy.types.Operator):
    bl_idname = "anime_hair_tools.remove_settings"
    bl_label = "Remove AHT Settings"

    # execute ok
    def execute(self, context):
        # no active object
        if bpy.context.view_layer.objects.active == None:
            return{'FINISHED'}

        backup_active_object = bpy.context.view_layer.objects.active

        bpy.ops.object.mode_set(mode='OBJECT')
        selected_curves = get_selected_curve_objects()

        # remove added modifiers
        apply_each_curves(selected_curves, self.remove_modifiers)

        # remove added bones
        apply_each_curves(selected_curves, self.remove_bones)

        # restore active object
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = backup_active_object

        return{'FINISHED'}

    # remove all hook modifiers
    def remove_modifiers(self, curve):
        bpy.context.view_layer.objects.active = curve

        # create remove name
        hook_name = ANIME_HAIR_TOOLS_auto_hook_modifier.create_modifier_name(curve.name, 0)
        hook_name_base = hook_name[:-4]  # remove .000

        # remove
        for modifier in curve.modifiers:
            if modifier.name.startswith(hook_name_base):
                bpy.ops.object.modifier_remove(modifier=modifier.name)
        
    # remove all hook bones
    def remove_bones(self, curve):
        root_armature = None
        if ANIME_HAIR_TOOLS_BONE_OBJ_NAME in bpy.data.objects.keys():
            root_armature = bpy.data.objects[ANIME_HAIR_TOOLS_BONE_OBJ_NAME]

        # if not exists noting to do
        if root_armature == None:
            return

        # to edit-mode
        bpy.context.view_layer.objects.active = root_armature
        bpy.ops.object.mode_set(mode='EDIT')

        # create remove name
        bone_name = ANIME_HAIR_TOOLS_auto_hook_bone.create_bone_name(curve.name, 0)
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


# retister blender
# *******************************************************************************************
classes = (
    ANIME_HAIR_TOOLS_PT_ui,
    ANIME_HAIR_TOOLS_OT_bevel_taper,
    ANIME_HAIR_TOOLS_OT_material,
    ANIME_HAIR_TOOLS_OT_auto_hook,
    ANIME_HAIR_TOOLS_OT_remove_settings,
)

for cls in classes:
    bpy.utils.register_class(cls)
