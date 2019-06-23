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
class MY_PT_ui(bpy.types.Panel):
    bl_label = "Anime Hair Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
  
    def draw(self, context):
        self.layout.operator("anime_hair_tools.root_button")


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


class MY_OT_button(bpy.types.Operator):
    bl_idname = "anime_hair_tools.root_button"
    bl_label = "Bevel & Taper Setting"

    # create curve enum list
    selected_bevel: bpy.props.EnumProperty(name="Bevel Curve", items=create_curve_enum_items)
    selected_taper: bpy.props.EnumProperty(name="Taper Curve", items=create_curve_enum_items)

    # execute ok
    def execute(self, context):
        # find all curves
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


# retister blender
# *******************************************************************************************
classes = (
    MY_PT_ui,
    MY_OT_button
)

for cls in classes:
    bpy.utils.register_class(cls)
