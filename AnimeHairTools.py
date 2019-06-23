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
NOTHING_NAME = "(nothing)"  # noting selected item

# 3DView Tools Panel
class MY_PT_ui(bpy.types.Panel):
    bl_label = "Anime Hair Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
  
    def draw(self, context):
        self.layout.operator("anime_hair_tools.root_button")


# Bebel & Taper Setting
# *******************************************************************************************
class MY_OT_button(bpy.types.Operator):
    bl_idname = "anime_hair_tools.root_button"
    bl_label = "Bevel & Taper Setting"

    # create curve enum list
    curve_enum = [(NOTHING_NAME, NOTHING_NAME, "")]
    available_curves = get_available_curve_objects()
    for curve_name in available_curves:
        curve = available_curves[curve_name]
        curve_enum.append((curve.name, curve.name, ""))

    selected_bevel: bpy.props.EnumProperty(name="Bevel Curve", items=curve_enum)
    selected_taper: bpy.props.EnumProperty(name="Taper Curve", items=curve_enum)

    # execute ok
    def execute(self, context):
        # set bevel & taper to selected curves
        selected_curves = get_selected_curve_objects()
        for curve_name in selected_curves:
            curve = selected_curves[curve_name]

            # set selected bevel
            bevel_object_name = self.selected_bevel
            if curve.name != bevel_object_name:  # not set myself
                if self.selected_bevel == NOTHING_NAME:
                    curve.data.bevel_object = None
                else:
                    curve.data.bevel_object = self.available_curves[bevel_object_name]

            # set selected taper
            taper_object_name = self.selected_taper
            if curve.name != taper_object_name:  # no set myself
                if self.selected_taper == NOTHING_NAME:
                    curve.data.taper_object = None
                else:
                    curve.data.taper_object = self.available_curves[taper_object_name]


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
