import bpy, math
from mathutils import Vector

# curve functions
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

# apply callback at each curves
def apply_each_curves(selected_curves, callback):
    for curve_name in selected_curves:
        curve = selected_curves[curve_name]
        callback(curve)


# Main UI
# *******************************************************************************************
NOTHING_ENUM = "(nothing)"  # noting selected item
REMOVE_ENUM = "(remove setted object)"  # noting selected item

# 3DView Tools Panel
class ANIME_HAIR_TOOLS_PT_ui(bpy.types.Panel):
    bl_label = "Anime Hair Tools (for Curve)"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AHT"
  
    def draw(self, context):
        self.layout.operator("anime_hair_tools.bevel_taper")
        self.layout.operator("anime_hair_tools.material")
        self.layout.operator("anime_hair_tools.create_bone_and_constraints")
        self.layout.operator("anime_hair_tools.remove_constraint")
        self.layout.operator("anime_hair_tools.add_shapekey")


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
ANIME_HAIR_TOOLS_ARMATURE_NAME = "AHT_Armature"
ANIME_HAIR_TOOLS_BONEROOT_NAME = "AHT_BoneRoot"

# create bones with armature
class ANIME_HAIR_TOOLS_create_bone:
    @classmethod
    def create_bone_name(cls, base_name, no):
        return base_name + ".hook_bone.{:0=3}".format(no)

    def __init__(self, selected_curves):
        self.selected_curves = selected_curves

    # execute create auto-hook-bones
    def execute(self, context):
        # create root Armature for aht-bones
        self.root_armature = self.create_root_armature()

        return{'FINISHED'}


    # find/create bone root for anime hair tools
    def create_root_armature(self):
        # already created?
        # -------------------------------------------------------------------------
        if ANIME_HAIR_TOOLS_ARMATURE_NAME in bpy.data.objects.keys():
            root_armature = bpy.data.objects[ANIME_HAIR_TOOLS_ARMATURE_NAME]
            return bpy.data.objects[ANIME_HAIR_TOOLS_ARMATURE_NAME]

        # create new bone
        # -------------------------------------------------------------------------
        bpy.ops.object.armature_add(enter_editmode=False, location=(0, 0, 0))
        root_armature = bpy.context.active_object

        # set name
        root_armature.name = ANIME_HAIR_TOOLS_ARMATURE_NAME
        root_armature.data.name = ANIME_HAIR_TOOLS_ARMATURE_NAME
        root_armature.data.bones[0].name = ANIME_HAIR_TOOLS_BONEROOT_NAME

        # other setup
        root_armature.show_in_front = True
        root_armature.data.display_type = 'STICK'

        # add constraint
        constraint = root_armature.constraints.new('COPY_LOCATION')
        constraint.name = "ATH_transform";
        constraint = root_armature.constraints.new('COPY_ROTATION')
        constraint.name = "ATH_rotation";

        # set transform
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = root_armature
        bpy.ops.object.mode_set(mode='EDIT')
        root_armature.data.edit_bones[0].select = True
        root_armature.data.edit_bones[0].tail = (0, 0, -1)
        bpy.ops.object.mode_set(mode='OBJECT')

        return root_armature



# create hook modifiers
class ANIME_HAIR_TOOLS_create_constraint:
    def __init__(self, selected_curves):
        self.selected_curves = selected_curves

    # execute create constraints
    def execute(self, context):
        # create translate constraint
        apply_each_curves(self.selected_curves, self.create_translate)

        # create rotation constraint
        apply_each_curves(self.selected_curves, self.create_rotate)

        return{'FINISHED'}


    # create translate constraint every cureve
    @classmethod
    def create_translate(cls, curve):
        # create 
        constraint = curve.constraints.new('COPY_LOCATION')

        # setting
        constraint.name = "ATH_transform";
        constraint.target = bpy.data.objects[ANIME_HAIR_TOOLS_ARMATURE_NAME]
        constraint.subtarget = ANIME_HAIR_TOOLS_BONEROOT_NAME

    # create rotate constraint every cureve
    @classmethod
    def create_rotate(cls, curve):
        # create 
        constraint = curve.constraints.new('COPY_ROTATION')

        # setting
        constraint.name = "ATH_rotation";
        constraint.target = bpy.data.objects[ANIME_HAIR_TOOLS_ARMATURE_NAME]
        constraint.subtarget = ANIME_HAIR_TOOLS_BONEROOT_NAME



# create constraints and controll bone
class ANIME_HAIR_TOOLS_OT_create_bone_and_constraint(bpy.types.Operator):
    bl_idname = "anime_hair_tools.create_bone_and_constraints"
    bl_label = "Create Bone and Constraint"

    # execute ok
    def execute(self, context):
        # no active object
        if bpy.context.view_layer.objects.active == None:
            return{'FINISHED'}

        backup_active_object = bpy.context.view_layer.objects.active

        bpy.ops.object.mode_set(mode='OBJECT')
        selected_curves = get_selected_curve_objects()

        # clear old constraints
        apply_each_curves(selected_curves, ANIME_HAIR_TOOLS_OT_remove_constraint.remove_constraints)
        
        # create bones
        ANIME_HAIR_TOOLS_create_bone(selected_curves).execute(context)

        # create hook
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
class ANIME_HAIR_TOOLS_OT_remove_constraint(bpy.types.Operator):
    bl_idname = "anime_hair_tools.remove_constraint"
    bl_label = "Remove AHT Constraints"

    # execute ok
    def execute(self, context):
        selected_curves = get_selected_curve_objects()

        # remove constraints
        apply_each_curves(selected_curves, self.remove_constraints)

        return{'FINISHED'}

    # remove constraints every curve
    @classmethod
    def remove_constraints(cls, curve):
        for constraint in curve.constraints:
            if(constraint.name[:4] == "ATH_"):
                curve.constraints.remove(constraint)

    # use dialog
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# Delete the constraints added for management
class ANIME_HAIR_TOOLS_OT_select_shapekey(bpy.types.Operator):
    bl_idname = "anime_hair_tools.add_shapekey"
    bl_label = "Select Shape Key (ATH)"

    # execute ok
    def execute(self, context):
        selected_curves = get_selected_curve_objects()

        # remove constraints
        apply_each_curves(selected_curves, self.add_or_select_shapekeys)

        return{'FINISHED'}

    # select or add shapekey every curve
    def add_or_select_shapekeys(self, curve):
        select_name = "ATH"
        select_value = 0.5

        shape_keys = curve.data.shape_keys

        # check Basis
        if(shape_keys == None):
            curve.shape_key_add(name="Basis");

        # check keyname
        if(select_name not in shape_keys.key_blocks.keys()):
            curve.shape_key_add(name=select_name);

        # select shapekey
        shapekey_index = shape_keys.key_blocks.find(select_name)
        curve.active_shape_key_index = shapekey_index
        
        # change value
        curve.active_shape_key.value = select_value

    # use dialog
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# retister blender
# *******************************************************************************************
classes = (
    ANIME_HAIR_TOOLS_PT_ui,
    ANIME_HAIR_TOOLS_OT_bevel_taper,
    ANIME_HAIR_TOOLS_OT_material,
    ANIME_HAIR_TOOLS_OT_create_bone_and_constraint,
    ANIME_HAIR_TOOLS_OT_remove_constraint,
    ANIME_HAIR_TOOLS_OT_select_shapekey,
)

for cls in classes:
    bpy.utils.register_class(cls)
