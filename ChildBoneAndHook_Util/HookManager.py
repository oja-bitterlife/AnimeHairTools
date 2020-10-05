import bpy

from . import Naming


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
                hook_name = Naming.make_modifier_name(curve_obj.name, spline_no, target_bone_no)

                # create modifier
                curve_obj.modifiers.new(hook_name, type="HOOK")
                new_modifier = curve_obj.modifiers[hook_name]

                # setup
                # -------------------------------------------------------------------------
                new_modifier.object = armature
                new_modifier.subtarget = Naming.make_bone_name(curve_obj.name, spline_no, target_bone_no)

                # ついでにHook
                if target_bone_no == 0:
                    new_modifier.vertex_indices_set([hook_offset, hook_offset + 1])  # 0と1両方設定
                else:
                    new_modifier.vertex_indices_set([hook_offset + target_bone_no+1])

            # hook用のpointのindexが取れないので、計算で出してみる用
            hook_offset += len(spline.points)


        # hook_modifire以外を後ろに持っていく
        # *********************************************************************
        # 処理するCurveをActiveにしておく必要があるっぽい
        bpy.context.view_layer.objects.active = curve_obj

        # Hookモディファイアでなければ、モディファイアの数だけ下に移動する
        hook_basename = Naming.make_modifier_basename(curve_obj.name) + Naming.HOOK_MODIFIRE_SEPALATER
        for modifier in curve_obj.modifiers:
            # Hookモディファイアを見つけたらそこで終了
            if modifier.name.startswith(hook_basename):
                break

            # Hookモディファイアでない間は下に移動
            for i in range(len(curve_obj.modifiers)-1):
                bpy.ops.object.modifier_move_down(modifier=modifier.name)


# Hookの削除
# =================================================================================================
def remove(context, selected_curve_objs):
    # 選択中のCurveに適用
    for curve_obj in selected_curve_objs:
        # 処理するCurveをActiveにしておく必要があるっぽい
        bpy.context.view_layer.objects.active = curve_obj

        # CurveオブジェクトについているすべてのATH用モディファイアを消す
        hook_basename = Naming.make_modifier_basename(curve_obj.name) + Naming.HOOK_MODIFIRE_SEPALATER
        for modifier in curve_obj.modifiers:
            if modifier.name.startswith(hook_basename):
                bpy.ops.object.modifier_remove(modifier=modifier.name)
