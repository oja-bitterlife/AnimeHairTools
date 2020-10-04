import bpy

from . import ChildBoneManager


HOOK_MODIFIRE_PREFIX = "AHT_HookModifire"
HOOK_MODIFIRE_SEPALATER = "@"


# name utility
# =================================================================================================
def make_modifier_basename(base_name):
    return HOOK_MODIFIRE_PREFIX + "." + base_name

def make_modifier_name(base_name, spline_no, point_no):
    return make_modifier_basename(base_name) + HOOK_MODIFIRE_SEPALATER + "{}.{:0=3}".format(spline_no, point_no)


# create hook modifiers
# =================================================================================================
def create(context, selected_curve_objs):
    armature = bpy.data.objects[context.scene.AHT_armature_name]

    # Curve全部に付ける
    for curve_obj in selected_curve_objs:
        hook_offset = 0  # 複数curveに対応

        # spline単位で処理
        for spline_no, spline in enumerate(curve_obj.data.splines):
            # 頂点ごとにHookを作成する
            for target_bone_no in range(len(spline.points)-1):
                hook_name = make_modifier_name(curve_obj.name, spline_no, target_bone_no)

                # create modifier
                curve_obj.modifiers.new(hook_name, type="HOOK")
                new_modifier = curve_obj.modifiers[hook_name]

                # setup
                # -------------------------------------------------------------------------
                new_modifier.object = armature
                new_modifier.subtarget = ChildBoneManager.make_bone_name(curve_obj.name, spline_no, target_bone_no)

                # ついでにHook
                new_modifier.vertex_indices_set([hook_offset + target_bone_no+1])

            # hook用のpointのindexが取れないので、計算で出してみる用
            hook_offset += len(spline.points)


# Hookの削除
# =================================================================================================
def remove(context, selected_curve_objs):
    # 選択中のCurveに適用
    for curve_obj in selected_curve_objs:
        # CurveオブジェクトについているすべてのATH用モディファイアを消す
        hook_basename = make_modifier_basename(curve_obj.name) + HOOK_MODIFIRE_SEPALATER
        for modifier in curve_obj.modifiers:
            if modifier.name.startswith(hook_basename):
                bpy.ops.object.modifier_remove(modifier=modifier.name)
