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

        # コンバート前にミラーを解除する
        recovery_data = _disable_mirror_modifires(curve_obj)

        # 房ごとにMesh化
        duplicated_list = _create_temp_mesh(curve_obj)

        # 頂点ウェイト設定
        _set_mesh_weights(curve_obj, duplicated_list)

        # JOIN & 名前設定
        mesh_obj = _join_temp_meshes(duplicated_list)
        mesh_obj.name = Naming.make_mesh_name(curve_obj.name)

        # ミラーの後処理
        for modifier in recovery_data:
            # Curveのモディファイアを元に戻す
            modifier.show_viewport = True
            # メッシュにモディファイアをコピー
            mesh_obj.modifiers.new(modifier.name, modifier.type)

def _disable_mirror_modifires(curve_obj):
    recovery_data = []

    # ミラーモディファイアを探して、disableにしておく
    for modifier in curve_obj.modifiers:
        if modifier.show_viewport and modifier.type == 'MIRROR':
            modifier.show_viewport = False

        # 後で戻せるよう変更したモディファイアを覚えておく
        recovery_data.append(modifier)

    return recovery_data

# テンポラリMeshを作成
def _create_temp_mesh(curve_obj):
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

    return duplicated_list

def _set_mesh_weights(curve_obj, duplicated_list):
    # まずはVertexGropusの追加から
    for duplicate_no,duplicated_obj in enumerate(duplicated_list):
        print(dir(curve_obj.data.splines))
#        for point_no,points in enumerate(curve_obj.data.splines.get(duplicate_no).points):
#            duplicated_obj.vertex_groups.new(name=Naming.make_bone_name(curve_obj.name, duplicate_no, point_no))

        # _set_mesh_weights(curve_obj, duplicated_list)

def _join_temp_meshes(duplicated_list):
    bpy.ops.object.select_all(action='DESELECT')
    for duplicated_obj in duplicated_list:
        duplicated_obj.select_set(True)
    bpy.ops.object.join()

    return bpy.context.view_layer.objects.active


# Meshの削除
# =================================================================================================
def remove(context, selected_curve_objs):
    bpy.ops.object.select_all(action='DESELECT')

    # 選択中のCurveを元にメッシュを特定
    for curve_obj in selected_curve_objs:
        mesh = bpy.data.objects.get(Naming.make_mesh_name(curve_obj.name))
        if mesh != None:
            mesh.select_set(True)

    # 削除        
    bpy.ops.object.delete()
