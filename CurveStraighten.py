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
        # Curveを移動させると移動前のポイントとの長さが変わるので、先に長さだけ抜き出しておく
        length_list = []
        for i, point in enumerate(spline.points):
            if i == 0:
                length_list.append(0)
            else:
                length_list.append((spline.points[i].co.xyz - spline.points[i-1].co.xyz).length)

        nvec = None
        for i, point in enumerate(spline.points):
            # まだ方向が未定(選択点を見つけていない)
            if nvec == None:
                if point.select:
                    # 方向取得
                    if i == 0:
                        nvec = (spline.points[i+1].co.xyz - point.co.xyz).normalized()
                    else:
                        nvec = (point.co.xyz - spline.points[i-1].co.xyz).normalized()
            else:
                # 選択点以降はまっすぐに配置しなおす
                spline.points[i].co.xyz = spline.points[i-1].co.xyz + (nvec * length_list[i])


# UI描画設定
# =================================================================================================
def ui_draw(context, layout):
    layout.operator("anime_hair_tools.curve_straighten")
