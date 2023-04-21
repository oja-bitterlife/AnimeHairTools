import bpy


# IK Setup
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_curve_straighten(bpy.types.Operator):
    bl_idname = "anime_hair_tools.curve_straighten"
    bl_label = "Straighten"

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
                    execute_nurbs_straighten(spline, context.scene.AHT_straighten_keep_length)
                elif spline.type == "BEZIER":
                    return "unsupported type: %s" % spline.type
                else:
                    return "unknown type: %s" % spline.type
        return ""

def execute_nurbs_straighten(spline, keep_length, is_force=False):
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
            if point.select or is_force:
                # 方向取得
                if i == 0:
                    # 最初が選択されてるときは次のポイントとの直線
                    vec = (spline.points[i+1].co.xyz - point.co.xyz).normalized()
                elif i == len(length_list)-1:
                    break  # 最後が選択されてるときは何もしない
                else:
                    # 前のポイントとの直線
                    vec = (point.co.xyz - spline.points[i-1].co.xyz).normalized()

                # keep length じゃなければconstant化
                if not keep_length:
                    total_length = sum(length_list[i+1:])
                    constant_length = total_length / (len(length_list)-(i+1))
                    for j in range(i+1, len(length_list)):
                        length_list[j] = constant_length

        else:
            # 選択点以降はまっすぐに配置しなおす
            spline.points[i].co.xyz = spline.points[i-1].co.xyz + (vec * length_list[i])


# UI描画設定
# =================================================================================================
label = "Curve Arrange"

classes = [
    ANIME_HAIR_TOOLS_OT_curve_straighten,
]

def draw(parent, context, layout):
    if context.mode != "EDIT_CURVE":
        layout.enabled = False

    box = layout.box()
    box.prop(context.scene, "AHT_straighten_keep_length", text="Keep Length")
    box.operator("anime_hair_tools.curve_straighten")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.AHT_straighten_keep_length = bpy.props.BoolProperty(name = "Kepp Length", default=True)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
