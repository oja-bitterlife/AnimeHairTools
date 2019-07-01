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

# find/create bone root for anime hair tools
def setup_root_bone_object():
    # already created
    if ANIME_HAIR_TOOLS_BONE_OBJ_NAME in bpy.data.objects.keys():
        return bpy.data.objects[ANIME_HAIR_TOOLS_BONE_OBJ_NAME]

    # create new bone
    bpy.ops.object.armature_add(enter_editmode=False, location=(0, 0, 0))

    # set name
    bpy.context.active_object.name = ANIME_HAIR_TOOLS_BONE_OBJ_NAME
    bpy.context.active_object.data.name = ANIME_HAIR_TOOLS_BONE_OBJ_NAME
    bpy.context.active_object.data.bones[0].name = ANIME_HAIR_TOOLS_BONE_ROOT_NAME

    # other setup
    bpy.context.active_object.show_in_front = True
    bpy.context.active_object.data.display_type = 'STICK'

    return bpy.context.active_object


# create auto hook bones
class ANIME_HAIR_TOOLS_OT_auto_hook(bpy.types.Operator):
    bl_idname = "anime_hair_tools.auto_hook"
    bl_label = "Create Auto Hook Bones"

    # execute ok
    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        selected_curves = get_selected_curve_objects()

        # save active object
        backup_active_object = bpy.context.active_object

        # bone
        root_bone_obj = setup_root_bone_object()

        # bone setup is edit-mode only
        bpy.context.view_layer.objects.active = root_bone_obj
        bpy.ops.object.mode_set(mode='EDIT')

        # set bone to selected curves
        for curve_name in selected_curves:
            curve = selected_curves[curve_name]  # process curve

            # get segment locations in curve
            hook_points = self.get_hook_points(curve)

            parent = root_bone_obj.data.edit_bones[0]  # find first bone
            for i in range(len(hook_points)-1):
                bgn = curve.matrix_world @ hook_points[i].co
                end = curve.matrix_world @ hook_points[i+1].co
                parent = self.create_child_bone(curve.name, i, root_bone_obj, parent, bgn, end)

        # convirm edit_bone
        bpy.ops.object.mode_set(mode='OBJECT')

        # set hook to selected curves
        for curve_name in selected_curves:
            curve = selected_curves[curve_name]  # process curve

            # get segment locations in curve
            hook_points = self.get_hook_points(curve)

            for modifire_no in range(len(hook_points)-1):
                self.create_hook(curve, modifire_no)

        # restore active object
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = backup_active_object

        return{'FINISHED'}

    # use dialog
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


    # return points in curve
    def get_hook_points(self, curve):
        # stock hook points
        hook_points = []

        # process splines
        for spline in curve.data.splines:
            # process spline points
            for point in spline.points:
                hook_points.append(point)

            # process bezier points
            for point in spline.bezier_points:
                hook_points.append(point)
    
        return hook_points

    def create_child_bone(self, base_name, i, root_bone_obj, parent, bgn, end):
        bone_name = base_name + ".hook_bone.{:0=3}".format(i)
    
        # create non exist bone
        if bone_name not in root_bone_obj.data.bones.keys():
            bpy.ops.armature.bone_primitive_add(name=bone_name)

        # find bone
        child_bone = root_bone_obj.data.edit_bones[bone_name]

        # setup
        child_bone.parent = parent
        child_bone.use_connect = i != 0  # no connect to root
        if i == 0:
            child_bone.head = bgn.xyz  # disconnected head setup
        child_bone.tail = end.xyz

        return child_bone

    def create_hook(self, curve, modifire_no):
        hook_name = curve.name + ".hook_modifier.{:0=3}".format(modifire_no)
        bone_name = curve.name + ".hook_bone.{:0=3}".format(modifire_no)

        # create hook modifier
        if hook_name not in curve.modifiers.keys():
            curve.modifiers.new(hook_name, type="HOOK");

        # modifier setup
        modifier = curve.modifiers[hook_name]

        modifier.object = bpy.data.objects[ANIME_HAIR_TOOLS_BONE_OBJ_NAME]
        modifier.subtarget = bone_name

        # assign segment
        bpy.context.view_layer.objects.active = curve
        bpy.ops.object.mode_set(mode='EDIT')

        # get points in edit mode
        hook_points = self.get_hook_points(curve)

        # assign hook
        for p_no, p in enumerate(hook_points):
            p.select = p_no == modifire_no+1
        bpy.ops.object.hook_assign(modifier=modifier.name)

        bpy.ops.object.mode_set(mode='OBJECT')


# retister blender
# *******************************************************************************************
classes = (
    ANIME_HAIR_TOOLS_PT_ui,
    ANIME_HAIR_TOOLS_OT_bevel_taper,
    ANIME_HAIR_TOOLS_OT_material,
    ANIME_HAIR_TOOLS_OT_auto_hook,
)

for cls in classes:
    bpy.utils.register_class(cls)
