
import bpy, math, mathutils
import re

from . import Naming, ArmatureMode, MirrorUtil
from . import MeshManager


# ボーン作成
# =================================================================================================
def create(context, selected_curve_objs, meshed_curve_list_group):
    # プラグインUiに設定されているArmatureを使う
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
    for i, curve_obj in enumerate(selected_curve_objs):
        meshed_curve_list = meshed_curve_list_group[i]

        for spline_no in range(len(curve_obj.data.splines)):
            # ミラーチェック
            MirrorName = None if len(MirrorUtil.find_mirror_modifires(meshed_curve_list[spline_no],)) == 0 else "L"

            edit_bones += _create_curve_bones(context, armature, curve_obj, spline_no, meshed_curve_list[spline_no], MirrorName)  # Curve１本１本処理する
            if MirrorName != None:
                edit_bones += _create_curve_bones(context, armature, curve_obj, spline_no, meshed_curve_list[spline_no], "R")  # Curve１本１本処理する

    # OBJECTモードに戻すのを忘れないように
    ArmatureMode.return_obuject_mode(state_backup)

    # Boneを作ったLayerも有効にして戻す
    backup_layers[context.scene.AHT_create_layer-1] = True
    armature.data.layers = backup_layers


# create bone chain
# *****************************************************************************
def _create_curve_bones(context, armature, curve_obj, spline_no, meshed_curve_obj, MirrorName):
    spline = curve_obj.data.splines[spline_no]

    # roll計算用
    spline_x_axis = None  # Z軸と進行方向からX軸を算出
    if len(spline.points) >= 2:
        v = meshed_curve_obj.matrix_world @ (spline.points[1].co - spline.points[0].co)
        spline_x_axis = mathutils.Vector((0, 0, 1)).cross(v.xyz.normalized()).normalized()

    # ボーン生成情報グループよりボーン位置を算出
    # -------------------------------------------------------------------------
    # 影響度を元に重心を求める
    center_of_gravity = []
    for point_no in range(len(spline.points)):
        gen_info_weight_name = MeshManager.get_bone_gen_info_name(point_no)

        sum_v = mathutils.Vector((0, 0, 0))
        total_w = 0
        for v in meshed_curve_obj.data.vertices:
            for vge in v.groups:
                if meshed_curve_obj.vertex_groups[vge.group].name == gen_info_weight_name:
                    world_pos = (meshed_curve_obj.matrix_world @ v.co).xyz
                    total_w += vge.weight
                    sum_v += world_pos * vge.weight

        center_of_gravity.append(sum_v / total_w)

    # セグメントごとにボーンを作成する
    # -------------------------------------------------------------------------
    created_bones = []
    for i in range(len(center_of_gravity)-1):
        bone_name = meshed_curve_obj.vertex_groups[i].name
        if MirrorName == "R" and meshed_curve_obj.vertex_groups[i].name.endswith(".L"):
            bone_name = bone_name[:-2] + ".R"  # R側

        # ボーン作成
        bpy.ops.armature.bone_primitive_add(name=bone_name)
        new_bone = armature.data.edit_bones[bone_name]

        # Bone設定
        m = re.match(r".*?@bone-(\d+)\.(\d+)", bone_name)
        if m == None or m.group(2) == "000":  # セグメントの先頭ボーンは親がルートボーン
            new_bone.parent = armature.data.edit_bones[context.scene.AHT_root_bone_name]
            new_bone.use_connect = False
        else:
            new_bone.parent = created_bones[-1]
            new_bone.use_connect = True

        # # ボーンをCenterに合わせて配置
        bgn = armature.matrix_world.inverted() @ center_of_gravity[i]
        end = armature.matrix_world.inverted() @ center_of_gravity[i+1]

        # # head/tailに反映
        if new_bone.use_connect:
            new_bone.head = new_bone.parent.tail
        else:
            new_bone.head = bgn.xyz
        new_bone.tail= end.xyz

        # rollも設定(head/tailのaxisを使うので代入後に)
        if spline_x_axis != None:
            if i == 0:  # 始点のrollですべてを設定
                x_axis = armature.matrix_world @ new_bone.x_axis
                y_axis = armature.matrix_world @ new_bone.y_axis
                roll = math.acos(spline_x_axis.dot(x_axis))
                # 三重積で回転方向をチェック
                if spline_x_axis.cross(x_axis).dot(y_axis) > 0:
                    roll = -roll  # 逆回転
            new_bone.roll += roll

        # .R側だった場合はBoneをX軸反転
        if MirrorName == "R":
            bgn.x = -bgn.x
            end.x = -end.x

            # head/tailを設定しなおし(Roll設定に影響しないよう代入しなおしで実施)
            if i == 0:
                new_bone.head = bgn.xyz  # disconnected head setup
            new_bone.tail = end.xyz

            # Mirror側はrollが逆転
            new_bone.roll = -new_bone.roll

        # BendyBone化
        if context.scene.AHT_bbone > 1:
            new_bone.bbone_segments = context.scene.AHT_bbone

        # 作ったボーンを覚えておく
        created_bones.append(new_bone)

    return created_bones


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


# pose_boneをCurveに沿って回転させる
# =================================================================================================
def pose_bone_fit_curve(armature, selected_curve_objs):
    for curve_obj in selected_curve_objs:
        for spline_no in range(len(curve_obj.data.splines)):

            # ミラーチェック
            if len(MirrorUtil.find_mirror_modifires(curve_obj)) == 0:
                _rec_pose_bone_fit_process(armature, curve_obj, spline_no, 0, mathutils.Quaternion(), mathutils.Quaternion(), None)
            else:
                _rec_pose_bone_fit_process(armature, curve_obj, spline_no, 0, mathutils.Quaternion(), mathutils.Quaternion(), "L")
                _rec_pose_bone_fit_process(armature, curve_obj, spline_no, 0, mathutils.Quaternion(), mathutils.Quaternion(), "R")


# spline１本について、セグメント間の方向にBoneを合わせていく
def _rec_pose_bone_fit_process(armature, curve_obj, spline_no, point_no, parent_world_qt, parent_pose_qt, LR):
    # 対象となるspline決定
    spline = curve_obj.data.splines[spline_no]
    if len(spline.points) <= point_no+1:
        return  # 再帰終了

    # 対象となるBone決定
    bone_name = Naming.make_bone_name(curve_obj.name, spline_no, point_no, LR)
    pose_bone = armature.pose.bones[bone_name]

    # ワールド空間上にCurveとBoneのベクトルを展開
    curve_vec = (curve_obj.matrix_world @ spline.points[point_no+1].co.xyz - curve_obj.matrix_world @ spline.points[point_no].co.xyz).normalized()
    if LR == "R":
        curve_vec.x = -curve_vec.x  # Mirror側
    bone_vec = pose_bone.y_axis.xyz @ armature.matrix_world.inverted_safe().to_3x3() @ parent_world_qt.to_matrix().to_3x3()

    # Worldで回転軸を出してPose座標系に変換
    world_axis = curve_vec.cross(bone_vec).normalized()
    if world_axis.length == 0:
        return
    pose_axis = world_axis @ armature.matrix_world.to_3x3() @ pose_bone.matrix.to_3x3() @ parent_pose_qt.to_matrix().to_3x3()

    # 誤差対策付き角度だし
    rad = math.acos(min(1, max(-1, curve_vec.dot(bone_vec))))

    # Pose座標系でボーンの回転
    pose_bone.rotation_quaternion = mathutils.Quaternion(pose_axis, -rad)

    # 回転を子に伝搬
    _rec_pose_bone_fit_process(
        armature,
        curve_obj,
        spline_no,
        point_no+1,
        parent_world_qt @ mathutils.Quaternion(world_axis, rad),
        parent_pose_qt @ pose_bone.rotation_quaternion,
        LR)

