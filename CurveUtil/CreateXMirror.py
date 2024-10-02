import bpy


# IK Setup
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_create_x_mirror(bpy.types.Operator):
    bl_idname = "anime_hair_tools.create_x_mirror"
    bl_label = "Create X-Mirror"

    # execute ok
    def execute(self, context):
        selected_curve_objs = [obj for obj in context.selected_objects if obj.type == "CURVE"]

        # 一つずつ処理をする
        for curve in selected_curve_objs:
            # 1つ複製
            bpy.ops.object.select_all(action='DESELECT')
            context.view_layer.objects.active = curve
            curve.select_set(True)
            bpy.ops.object.duplicate(linked=False)

            dup_curve = context.active_object
            dup_curve.name = curve.name + ".x_mirror"

            # セグメントを反転する
            for spline in dup_curve.data.splines:
                for point in spline.points:
                    point.co.x *= -1
                    point.tilt *= -1

            # 元のcurveにjoinする
            if context.scene.AHT_x_mirror_join:
                curve.select_set(True)
                dup_curve.select_set(True)
                context.view_layer.objects.active = curve
                bpy.ops.object.join()        

        return {'FINISHED'}


# UI描画設定
# =================================================================================================
classes = [
    ANIME_HAIR_TOOLS_OT_create_x_mirror,
]

def draw(parent, context, layout):
    row = layout.box().row()

    selected_curve_objs = [obj for obj in context.selected_objects if obj.type == "CURVE"]
    row.enabled = context.mode == "OBJECT" and len(selected_curve_objs) > 0

    row.operator("anime_hair_tools.create_x_mirror")
    row.prop(context.scene, "AHT_x_mirror_join", text="with Join")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
