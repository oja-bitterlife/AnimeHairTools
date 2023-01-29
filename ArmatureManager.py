import bpy
import math

from .Util.ListupUtil import ListupProperty
from .Util import ArmatureMode
from .Util import BoneManager, MeshManager
from . import CurveStraighten


# AHT用のArmatureのセットアップを行う
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_setup_armature(bpy.types.Operator):
    bl_idname = "anime_hair_tools.setup_armature"
    bl_label = "Setup Armature and RootBone"

    # execute
    def execute(self, context):
        scene = context.scene
        # armature
        # -------------------------------------------------------------------------
        # ない時だけ新たに作る
        if scene.AHT_armature_name not in bpy.data.objects.keys():
            self.create_armature(context)
        armature = bpy.data.objects[scene.AHT_armature_name]

        # root_bone
        # -------------------------------------------------------------------------
        armature.data.bones[0].name = scene.AHT_root_bone_name

        # parent 設定
        # -------------------------------------------------------------------------
        if scene.AHT_parent_target_name.armature == "_empty_for_delete":
             # parentの削除
            armature.parent = None
        else:
            # parentの設定
            armature.parent = bpy.data.objects[scene.AHT_parent_target_name.armature]
            armature.parent_type = "BONE"
            armature.parent_bone = scene.AHT_parent_target_name.bone

        return{'FINISHED'}

    # ATH用のArmatureを作成する。root_bone付き
    def create_armature(self, context):
        scene = context.scene

        # Armatureの作成
        # -------------------------------------------------------------------------
        bpy.ops.object.armature_add(enter_editmode=False, location=(0, 0, 0))
        armature = bpy.context.active_object

        # Collectionの中に入って迷子にならないように、先頭に出しておく
        if armature.users_scene[0].collection.objects.get(armature.name) == None:  # TOPレベルにいなければ
            armature.users_scene[0].collection.objects.link(armature)  # TOPレベルからリンク
            armature.users_collection[0].objects.unlink(armature)  # 現在のコレクションからunlink

        # set name
        armature.name = scene.AHT_armature_name
        armature.data.name = scene.AHT_armature_name

        # other setup
        # -------------------------------------------------------------------------
        armature.show_in_front = True  # 常に手前
        armature.data.display_type = 'WIRE'  # WIRE表示

        # 見やすいように奥向きに設定しておく
        # -------------------------------------------------------------------------
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='EDIT')
        armature.data.edit_bones[0].select = True
        armature.data.edit_bones[0].tail = (0, 1, 0)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.object.rotation_euler[0] = -math.pi/2


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

        for curve in selected_curve_objs:  # 対象となったCurveを選択状態に戻しておく
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
class ANIME_HAIR_TOOLS_PT_setup_hair_armature(bpy.types.Panel):
    bl_label = "Setup Hair Armature"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "APT_HAIR_PT_UI"
    bl_options = {'HEADER_LAYOUT_EXPAND'}

    def draw(self, context):
        if context.mode != "OBJECT":
            self.layout.enabled = False

        # Armature生成
        # ---------------------------------------------------------------------
        self.layout.label(text="Armature and RootBone Setting:")
        box = self.layout.box()

        # ATHのArmatureの設定
        box.prop(context.scene, "AHT_armature_name", text="Armature")
        box.prop(context.scene, "AHT_root_bone_name", text="RootBone")

        # コンストレイント先設定
        box.label(text="Parent Target:")
        box.prop(context.scene.AHT_parent_target_name, "armature", text="Armature")
        box.prop(context.scene.AHT_parent_target_name, "bone", text="Bone")

        # 実行
        box.operator("anime_hair_tools.setup_armature")

        # Mesh化&Bone生成
        # ---------------------------------------------------------------------
        self.layout.label(text="Mesh & Bones Setting:")
        box = self.layout.box()
        box.prop(context.scene, "AHT_subdivision", text="Use Subdivision Modifire")
        box.prop(context.scene, "AHT_bbone", text="Bendy Bones")
        box.prop(context.scene, "AHT_create_layer", text="Bone Create Layer")
        box.operator("anime_hair_tools.create")
        box.operator("anime_hair_tools.remove")


# =================================================================================================
def register():
    # Armature設定用
    bpy.types.Scene.AHT_armature_name = bpy.props.StringProperty(name = "armature name", default="AHT_Armature")
    bpy.types.Scene.AHT_root_bone_name = bpy.props.StringProperty(name = "bone root name", default="AHT_RootBone")

    bpy.types.Scene.AHT_parent_target_name = bpy.props.PointerProperty(type=ListupProperty)

    # Bone設定
    bpy.types.Scene.AHT_bbone = bpy.props.IntProperty(name = "BendyBone split", default=3, min=1, max=32)
    bpy.types.Scene.AHT_create_layer = bpy.props.IntProperty(name = "Bone Create Layer", default=1, min=1, max=32)

    # モディファイア設定
    bpy.types.Scene.AHT_subdivision = bpy.props.BoolProperty(name = "With Subdivision", default=True)
