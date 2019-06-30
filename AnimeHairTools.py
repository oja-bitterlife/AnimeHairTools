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
    bl_label = "Anime Hair Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
  
    def draw(self, context):
        self.layout.operator("anime_hair_tools.bevel_taper")
        self.layout.operator("anime_hair_tools.material")
        self.layout.operator("anime_hair_tools.auto_hook")
        self.layout.operator("anime_hair_tools.remove_hook")


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
        # enum selected
        available_curves = get_available_curve_objects()

        # set bevel & taper to selected curves
        selected_curves = get_selected_curve_objects()
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
        # save active object
        backup_active_object = bpy.context.active_object

        # set material to selected curves
        selected_curves = get_selected_curve_objects()
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
def setup_root_bone():
    # already created
    if ANIME_HAIR_TOOLS_BONE_ROOT_NAME in bpy.data.objects.keys():
        return bpy.data.objects[ANIME_HAIR_TOOLS_BONE_ROOT_NAME]

    # new bone
    bpy.ops.object.armature_add(enter_editmode=False, location=(0, 0, 0))
    bpy.context.active_object.name = ANIME_HAIR_TOOLS_BONE_OBJ_NAME
    bpy.context.active_object.data.name = ANIME_HAIR_TOOLS_BONE_OBJ_NAME
    bpy.context.active_object.data.bones[0].name = ANIME_HAIR_TOOLS_BONE_ROOT_NAME
    return bpy.context.active_object.name

# bpy.ops.armature.bone_primitive_add()


class ANIME_HAIR_TOOLS_OT_auto_hook(bpy.types.Operator):
    bl_idname = "anime_hair_tools.auto_hook"
    bl_label = "Create Auto Hook"

    # execute ok
    def execute(self, context):
        # save active object
        backup_active_object = bpy.context.active_object

        # bone
        bone_root = setup_root_bone()

        # set material to selected curves
        selected_curves = get_selected_curve_objects()
        for curve_name in selected_curves:
            curve = selected_curves[curve_name]  # process curve

            # get segment locations in curve
            hook_locations = self.get_hook_locations(curve)
    
            parent = bone_root
            for i in range(len(hook_locations)-1):
                bgn = hool_locations[i]
                end = hool_locations[i+1]
                parent = self.create_child_bone(curve.name, i, parent, bgn, end)


        # restore active object
        bpy.context.view_layer.objects.active = backup_active_object

        return{'FINISHED'}

    # use dialog
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


    # return locations in curve
    def get_hook_locations(self, curve):
        # stock hook locations
        hook_locations = []

        # process splines
        for spline in curve.data.splines:
            # process spline points
            for point in spline.points:
                hook_locations.append(curve.matrix_world @ point.co)

            # process bezier points
            for point in spline.bezier_points:
                hook_locations.append(curve.matrix_world @ point.co)
    
        return hook_locations

    def create_child_bone(self, base_name, i, parent, bgn, end):
        bpy.context.view_layer.objects.active = parent
        print(parent)


# remove hook object
# *******************************************************************************************
class ANIME_HAIR_TOOLS_OT_remove_hook(bpy.types.Operator):
    bl_idname = "anime_hair_tools.remove_hook"
    bl_label = "Remove Auto Hook"

    # execute ok
    def execute(self, context):
        delete_target = []

        # set material to selected curves
        selected_curves = get_selected_curve_objects()
        for curve_name in selected_curves:
            curve = selected_curves[curve_name]  # process curve

            remove_name = curve.name + ".auto_hook."

            # remove child hooks
            for child in curve.children:
                if child.type == "EMPTY" and child.name.find(remove_name) == 0:  # match to top
                    delete_target.append(child)  # append target

        # delete target hook objects
        bpy.ops.object.select_all(action='DESELECT')  # all deselect for delete
        for target in delete_target:
            target.select_set(True)
        bpy.ops.object.delete()  # delete selected objects
                    
        return{'FINISHED'}

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
    ANIME_HAIR_TOOLS_OT_remove_hook,
)

for cls in classes:
    bpy.utils.register_class(cls)
