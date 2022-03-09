import bpy, math

from . import Naming, MirrorUtil


# Curveをメッシュにコンバート
# =================================================================================================
def create(context, selected_curve_objs):
    armature = bpy.data.objects[context.scene.AHT_armature_name]

    # Curveごとに分離する
    for curve_obj in selected_curve_objs:
        # 処理するCurveをActiveに
        bpy.context.view_layer.objects.active = curve_obj

        # コンバート前にミラーを解除する
        recovery_data = MirrorUtil.disable_mirror_modifires(curve_obj)

        # 房ごとにMesh化
        duplicated_list = _create_temp_mesh(curve_obj)

        # CurveのMirrorモディファイアを元に戻しておく
        MirrorUtil.recovery_mirror_modifires(recovery_data)

        # 頂点ウェイト設定
        _set_mesh_weights(curve_obj, duplicated_list)

        # JOIN & 名前設定
        mesh_obj = _join_temp_meshes(duplicated_list)
        mesh_obj.name = Naming.make_mesh_name(curve_obj.name)

        # ミラーのコピー
        for modifier in recovery_data:
            mesh_obj.modifiers.new(modifier.name, modifier.type)

        # メッシュにモディファイアを追加
        mesh_obj.modifiers.new("Armature", "ARMATURE")
        armature = mesh_obj.modifiers[-1]
        armature.object = bpy.data.objects.get(context.scene.AHT_armature_name)

        if context.scene.AHT_subdivision:
            mesh_obj.modifiers.new("Subdivision", 'SUBSURF')

        # Meshの親をArmatureに設定
        mesh_obj.parent = bpy.data.objects.get(context.scene.AHT_armature_name)
        mesh_obj.matrix_parent_inverse = mesh_obj.parent.matrix_world.inverted()

# テンポラリMeshを作成
def _create_temp_mesh(curve_obj):
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

    # メッシュ化
    bpy.ops.object.select_all(action='DESELECT')
    for duplicated_obj in duplicated_list:
        duplicated_obj.select_set(True)
    bpy.ops.object.convert(target='MESH', keep_original=False)

    return duplicated_list

def _set_mesh_weights(curve_obj, duplicated_list):
    # 頂点にウェイト設定する内部関数を用意しておく
    def __add_weight_group(target_obj, name_base, spline_no, segment_no, mirror_name):
        vw_name = Naming.make_bone_name(name_base, spline_no, segment_no, mirror_name)
        vg = target_obj.vertex_groups[vw_name]
        vg.add([v_no], 1, 'ADD')

    # 関数本体
    # -------------------------------------------------------------------------
    # ミラーチェック
    MirrorName = None if len(MirrorUtil.find_mirror_modifires(curve_obj)) == 0 else "L"

    # まずはVertexGropusの追加
    # -------------------------------------------------------------------------
    for duplicate_no,duplicated_obj in enumerate(duplicated_list):
        splines = curve_obj.data.splines.values()
        for point_no in range(len(splines[duplicate_no].points)-1):
            duplicated_obj.vertex_groups.new(name=Naming.make_bone_name(curve_obj.name, duplicate_no, point_no, MirrorName))
        # .Rも追加
        if MirrorName != None:
            for point_no in range(len(splines[duplicate_no].points)-1):
                duplicated_obj.vertex_groups.new(name=Naming.make_bone_name(curve_obj.name, duplicate_no, point_no, "R"))

    # 頂点ごとにウェイト値を算出
    # -------------------------------------------------------------------------
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
    for duplicate_no,duplicated_obj in enumerate(duplicated_list):
        mesh = duplicated_obj.data
        root_matrix = duplicated_obj.matrix_world

        curve_world_points = curve_world_points_list[duplicate_no]

        # Meshの頂点ごとにウェイトを計算
        for v_no,v in enumerate(mesh.vertices):
            world_vpos = (root_matrix @ v.co)
            # Curveの線分ごとに処理
            vg_add_flag = False
            for i in range(len(curve_world_points)-1):
                # Curveの線分のベクトル
                curve_vec = curve_world_points[i+1] - curve_world_points[i]
                curve_vec_length = curve_vec.length  # ベクトルの長さを出しておく
                curve_vec.normalize()  # 単位化
    
                # Curveの始点から頂点へのベクトル
                to_point_vec = world_vpos - curve_world_points[i]

                # 射影
                on_curve_length = curve_vec.dot(to_point_vec)

                # 線分上にいればその線分から作られるBoneをウェイト1.0に
                if on_curve_length >= 0 and on_curve_length < curve_vec_length:
                    # この頂点が始点のBoneに追従するようにウェイト設定
                    __add_weight_group(duplicated_obj, curve_obj.name, duplicate_no, i, MirrorName)
                    vg_add_flag = True
                    break

            # 頂点グループを設定しそこなった
            if vg_add_flag == False:
                # 一番近いBoneの始点をを算出
                min_distance = math.inf
                min_index = None
                for i in range(len(curve_world_points)-1):
                    distance = (world_vpos - curve_world_points[i]).length
                    if min_distance > distance:
                        min_index = i
                        min_distance = distance

                # 一番近いBoneの始点を対象にする
                if min_index != None:
                    # この頂点が始点のBoneに追従するようにウェイト設定
                    __add_weight_group(duplicated_obj, curve_obj.name, duplicate_no, min_index, MirrorName)
                    vg_add_flag = True

            # 基本的にここには来ない
            if vg_add_flag == False:
                print("error: weight cannot set:", v_no)


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
                obj.select_set(True)

    # 削除        
    bpy.ops.object.delete()
