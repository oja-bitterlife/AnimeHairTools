import bpy, math

from . import Naming, MirrorUtil
from . import ArmatureMode
from .. import CurveStraighten


# Curveをメッシュにコンバート
# =================================================================================================
def create(context, selected_curve_objs):
    # armature = bpy.data.objects[context.scene.AHT_armature_name]

    # Curveごとに分離する
    for i, curve_obj in enumerate(selected_curve_objs):
        # 処理するCurveをActiveに
        bpy.context.view_layer.objects.active = curve_obj

        # コンバート前にミラーを解除する
        recovery_data = MirrorUtil.disable_mirror_modifires(curve_obj)

        # 房ごとにMesh化
        created_list = _create_temp_mesh(context, curve_obj)

        # CurveのMirrorモディファイアを元に戻しておく
        MirrorUtil.recovery_mirror_modifires(recovery_data)

        # 頂点ウェイト設定
        _set_mesh_weights(curve_obj, created_list)

        # # JOIN & 名前設定
        # mesh_obj = _join_temp_meshes(duplicated_list)
        # mesh_obj.name = Naming.make_mesh_name(original_name)

        # # ミラーのコピー
        # for modifier in recovery_data:
        #     new_mirror_modifire = mesh_obj.modifiers.new(modifier.name, modifier.type)
        #     new_mirror_modifire.use_mirror_merge = False


        # # メッシュにモディファイアを追加
        # mesh_obj.modifiers.new("Armature", "ARMATURE")
        # armature = mesh_obj.modifiers[-1]
        # armature.object = bpy.data.objects.get(context.scene.AHT_armature_name)

        # if context.scene.AHT_subdivision:
        #     mesh_obj.modifiers.new("Subdivision", 'SUBSURF')

        # # Meshの親をArmatureに設定
        # mesh_obj.parent = bpy.data.objects.get(context.scene.AHT_armature_name)
        # mesh_obj.matrix_parent_inverse = mesh_obj.parent.matrix_world.inverted()

# テンポラリMeshを作成
def _create_temp_mesh(context, curve_obj):
    armature = bpy.data.objects[context.scene.AHT_armature_name]

    # 複製の対象を対象のCurveだけにする
    bpy.ops.object.select_all(action='DESELECT')
    curve_obj.select_set(True)

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

def _set_mesh_weights(curve_obj, created_list):
    # 分離して扱いやすく
    duplicated_list, straighted_list = created_list

    # 頂点にウェイト設定する内部関数を用意しておく
    def __add_weight_group(target_obj, v_no, name_base, spline_no, segment_no, mirror_name):
        vw_name = Naming.make_bone_name(name_base, spline_no, segment_no, mirror_name)
        vg = target_obj.vertex_groups[vw_name]
        vg.add([v_no], 1, 'ADD')


    # 関数本体
    # -------------------------------------------------------------------------
    # ミラーチェック
    MirrorName = None if len(MirrorUtil.find_mirror_modifires(curve_obj)) == 0 else "L"

    # まずはVertexGropusの追加
    # -------------------------------------------------------------------------
    for duplicate_no in range(len(duplicated_list)):
        splines = curve_obj.data.splines.values()
        for point_no in range(len(splines[duplicate_no].points)-1):
            duplicated_list[duplicate_no].vertex_groups.new(name=Naming.make_bone_name(curve_obj.name, duplicate_no, point_no, MirrorName))
            straighted_list[duplicate_no].vertex_groups.new(name=Naming.make_bone_name(curve_obj.name, duplicate_no, point_no, MirrorName))
        # .Rも追加
        if MirrorName != None:
            for point_no in range(len(splines[duplicate_no].points)-1):
                duplicated_list[duplicate_no].vertex_groups.new(name=Naming.make_bone_name(curve_obj.name, duplicate_no, point_no, "R"))
                straighted_list[duplicate_no].vertex_groups.new(name=Naming.make_bone_name(curve_obj.name, duplicate_no, point_no, "R"))

    # 頂点ごとにウェイト値を算出
    # -------------------------------------------------------------------------
    # ベクトル取得
    root_matrix = curve_obj.matrix_world
    spline = curve_obj.data.splines[0]  # 1Curve=1Splineになっているはず
    world_vec = (root_matrix @ spline.points[1].co - root_matrix @ spline.points[0].co).xyz.normalized()

    # カーブの各セグメントまでの距離を入れる
    curve_length = []
    segments = curve_obj.data.splines[0].points  # 1Curve=1Splineになっているはず
    total_length = 0
    for point_no in range(len(segments)-1):
        total_length += (segments[point_no+1].co - segments[point_no].co).length
        curve_length.append(total_length)
    print(curve_length)

    return







    # まずは対象となるCurveポイントのWorld座標を取得
    curve_world_points_list = []
    for spline in curve_obj.data.splines:
        curve_world_points = []
        for spline_point in spline.points:
            root_matrix = curve_obj.matrix_world
            world_pos = root_matrix @ spline_point.co
            curve_world_points.append(world_pos.xyz)
        # スプラインごとにまとめていく
        curve_world_points_list.append(curve_world_points)

    # 房(メッシュ)ごとに処理。
    # Curveのポイント間をつなぐ線分上に射影して、一番近い(ただし0以上)
    # Curveの始点をウェイト対象にする
    for duplicate_no,duplicated_obj in enumerate(straighted_list):
        mesh = duplicated_obj.data
        root_matrix = duplicated_obj.matrix_world

        curve_world_points = curve_world_points_list[duplicate_no]

        # Meshの頂点ごとにウェイトを計算
        for v_no,v in enumerate(mesh.vertices):
            world_vpos = (root_matrix @ v.co)

            # Curveの線分ごとに処理
            distance_list = []
            for i in range(len(curve_world_points)-1):
                # 頂点間の距離
                distance_list.append([i , (world_vpos - curve_world_points[i]).length])

            # ソートして近い順に
            distance_list = sorted(distance_list, key=lambda x: x[1])

            # ボーン方向にないものを排除
            def check_dir(distance, world_vpos, curve_world_points):
                point_no = distance[0]
                point_vec = world_vpos - curve_world_points[point_no]
                curve_vec = curve_world_points[point_no+1] - curve_world_points[point_no]
                return curve_vec.dot(point_vec) >= 0

            check_dir_list = [distance for distance in distance_list if check_dir(distance, world_vpos, curve_world_points)]

            # 順方向に近いCurveのpointがなかった
            use_no = None
            if len(check_dir_list) == 0:
                use_no = distance_list[0][0]  # とりあえず一番近いCurveのpointを使う
            else:
                # 残ったので一番近いもの
                use_no = check_dir_list[0][0]

            __add_weight_group(duplicated_obj, v_no, curve_obj.name, duplicate_no, use_no, MirrorName)


# ウェイトを付け終わった中間Meshを結合して１つのオブジェクトにする
def _join_temp_meshes(duplicated_list):
    bpy.ops.object.select_all(action='DESELECT')

    # 結合用に生成したメッシュを選択
    for duplicated_obj in duplicated_list:
        duplicated_obj.select_set(True)

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
