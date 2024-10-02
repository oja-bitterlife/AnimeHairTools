import bpy


# IK Setup
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_curve_straighten(bpy.types.Operator):
    bl_idname = "anime_hair_tools.curve_straighten"
    bl_label = "Curve Straighten"

    # execute ok
    def execute(self, context):
        selected_curve_objs = [obj for obj in context.selected_objects if obj.type == "CURVE"]
        err = self.do_straighten(context, selected_curve_objs)

        if err != "":
            self.report({'ERROR'}, err)
            return {'CANCELLED'}

        return {'FINISHED'}

    def do_straighten(self, context, selected_curve_objs):
        for curve in selected_curve_objs:
            for spline in curve.data.splines:
                if spline.type == "NURBS":
                    execute_nurbs_straighten(spline)
                elif spline.type == "BEZIER":
                    return "unsupported type: %s" % spline.type
                else:
                    return "unknown type: %s" % spline.type
        return ""

def execute_nurbs_straighten(spline, force_all=False):
    # Curveを移動させると移動前のポイントとの長さが変わるので、先に長さだけ抜き出しておく
    length_list = []
    for i, point in enumerate(spline.points):
        if i == 0:
            length_list.append(0)
        else:
            length_list.append((spline.points[i].co.xyz - spline.points[i-1].co.xyz).length)

    vec = None
    for i, point in enumerate(spline.points):
        # まだ方向が未定(選択点を見つけていない)
        if vec == None:
            if point.select or force_all:
                # 方向取得
                if i == 0:
                    # 最初が選択されてるときは次のポイントとの直線
                    vec = (spline.points[i+1].co.xyz - point.co.xyz).normalized()
                elif i == len(length_list)-1:
                    break  # 最後が選択されてるときは何もしない
                else:
                    # 前のポイントとの直線
                    vec = (point.co.xyz - spline.points[i-1].co.xyz).normalized()

        else:
            # 選択点以降はまっすぐに配置しなおす
            spline.points[i].co.xyz = spline.points[i-1].co.xyz + (vec * length_list[i])


# UI描画設定
# =================================================================================================
classes = [
    ANIME_HAIR_TOOLS_OT_curve_straighten,
]

def draw(parent, context, layout):
    if context.mode != "EDIT_CURVE":
        layout.enabled = False

    layout.operator("anime_hair_tools.curve_straighten")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
