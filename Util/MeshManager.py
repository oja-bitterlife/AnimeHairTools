import bpy, math

from . import Naming, MirrorUtil
from . import ArmatureMode
from .. import CurveStraighten


NEAR_BONE_MARKING_WEIGHT_NAME = "AHT_NEAR_BONE"

# Curveをメッシュにコンバート
# =================================================================================================
def create(context, selected_curve_objs):
    # armature = bpy.data.objects[context.scene.AHT_armature_name]

    # Curveごとに分離する
    for curve_obj in selected_curve_objs:
        # 処理するCurveをActiveに
        bpy.context.view_layer.objects.active = curve_obj

        # コンバート前にミラーを解除する
        recovery_data = MirrorUtil.disable_mirror_modifires(curve_obj)

        # 房ごとにMesh化
        (duplicated_list, straighted_list) = _create_temp_mesh(context, curve_obj)

        # CurveのMirrorモディファイアを元に戻しておく
        MirrorUtil.recovery_mirror_modifires(recovery_data)

        # 頂点ウェイト設定
        _set_mesh_weights(curve_obj, duplicated_list, straighted_list)

        # 頂点ウェイト設定が終わったらstraight側はもういらない
        bpy.ops.object.select_all(action='DESELECT')
        for straight_mesh in straighted_list:
            straight_mesh.select_set(True)
        bpy.ops.object.delete()

        # JOIN & 名前設定
        # mesh_obj = _join_temp_meshes(duplicated_list)
        # mesh_obj.name = Naming.make_mesh_name(curve_obj.name)

        # ミラーのコピー
        for meshed_curve_obj in duplicated_list:
            for modifier in recovery_data:
                new_mirror_modifire = meshed_curve_obj.modifiers.new(modifier.name, modifier.type)
                new_mirror_modifire.use_mirror_merge = False

            # メッシュにモディファイアを追加
            meshed_curve_obj.modifiers.new("Armature", "ARMATURE")
            armature = meshed_curve_obj.modifiers[-1]
            armature.object = bpy.data.objects.get(context.scene.AHT_armature_name)

            if context.scene.AHT_subdivision:
                meshed_curve_obj.modifiers.new("Subdivision", 'SUBSURF')

            # Meshの親をArmatureに設定
            meshed_curve_obj.parent = bpy.data.objects.get(context.scene.AHT_armature_name)
            meshed_curve_obj.matrix_parent_inverse = meshed_curve_obj.parent.matrix_world.inverted()

    return duplicated_list


# テンポラリMeshを作成
def _create_temp_mesh(context, curve_obj):
    armature = bpy.data.objects[context.scene.AHT_armature_name]

    # 複製の対象を対象のCurveだけにする
    bpy.ops.object.select_all(action='DESELECT')
    curve_obj.select_set(True)
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

    # さらにストレート化用に複製
    bpy.ops.object.select_all(action='DESELECT')
    for duplicated_obj in duplicated_list:
        duplicated_obj.select_set(True)
    bpy.ops.object.duplicate()
    straighted_list = [obj for obj in context.selected_objects if obj.type == "CURVE"]

    # ストレート化
    ArmatureMode.to_edit_mode(context, armature)
    for curve in straighted_list:
        for spline in curve.data.splines:
            if spline.type == "NURBS":
                CurveStraighten.execute_nurbs_straighten(spline, True, True)
    ArmatureMode.return_obuject_mode()

    # メッシュ化
    bpy.ops.object.select_all(action='DESELECT')
    for duplicated_obj in duplicated_list:
        duplicated_obj.select_set(True)
    for straighted_obj in straighted_list:
        straighted_obj.select_set(True)
        bpy.context.view_layer.objects.active = straighted_obj
    bpy.ops.object.convert(target='MESH', keep_original=False)

    return (duplicated_list, straighted_list)


# テンポラリメッシュにウェイトを設定する
def _set_mesh_weights(curve_obj, duplicated_list, straighted_list):
    # 頂点にウェイト設定する内部関数を用意しておく
    # *************************************************************************
    def __add_weight_group(ratio, target_obj, v_no, name_base, spline_no, segment_no, mirror_name):
        vw_name = Naming.make_bone_name(name_base, spline_no, segment_no, mirror_name)
        vg = target_obj.vertex_groups[vw_name]
        vg.add([v_no], ratio, 'ADD')
    # *************************************************************************

    # 関数本体
    # -------------------------------------------------------------------------
    # ミラーチェック
    MirrorName = None if len(MirrorUtil.find_mirror_modifires(curve_obj)) == 0 else "L"

    # まずはVertexGropusの追加
    # -------------------------------------------------------------------------
    for spline_no,spline in enumerate(curve_obj.data.splines):
        for point_no in range(len(spline.points)-1):
            duplicated_list[spline_no].vertex_groups.new(name=Naming.make_bone_name(curve_obj.name, spline_no, point_no, MirrorName))
            straighted_list[spline_no].vertex_groups.new(name=Naming.make_bone_name(curve_obj.name, spline_no, point_no, MirrorName))
        # .Rも追加
        if MirrorName != None:
            for point_no in range(len(spline.points)-1):
                duplicated_list[spline_no].vertex_groups.new(name=Naming.make_bone_name(curve_obj.name, spline_no, point_no, "R"))
                straighted_list[spline_no].vertex_groups.new(name=Naming.make_bone_name(curve_obj.name, spline_no, point_no, "R"))

    # ボーン地点付近マーキング用
    for spline_no,spline in enumerate(curve_obj.data.splines):
        duplicated_list[spline_no].vertex_groups.new(name=NEAR_BONE_MARKING_WEIGHT_NAME)


    # 頂点ごとにウェイト値を算出
    # -------------------------------------------------------------------------
    # ベクトル取得
    root_matrix = curve_obj.matrix_world

    # 房(メッシュ)ごとに処理。
    # Curveのポイント間をつなぐ線分上に射影して、線分の端点２点からの距離でウェイトを設定する
    for list_no,straighted_obj in enumerate(straighted_list):
        spline = curve_obj.data.splines[list_no]
        world_vec = (root_matrix @ spline.points[1].co - root_matrix @ spline.points[0].co).xyz.normalized()
        root_point = (root_matrix @ spline.points[0].co).xyz

        # カーブの各セグメントまでの距離を入れる
        curve_length = [0]
        segments = curve_obj.data.splines[0].points  # 1Curve=1Splineになっているはず
        total_length = 0
        for point_no in range(len(segments)-1):
            total_length += (segments[point_no+1].co - segments[point_no].co).length
            curve_length.append(total_length)

        # ストレート側と元形状側のメッシュの頂点番号は同じと信じている
        mesh = straighted_obj.data
        
        # Meshの頂点ごとにウェイトを計算
        for v_no,v in enumerate(mesh.vertices):
            world_vpos = (root_matrix @ v.co).xyz

            # 射影して距離算出
            vertex_len = abs((world_vpos - root_point).dot(world_vec))

            # 端点を調べる
            for term_no in range(len(curve_length)):
                if vertex_len < curve_length[term_no]:
                    break
            ratio = (vertex_len-curve_length[term_no-1]) / (curve_length[term_no]-curve_length[term_no-1])
    
            # ボーン番号マーキング
            if ratio <= 0.2:
                vg = duplicated_list[list_no].vertex_groups[NEAR_BONE_MARKING_WEIGHT_NAME]
                vg.add([v_no], (term_no)*0.1, 'ADD')
            if ratio >= 0.8:
                vg = duplicated_list[list_no].vertex_groups[NEAR_BONE_MARKING_WEIGHT_NAME]
                vg.add([v_no], (term_no+1)*0.1, 'ADD')

            # ウェイト設定
            __add_weight_group(1, duplicated_list[list_no], v_no, curve_obj.name, list_no, term_no-1, MirrorName)
            __add_weight_group(1, straighted_list[list_no], v_no, curve_obj.name, list_no, term_no-1, MirrorName)



# ウェイトを付け終わった中間Meshを結合して１つのオブジェクトにする
def _join_temp_meshes(duplicated_list):
    bpy.ops.object.select_all(action='DESELECT')

    # 結合用に生成したメッシュを選択
    for duplicated_obj in duplicated_list:
        duplicated_obj.select_set(True)

    bpy.context.view_layer.objects.active = duplicated_list[0]
    bpy.ops.object.join()

    # 結合したオブジェクトがアクティブになる
    return bpy.context.view_layer.objects.active


# Meshの削除
# =================================================================================================
def remove(context, selected_curve_objs):
    # 一旦全部選択解除
    bpy.ops.object.select_all(action='DESELECT')

    # 消すべきMeshを選択
    for curve_obj in selected_curve_objs:
        mesh_basename = Naming.make_mesh_name(curve_obj.name)
        for obj in bpy.data.objects:
            if obj.type == "MESH" and obj.name.startswith(mesh_basename):
                try:
                    obj.select_set(True)
                except:
                    pass  # 消したてだとSelectに失敗することがある(完全削除待ち？)

    # 削除        
    bpy.ops.object.delete()
