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
                    self.report({'ERROR'}, "unsupported type: %s" % spline.type)
                else:
                    self.report({'ERROR'}, "unknown type: %s" % spline.type)
                    return {'CANCELLED'}

        return {'FINISHED'}

    def execute_nurbs(self, spline):
        beforPos = None
        vec = None
        for i, point in enumerate(spline.points):
            # まだ選択点を見つけていない
            if beforPos == None:
                if point.select:
                    if i == 0: 
                        beforPos = -spline.points[i+1].co.xyz  # 次のポイントの反対方向
                    else:
                        beforPos = spline.points[i-1].co.xyz
                    # 方向取得
                    nvec = (point.co.xyz - beforPos).normalized()

            else:
                # 選択点以降はまっすぐに配置しなおす
                length = (spline.points[i].co.xyz - spline.points[i-1].co.xyz).length
                spline.points[i].co.xyz = spline.points[i-1].co.xyz + nvec * length


# UI描画設定
# =================================================================================================
def ui_draw(context, layout):
    layout.operator("anime_hair_tools.curve_straighten")
