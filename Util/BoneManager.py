
import bpy

from . import Naming, ArmatureMode, MirrorUtil, ConstraintUtil


# ボーン作成
# =================================================================================================
def create(context, tmp_curve_objs, original_curve_objs):
    armature = bpy.data.objects[context.scene.AHT_armature_name]
    bpy.context.view_layer.objects.active = armature

    # Layerのバックアップとwork用LayerのみON
    backup_layers = list(armature.data.layers)
    setup_layers = [i == context.scene.AHT_create_layer-1 for i in range(len(backup_layers))]
    armature.data.layers = setup_layers

    # to edit-mode
    state_backup = ArmatureMode.to_edit_mode(context, armature)

    # Curveごとに回す
    edit_bones = []
    for i, curve_obj in enumerate(tmp_curve_objs):
        original_name = original_curve_objs[i].name

        # ミラーチェック
        MirrorName = None if len(MirrorUtil.find_mirror_modifires(curve_obj)) == 0 else "L"

        edit_bones += _create_curve_bones(context, armature, original_name, curve_obj, MirrorName)  # Curve１本１本処理する
        if MirrorName != None:
            edit_bones += _create_curve_bones(context, armature, original_name, curve_obj, "R")  # Curve１本１本処理する

    # OBJECTモードに戻すのを忘れないように
    ArmatureMode.return_obuject_mode(state_backup)
    # Boneを作ったLayerも有効にして戻す
    backup_layers[context.scene.AHT_create_layer-1] = True
    armature.data.layers = backup_layers


# create bone chain
# *****************************************************************************
def _create_curve_bones(context, armature, original_name, curve_obj, MirrorName):
    created = []

    root_matrix = armature.matrix_world.inverted() @ curve_obj.matrix_world

    # spline単位で処理
    for spline_no, spline in enumerate(curve_obj.data.splines):
        # 頂点ごとにボーンを作成する
        parent = armature.data.edit_bones[context.scene.AHT_root_bone_name]  # 最初はRootBoneが親
        for i in range(len(spline.points)-1):
            # Bone生成
            bone_name = Naming.make_bone_name(original_name, spline_no, i, MirrorName)
            bpy.ops.armature.bone_primitive_add(name=bone_name)
            new_bone = armature.data.edit_bones[bone_name]

            # Bone設定
            new_bone.parent = parent  # 親子設定

            new_bone.use_connect = i != 0  # チェインの開始位置をrootとは接続しない

            # ボーンをCurveに合わせて配置
            bgn = root_matrix @ spline.points[i].co
            end = root_matrix @ spline.points[i+1].co

            # .R側だった場合はBoneをX軸反転
            if MirrorName == "R":
                bgn.x = -bgn.x
                end.x = -end.x

            if i == 0:
                new_bone.head = bgn.xyz  # disconnected head setup
            new_bone.tail = end.xyz

            # BendyBone化
            if context.scene.AHT_bbone > 1:
                new_bone.bbone_segments = context.scene.AHT_bbone

            # 自分を親にして次をつなげていく
            parent = new_bone

            # 作ったボーンを覚えておく
            created.append(new_bone)

    return created


# 削除
# =================================================================================================
def remove(context, selected_curve_objs):
    armature = bpy.data.objects[context.scene.AHT_armature_name]
    bpy.context.view_layer.objects.active = armature

    # to edit-mode
    state_backup = ArmatureMode.to_edit_mode(context, armature)

    # 一旦全部選択解除
    bpy.ops.armature.select_all(action='DESELECT')

    # 消すべきBoneを選択
    for curve_obj in selected_curve_objs:
        bone_basename = Naming.make_bone_basename(curve_obj.name)
        for bone in armature.data.edit_bones:
            bone.select = bone.name.startswith(bone_basename)

        # 一括削除
        bpy.ops.armature.delete()

    # OBJECTモードに戻すのを忘れないように
    ArmatureMode.return_obuject_mode(state_backup)


# pose_boneの子を再帰的に選択する
# =================================================================================================
def pose_bone_gather_children(pose_bone, select_func=None):
    pose_bone_list = []
    for child_pose_bone in pose_bone.children:
        # 選択関数があれば選択するかチェック
        if select_func != None:
            if not select_func(child_pose_bone):
                continue  # 非選択になったら処理しない
        # 登録
        pose_bone_list.append(child_pose_bone)

        # 再帰で潜って追加していく
        pose_bone_list.extend(pose_bone_gather_children(child_pose_bone))

    return pose_bone_list

