import bpy, math, mathutils
import re

from ..Util import Naming


# ボーン作成
# =================================================================================================
# create controll bone
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_create_bones(bpy.types.Operator):
    bl_idname = "anime_hair_tools.create"
    bl_label = "Create Bones"

    # execute ok
    def execute(self, context):
        armature = bpy.data.objects[context.scene.AHT_armature_name]
        backup_active = bpy.context.view_layer.objects.active
        selected_curve_objs = [obj for obj in context.selected_objects if obj.type == "CURVE"]

        # 一旦今までのものを削除
        # ---------------------------------------------------------------------
        # Boneを削除
        remove(context, armature, selected_curve_objs)

        # 作り直す
        # ---------------------------------------------------------------------
        # create bones
        create(context, armature, selected_curve_objs)

        # 後始末
        # ---------------------------------------------------------------------
        bpy.ops.object.select_all(action='DESELECT')
        for curve in selected_curve_objs:  # 対象となったCurveを選択状態に戻しておく
            curve.select_set(True)
        bpy.context.view_layer.objects.active = backup_active

        return{'FINISHED'}


def create(context, armature, selected_curve_objs):
    bpy.context.view_layer.objects.active = armature

    # BoneCollectionがなければ作っておく
    bone_collection_name = context.scene.AHT_bone_collection_name
    if armature.data.collections.get(bone_collection_name) == None:
        armature.data.collections.new(bone_collection_name)

    # 格納先のコレクションをアクティブに
    armature.data.collections.active_index = armature.data.collections.find(bone_collection_name)

    # Curveごとに回す
    point_offset = 0
    for curve in selected_curve_objs:
        # Curve１本１本処理する
        for spline_no in range(len(curve.data.splines)):
            # ボーン生成
            _create_curve_bones(context, armature, curve, spline_no)

            # hookモディファイア生成
            _create_curve_modifires(context, armature, curve, spline_no, point_offset)

            # Curve上のセグメントのインデックスを取得するためのオフセット
            point_offset += len(curve.data.splines[spline_no].points)

# create bone chain
# *****************************************************************************
def _create_curve_bones(context, armature, curve, spline_no):
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')

    # mode_setの後でないと取得してはいけない
    spline = curve.data.splines[spline_no]


    # 連結最初のボーンを基準にする
    first_bone = None

    # セグメントごとにボーンを作成する
    for point_no in range(len(spline.points)-1):  # ボーンの数はセグメント数-1
        # if MirrorName == "R" and meshed_curve_obj.vertex_groups[i].name.endswith(".L"):
        #     bone_name = bone_name[:-2] + ".R"  # R側

        # ボーン作成
        bone_name = Naming.make_bone_name(curve.name, spline_no, point_no)
        bpy.ops.armature.bone_primitive_add(name=bone_name)
        new_bone = armature.data.edit_bones[bone_name]

        # Bone設定
        # ---------------------------------------------------------------------
        world_matrix = armature.matrix_world.inverted() @ curve.matrix_world
        # ボーンの位置を計算
        bgn = world_matrix @ spline.points[point_no].co.xyz
        end = world_matrix @ spline.points[point_no+1].co.xyz

        # 親子設定
        if point_no == 0:  # セグメントの先頭ボーンは親がルートボーン
            new_bone.parent = armature.data.edit_bones[context.scene.AHT_root_bone_name]
            new_bone.head = bgn.xyz
            new_bone.use_connect = False
        else:
            parent_bone_name = Naming.make_bone_name(curve.name, spline_no, point_no-1)
            new_bone.parent = armature.data.edit_bones[parent_bone_name]
            new_bone.head = new_bone.parent.tail
            new_bone.use_connect = True

        new_bone.tail= end.xyz

        # rollも設定(オブジェクト中心ベース)
        x_axis = spline.points[point_no].co.xyz.normalized().cross(mathutils.Vector((0, 0, -1))).normalized()
        z_axis = x_axis.cross(new_bone.y_axis).normalized()
        new_bone.align_roll(z_axis)
        new_bone.roll += spline.points[point_no].tilt*0.5  # tiltも反映(360度で半周してる？)

    bpy.ops.object.mode_set(mode='OBJECT')

def _create_curve_modifires(context, armature, curve, spline_no, point_offset):
    bpy.context.view_layer.objects.active = curve
    bpy.ops.object.mode_set(mode='EDIT')

    # mode_setの後でないと取得してはいけない
    spline = curve.data.splines[spline_no]

    # 最初からあるモディファイアの数
    original_mods_num = len(curve.modifiers)

    # セグメントごとにhookを作成
    for point_no in range(len(spline.points)-1):  # ボーンの数はセグメント数-1
        bone_name = Naming.make_bone_name(curve.name, spline_no, point_no)
        hook = curve.modifiers.new(type = "HOOK", name = Naming.make_hook_name(bone_name))
        hook.object = armature
        hook.subtarget = bone_name
        hook.show_expanded = False

        # 最後尾に付いたhookを前に移動させる
        curve.modifiers.move(len(curve.modifiers)-1, len(curve.modifiers)-1-original_mods_num)

        # セグメントをassignする
        hook.vertex_indices_set([point_no+1+point_offset])

    bpy.ops.object.mode_set(mode='OBJECT')

# 削除
# =================================================================================================
# Delete bones and modifires
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_remove_bones(bpy.types.Operator):
    bl_idname = "anime_hair_tools.remove"
    bl_label = "Remove Bones"

    # execute ok
    def execute(self, context):
        armature = bpy.data.objects[context.scene.AHT_armature_name]
        backup_active = bpy.context.view_layer.objects.active
        selected_curve_objs = [obj for obj in context.selected_objects if obj.type == "CURVE"]

        # remove child bones
        remove(context, armature, selected_curve_objs)  # ボーンを削除

        # 後始末
        # ---------------------------------------------------------------------
        bpy.ops.object.select_all(action='DESELECT')
        for curve in selected_curve_objs:  # 対象となったCurveを選択状態に戻しておく
            curve.select_set(True)
        bpy.context.view_layer.objects.active = backup_active

        return{'FINISHED'}

def remove(context, armature, selected_curve_objs):
    bpy.context.view_layer.objects.active = armature

    # 一旦全部選択解除
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.armature.select_all(action='DESELECT')

    # 消すべきBoneを選択
    for curve_obj in selected_curve_objs:
        bone_basename = Naming.make_bone_basename(curve_obj.name)
        for bone in armature.data.edit_bones:
            bone.select = bone.name.startswith(bone_basename)

        # 一括削除(Curveごとじゃないと失敗する)
        bpy.ops.armature.delete()

    # OBJECTモードに戻す
    bpy.ops.object.mode_set(mode='OBJECT')

    # hookも削除する
    for curve_obj in selected_curve_objs:
        for mod in curve_obj.modifiers:
            # 名前で判別
            if mod.type == "HOOK" and mod.name.startswith(Naming.HOOK_PREFIX):
                curve_obj.modifiers.remove(mod)


# UI描画設定
# =================================================================================================
classes = [
    ANIME_HAIR_TOOLS_OT_create_bones,
    ANIME_HAIR_TOOLS_OT_remove_bones,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
