import bpy


# IK Setup
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_curve_straighten(bpy.types.Operator):
    bl_idname = "anime_hair_tools.curve_straighten"
    bl_label = "CurveStraighten"

    # execute ok
    def execute(self, context):
        selected_curve_objs = [obj for obj in context.selected_objects if obj.type == "CURVE"]

        for curve in selected_curve_objs:
            for spline in curve.data.splines:
                if spline.type == "NURBS":
                    self.execute_nurbs(spline)
                elif spline.type == "BEZIER":
                    self.execute_bezier(spline)
                else:
                    self.report({'ERROR'}, "unknown type: %s" % spline.type)
                    return {'CANCELLED'}

        return {'FINISHED'}

    def execute_nurbs(self, spline):
        selected = False
        for point in spline.points:
            if point.select:
                selected = True
            if selected:
                print(point)

    def execute_bezier(self, spline):
        selected = False
        for point in spline.bezier_points:
            if point.select_control_point:
                selected = True
            if selected:
                print(point)


# UI描画設定
# =================================================================================================
def ui_draw(context, layout):
    layout.operator("anime_hair_tools.curve_straighten")
