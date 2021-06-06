import bpy

from . import Naming, MirrorUtil


# Curveをメッシュにコンバート
# =================================================================================================
def create(context, selected_curve_objs):
    armature = bpy.data.objects[context.scene.AHT_armature_name]

    # Curveごとに分離する
    for curve_obj in selected_curve_objs:
        # 処理するCurveをActiveにしてEDITモードに
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

        # Bone用に親を設定
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
    # まずは対象となるCurveのポイントの座標を取得
    bone_ends_list = []
    for spline_no, spline in enumerate(curve_obj.data.splines):
        bone_ends = []
        for i in range(len(spline.points)-1):
            root_matrix = curve_obj.matrix_world
            world_pos = root_matrix @ spline.points[i+1].co
            bone_ends.append(world_pos.xyz)
        # スプラインごとにまとめていく
        bone_ends_list.append(bone_ends)

    # 房(メッシュ)ごとに各頂点のボーンとの距離算出
    for duplicate_no,duplicated_obj in enumerate(duplicated_list):
        mesh = duplicated_obj.data
        root_matrix = duplicated_obj.matrix_world
    
        for v_no,v in enumerate(mesh.vertices):
            # 一つの頂点にすべてのボーンへの距離を突っ込む
            vertex_weight = []
            for bone_no,bone_world in enumerate(bone_ends_list[duplicate_no]):
                d = (root_matrix @ v.co) - bone_world
                vertex_weight.append([bone_no, d.length])
            # 値が小さい３つに絞る
            vertex_weight = sorted(vertex_weight, key=lambda x: x[1])[:3]

            # 割合に変換
            sum_length = 0
            for vw_no in range(len(vertex_weight)):
                sum_length += vertex_weight[vw_no][1]
            if sum_length > 0:  # 一応0割対策
                for vw_no in range(len(vertex_weight)):
                    vertex_weight[vw_no][1] = vertex_weight[vw_no][1] / sum_length
            for vw_no in range(len(vertex_weight)):
                vertex_weight[vw_no][1] = 1 - vertex_weight[vw_no][1]  # 一番近いときが1
                # 影響にメリハリを
                vertex_weight[vw_no][1] = pow(vertex_weight[vw_no][1], 3)

            # 頂点についたウェイトを頂点グループに登録
            for vw in vertex_weight:
                vw_name = Naming.make_bone_name(curve_obj.name, duplicate_no, vw[0], MirrorName)
                vg = duplicated_obj.vertex_groups[vw_name]
                vg.add([v_no], vw[1], 'ADD')  # 割合にして逆数に

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
