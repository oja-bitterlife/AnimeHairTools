import bpy

from .Util import ArmatureMode
from .Util import BoneManager, MeshManager
from . import CurveStraighten


# create constraints and controll bone
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_create(bpy.types.Operator):
    bl_idname = "anime_hair_tools.create"
    bl_label = "Create Mesh & Bones"

    # execute ok
    def execute(self, context):
        armature = bpy.data.objects[context.scene.AHT_armature_name]
        selected_curve_objs = [obj for obj in context.selected_objects if obj.type == "CURVE"]

        # Curveが１つも選択されていなかった
        if len(selected_curve_objs) == 0:
            return{'FINISHED'}

        # 一旦今までのものを削除
        # ---------------------------------------------------------------------
        BoneManager.remove(context, selected_curve_objs)  # Boneを削除
        MeshManager.remove(context, selected_curve_objs)  # Meshも削除


        # 破壊してもいいようコピーしたものを使う
        # ---------------------------------------------------------------------
        # Curveだけ選択状態にする
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected_curve_objs:
            obj.select_set(True)
        bpy.ops.object.duplicate(linked=False)  # Curveだけ複製
        tmp_curve_objs = [obj for obj in context.selected_objects if obj.type == "CURVE"]

        # Curveをストレート化
        ArmatureMode.to_edit_mode(context, armature)
        for curve in tmp_curve_objs:
            for spline in curve.data.splines:
                if spline.type == "NURBS":
                    CurveStraighten.execute_nurbs_straighten(spline, True, True)
        ArmatureMode.return_obuject_mode()


        # 作り直す
        # ---------------------------------------------------------------------
        # create bones
        BoneManager.create(context, tmp_curve_objs, selected_curve_objs)
        # create mesh
        MeshManager.create(context, tmp_curve_objs, selected_curve_objs)


        # 後始末
        # ---------------------------------------------------------------------
        # ストレート化用に作ったCurveを削除する
        bpy.ops.object.select_all(action='DESELECT')
        for obj in tmp_curve_objs:
            obj.select_set(True)
        bpy.ops.object.delete()
        context.view_layer.objects.active = armature

        for curve in selected_curve_objs:
            curve.select_set(True)


        # ボーンの形状を元のカーブに合わせておく
        # ---------------------------------------------------------------------
        BoneManager.pose_bone_fit_curve(armature, selected_curve_objs)


        return{'FINISHED'}


    # ATH_Armatureを先に作る必要がある
    @classmethod
    def poll(cls, context):
        return bpy.data.objects.get(context.scene.AHT_armature_name) != None


# Delete the constraints added for management
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_remove(bpy.types.Operator):
    bl_idname = "anime_hair_tools.remove"
    bl_label = "Remove Mesh & Bones"

    # execute ok
    def execute(self, context):
        selected_curve_objs = [obj for obj in context.selected_objects if obj.type == "CURVE"]
        # Curveが１つも選択されていなかった
        if len(selected_curve_objs) == 0:
            return{'FINISHED'}

        # remove child bones
        if bpy.data.objects.get(context.scene.AHT_armature_name) != None:  # ATHのArmatureがあるときだけBoneを消せる
            BoneManager.remove(context, selected_curve_objs)  # ボーンを削除

        # remove mesh
        MeshManager.remove(context, selected_curve_objs)

        return{'FINISHED'}


# UI描画設定
# =================================================================================================
def ui_draw(context, layout):
    layout.label(text="Mesh & Bones Setting:")

    box = layout.box()

    # 実行
    box.prop(context.scene, "AHT_subdivision", text="Use Subdivision Modifire")
    box.prop(context.scene, "AHT_bbone", text="Bendy Bones")
    box.prop(context.scene, "AHT_create_layer", text="Bone Create Layer")
    box.operator("anime_hair_tools.create")
    box.operator("anime_hair_tools.remove")


# =================================================================================================
def register():
    # Bone設定
    bpy.types.Scene.AHT_bbone = bpy.props.IntProperty(name = "BendyBone split", default=3, min=1, max=32)
    bpy.types.Scene.AHT_create_layer = bpy.props.IntProperty(name = "Bone Create Layer", default=1, min=1, max=32)
    # モディファイア設定
    bpy.types.Scene.AHT_subdivision = bpy.props.BoolProperty(name = "With Subdivision", default=True)
