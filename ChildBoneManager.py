
import bpy

from . import HookManager


HOOK_BONE_PREFIX = "AHT_HookBone"
HOOK_BONE_SEPALATER = "@"


# name utility
# =================================================================================================
def make_bone_basename(base_name):
    return HOOK_BONE_PREFIX + "." + base_name

def make_bone_name(base_name, spline_no, point_no):
    return make_bone_basename(base_name) + HOOK_BONE_SEPALATER + "{}.{:0=3}".format(spline_no, point_no)


# ボーン作成
# =================================================================================================
def create(context, selected_curve_objs):
    armature = bpy.data.objects[context.scene.AHT_armature_name]
    bpy.context.view_layer.objects.active = armature

    # to edit-mode
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')

    # Curveごとに回す
    for curve_obj in selected_curve_objs:
        _create_curve_bones(context, armature, curve_obj)  # Curve１本１本処理する

    # OBJECTモードに戻すのを忘れないように
    bpy.ops.object.mode_set(mode='OBJECT')


# create bone chain
# *****************************************************************************
def _create_curve_bones(context, armature, curve_obj):
    root_matrix = armature.matrix_world.inverted() @ curve_obj.matrix_world

    # spline単位で処理
    for spline_no, spline in enumerate(curve_obj.data.splines):
        # 頂点ごとにボーンを作成する
        parent = armature.data.edit_bones[context.scene.AHT_root_bone_name]  # 最初はRootBoneが親
        for i in range(len(spline.points)-1):
            # Bone生成
            bone_name = make_bone_name(curve_obj.name, spline_no, i)
            bpy.ops.armature.bone_primitive_add(name=bone_name)
            new_bone = armature.data.edit_bones[bone_name]

            # Bone設定
            new_bone.parent = parent  # 親子設定

            new_bone.use_connect = i != 0  # チェインの開始位置をrootとは接続しない

            # ボーンをCurveに合わせて配置
            bgn = root_matrix @ spline.points[i].co
            end = root_matrix @ spline.points[i+1].co
            if i == 0:
                new_bone.head = bgn.xyz  # disconnected head setup
            new_bone.tail = end.xyz

            # 自分を親にして次をつなげていく
            parent = new_bone


# 削除
# =================================================================================================
def remove(context, selected_curve_objs):
    armature = bpy.data.objects[context.scene.AHT_armature_name]

    # to edit-mode
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')

    # 一旦全部選択解除
    bpy.ops.armature.select_all(action='DESELECT')

    # 消すべきBoneを選択
    for curve_obj in selected_curve_objs:
        bone_basename = make_bone_basename(curve_obj.name) + HOOK_BONE_SEPALATER
        for bone in armature.data.edit_bones:
            bone.select = bone.name.startswith(bone_basename)

    # 一括削除
    bpy.ops.armature.delete()

    # OBJECTモードに戻すのを忘れないように
    bpy.ops.object.mode_set(mode='OBJECT')
