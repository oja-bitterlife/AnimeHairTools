import bpy

from . import Naming


# Curveをメッシュにコンバート
# =================================================================================================
def create(context, selected_curve_objs):
    armature = bpy.data.objects[context.scene.AHT_armature_name]

    # Curveごとに分離する
    for curve_obj in selected_curve_objs:
        # 処理するCurveをActiveにしてEDITモードに
        bpy.context.view_layer.objects.active = curve_obj

        # splineの数だけ複製
        duplicated_list = []
        for spline in curve_obj.data.splines:
            bpy.ops.object.duplicate()
            duplicated_list.append(bpy.context.view_layer.objects.active)

        # 不要なスプラインを削除
        for duplicate_no,duplicated_obj in enumerate(duplicated_list):
            for spline_no,spline in enumerate(duplicated_obj.data.splines):
                if duplicate_no != spline_no:
                    duplicated_obj.data.splines.remove(spline)

            # 名前も設定しておく
            duplicated_obj.name = Naming.make_tmp_mesh_name(curve_obj.name, duplicate_no)

        # メッシュ化
        bpy.ops.object.select_all(action='DESELECT')
        for duplicated_obj in duplicated_list:
            duplicated_obj.select_set(True)
        bpy.ops.object.convert(target='MESH', keep_original=False)


# Meshの削除
# =================================================================================================
def remove(context, selected_curve_objs):
    bpy.ops.object.select_all(action='DESELECT')

    # 選択中のCurveを元にメッシュを特定
    for curve_obj in selected_curve_objs:
        bpy.data.objects[Naming.make_mesh_basename(curve_obj.name)].select_set(True)

    # 削除        
    bpy.ops.object.delete()
