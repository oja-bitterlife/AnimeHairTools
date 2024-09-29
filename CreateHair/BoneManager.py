
import bpy, math, mathutils
import re

from ..Util import Naming


# ボーン作成
# =================================================================================================
# create constraints and controll bone
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

    # to edit-mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Curveごとに回す
    for curve in selected_curve_objs:
        # Curve１本１本処理する
        for spline_no,spline in enumerate(curve.data.splines):
            # # ミラーチェック
            # MirrorName = None if len(MirrorUtil.find_mirror_modifires(meshed_curve_obj)) == 0 else "L"

            _create_curve_bones(context, armature, curve, spline_no, spline)
            # if MirrorName != None:
            #     edit_bones += _create_curve_bones(context, armature, spline, meshed_curve_obj, straight_points_list[list_no], "R")  # Curve１本１本処理する

    # OBJECTモードに戻すのを忘れないように
    bpy.ops.object.mode_set(mode='OBJECT')


# create bone chain
# *****************************************************************************
def _create_curve_bones(context, armature, curve, spline_no, spline):
    # セグメントごとにボーンを作成する
    created_bones = []
    for point_no in range(len(spline.points)-1):  # ボーンの数はセグメント数-1
        # if MirrorName == "R" and meshed_curve_obj.vertex_groups[i].name.endswith(".L"):
        #     bone_name = bone_name[:-2] + ".R"  # R側

        # ボーン作成
        bone_name = Naming.make_bone_name(curve.name, spline_no, point_no)
        bpy.ops.armature.bone_primitive_add(name=bone_name)
        new_bone = armature.data.edit_bones[bone_name]

        # 作ったボーンを覚えておく
        created_bones.append(new_bone)

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
            new_bone.parent = created_bones[point_no-1]
            new_bone.head = new_bone.parent.tail
            new_bone.use_connect = True

        new_bone.tail= end.xyz

        # rollも設定
        forward_axis = world_matrix.to_3x3() @ mathutils.Vector((0, 1, 0))
        z_axis = new_bone.y_axis.cross(forward_axis).normalized()
        new_bone.align_roll(-z_axis)
        new_bone.roll += spline.points[point_no].tilt
       
        # # .R側だった場合はBoneをX軸反転
        # if MirrorName == "R":
        #     bgn.x = -bgn.x
        #     end.x = -end.x

        #     # head/tailを設定しなおし(Roll設定に影響しないよう代入しなおしで実施)
        #     if i == 0:
        #         new_bone.head = bgn.xyz  # disconnected head setup
        #     new_bone.tail = end.xyz

        #     # Mirror側はrollが逆転
        #     new_bone.roll = -new_bone.roll

    return created_bones


# 削除
# =================================================================================================
# Delete the constraints added for management
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

    # 一括削除
    bpy.ops.armature.delete()

    # OBJECTモードに戻すのを忘れないように
    bpy.ops.object.mode_set(mode='OBJECT')



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
