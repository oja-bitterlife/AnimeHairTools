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
