import bpy, math

from ..Util import Naming
from . import ArmatureMode, MirrorUtil
from .. import CurveStraighten


# Curveをメッシュにコンバート
# =================================================================================================
def create(context, selected_curve_objs):
    meshed_curve_list_group = []

    # Curveごとに分離する
    for curve_obj in selected_curve_objs:
        # 処理するCurveをActiveに
        bpy.context.view_layer.objects.active = curve_obj

        # コンバート前にミラーを解除する
        recovery_data = MirrorUtil.disable_mirror_modifires(curve_obj)

        # 房ごとにMesh化
        (duplicated_list, straighted_list, straight_points_list) = _create_temp_mesh(context, curve_obj)

        # CurveのMirrorモディファイアを元に戻しておく
        MirrorUtil.recovery_mirror_modifires(recovery_data)

        # 頂点ウェイト設定
        _set_mesh_weights(curve_obj, duplicated_list, straighted_list, straight_points_list)

        # 頂点ウェイト設定が終わったらstraight側はもういらない
        bpy.ops.object.select_all(action='DESELECT')
        for straight_mesh in straighted_list:
            straight_mesh.select_set(True)
        bpy.ops.object.delete()

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

        meshed_curve_list_group.append((duplicated_list, straight_points_list))

    return meshed_curve_list_group


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
            else:
                print("Splineタイプのエラー", spline.type)
    ArmatureMode.return_obuject_mode()

    # ストレート化したときのCurveポイントを保存する
    straight_points_list = []
    for curve in straighted_list:
        for spline in curve.data.splines:
            # ワールド座標でストレートカーブのポイント位置記録
            straight_points_list.append([(curve.matrix_world @ spline.points[point_no].co).xyz for point_no in range(len(spline.points))])

    # メッシュ化
    bpy.ops.object.select_all(action='DESELECT')
    for duplicated_obj in duplicated_list:
        duplicated_obj.select_set(True)
    for straighted_obj in straighted_list:
        straighted_obj.select_set(True)
        bpy.context.view_layer.objects.active = straighted_obj
    bpy.ops.object.convert(target='MESH', keep_original=False)

    return (duplicated_list, straighted_list, straight_points_list)


# テンポラリメッシュにウェイトを設定する
def _set_mesh_weights(curve_obj, duplicated_list, straighted_list, straight_points_list):
    # 頂点にウェイト設定する内部関数を用意しておく
    # *************************************************************************
    def __add_weight_group(ratio, target_obj, v_no, name_base, list_no, point_no, mirror_name):
        vw_name = Naming.make_bone_name(name_base, list_no, point_no, mirror_name)
        vg = target_obj.vertex_groups[vw_name]
        vg.add([v_no], ratio, 'ADD')
    # *************************************************************************

    # 関数本体
    # -------------------------------------------------------------------------
    # ミラーチェック
    MirrorName = None if len(MirrorUtil.find_mirror_modifires(curve_obj)) == 0 else "L"

    # まずはVertexGropusの追加
    # -------------------------------------------------------------------------
    for list_no,_ in enumerate(straight_points_list):
        for point_no in range(len(straight_points_list[list_no])-1):
            duplicated_list[list_no].vertex_groups.new(name=Naming.make_bone_name(curve_obj.name, list_no, point_no, MirrorName))
            straighted_list[list_no].vertex_groups.new(name=Naming.make_bone_name(curve_obj.name, list_no, point_no, MirrorName))
        # .Rも追加
        if MirrorName != None:
            for point_no in range(len(straight_points_list[list_no])-1):
                duplicated_list[list_no].vertex_groups.new(name=Naming.make_bone_name(curve_obj.name, list_no, point_no, "R"))
                straighted_list[list_no].vertex_groups.new(name=Naming.make_bone_name(curve_obj.name, list_no, point_no, "R"))


    # 頂点ごとにウェイト値を算出
    # -------------------------------------------------------------------------
    # ベクトル取得
    root_matrix = curve_obj.matrix_world

    # 房(メッシュ)ごとに処理。
    # Curveのポイント間をつなぐ線分上に射影して、線分の端点２点からの距離でウェイトを設定する
    for list_no,straighted_obj in enumerate(straighted_list):
        root_point = straight_points_list[list_no][0]
        world_vec = (straight_points_list[list_no][1] - root_point).normalized()

        # カーブの各セグメントまでの距離を入れる
        curve_length = [0]
        total_length = 0
        for point_no in range(len(straight_points_list[list_no])-1):
            total_length += (straight_points_list[list_no][point_no+1] - straight_points_list[list_no][point_no]).length
            curve_length.append(total_length)

        # ストレート側と元形状側のメッシュの頂点番号は同じと信じてみる
        mesh = straighted_obj.data
        
        # Meshの頂点ごとにウェイトを計算
        for v_no,v in enumerate(mesh.vertices):
            world_vpos = (root_matrix @ v.co).xyz

            # 射影して距離算出
            v_len = abs((world_vpos - root_point).dot(world_vec))

            # 端点を調べる
            for term_no,length in enumerate(curve_length):
                if v_len < length:
                    break

            # ウェイト設定
            __add_weight_group(1, duplicated_list[list_no], v_no, curve_obj.name, list_no, term_no-1, MirrorName)
            __add_weight_group(1, straighted_list[list_no], v_no, curve_obj.name, list_no, term_no-1, MirrorName)


        # ボーン生成のための情報を取得
        # -------------------------------------------------------------------------
        # 頂点がボーン生成に与える影響を格納するウェイト
        # セグメントごとに頂点全部ウェイト設定
        for point_no,point in enumerate(straight_points_list[list_no]):
            # データ格納先作成
            new_vg = duplicated_list[list_no].vertex_groups.new(name=Naming.get_bone_gen_info_name(point_no))

            p_len = abs((point - root_point).dot(world_vec))
            weights = []
            max_ratio = 0
            for v_no,v in enumerate(mesh.vertices):
                world_vpos = (root_matrix @ v.co).xyz
                v_len = abs((world_vpos - root_point).dot(world_vec))

                # 近いほど1に設定
                ratio = 1 - abs((v_len-p_len) / total_length)
                max_ratio = max(max_ratio, ratio)
                weights.append(ratio)

            # normalize
            weights = [(w/max_ratio) ** 16 for w in weights]

            # 登録
            for v_no,v in enumerate(mesh.vertices):
                new_vg.add([v_no], weights[v_no], 'ADD')



# ウェイトを付け終わった中間Meshを結合して１つのオブジェクトにする
# =================================================================================================
def join_and_settings(selected_curve_objs, meshed_curve_list_group):
    # 不要なデータを消す
    for i,(meshed_curve_list, straight_points_list) in enumerate(meshed_curve_list_group):
            for meshed_curve_obj in meshed_curve_list:
                # もう不要なVGであれば削除
                for vg in meshed_curve_obj.vertex_groups:
                    if vg.name.startswith(Naming.AHT_BONE_GEN_INFO_NAME):  # ボーン生成位置特定用ウェイト
                        meshed_curve_obj.vertex_groups.remove(vg)

    # 最終設定
    for i,curve_obj in enumerate(selected_curve_objs):
        (meshed_curve_list, straight_points_list) = meshed_curve_list_group[i]

        bpy.ops.object.select_all(action='DESELECT')

        # 結合用に生成したメッシュを選択
        for duplicated_obj in meshed_curve_list:
            duplicated_obj.select_set(True)

        # JOIN
        bpy.context.view_layer.objects.active = meshed_curve_list[0]
        bpy.ops.object.join()

        # 名前の修正
        obj = bpy.context.view_layer.objects.active
        obj.name = Naming.make_mesh_name(curve_obj.name)


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
