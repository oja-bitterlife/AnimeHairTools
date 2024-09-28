import bpy, mathutils
import math

from . import BoneManager
from ..Util import Naming

# AHT用のArmatureのセットアップを行う
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_setup_armature(bpy.types.Operator):
    bl_idname = "anime_hair_tools.setup_armature"
    bl_label = "Setup Armature and RootBone"

    # execute
    def execute(self, context):
        scene = context.scene

        parent_armature = bpy.data.objects[scene.AHT_parent_armature_name]
        parent_bone = parent_armature.data.bones[scene.AHT_parent_bone_name]

        # armature
        # -------------------------------------------------------------------------
        # ない時だけ新たに作る
        if scene.AHT_armature_name in bpy.data.objects.keys():
            armature = bpy.data.objects[scene.AHT_armature_name]
        else:
            armature = self.create_armature(context)

        armature.parent = parent_armature

        # root_bone
        # -------------------------------------------------------------------------
        armature.data.bones[0].name = scene.AHT_root_bone_name  # 名前を修正
        armature.parent = parent_armature
        armature.parent_type = 'BONE'
        armature.parent_bone = parent_bone.name

        # 設定
        # -------------------------------------------------------------------------
        context.view_layer.objects.active = armature

        # 座標設定
        bpy.ops.object.mode_set(mode='EDIT')
        armature.data.edit_bones[0].head = parent_bone.head
        armature.data.edit_bones[0].tail = parent_bone.head + mathutils.Vector((0, 0, -0.5))
        bpy.ops.object.mode_set(mode='OBJECT')

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
        # bpy.ops.object.select_all(action='DESELECT')
        # bpy.context.view_layer.objects.active = armature
        # bpy.ops.object.mode_set(mode='EDIT')
        # armature.data.edit_bones[0].select = True
        # armature.data.edit_bones[0].tail = (0, 1, 0)
        # bpy.ops.object.mode_set(mode='POSE')
        # bpy.context.active_pose_bone.rotation_mode = 'XYZ'
        # bpy.ops.object.mode_set(mode='OBJECT')

        # 初回限定処理
        # -------------------------------------------------------------------------
        armature.data.collections[0].name = "AHT_Root"

        # Armatureコンストレイントも用意しておく
        constraint = armature.pose.bones[0].constraints.new("ARMATURE")
        constraint.name = Naming.make_constraint_name("parent")

        return armature


# create constraints and controll bone
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_create(bpy.types.Operator):
    bl_idname = "anime_hair_tools.create"
    bl_label = "Create Mesh & Bones"

    # execute ok
    def execute(self, context):
        armature = bpy.data.objects[context.scene.AHT_armature_name]
        selected_curve_objs = [obj for obj in context.selected_objects if obj.type == "CURVE"]
        backup_active = bpy.context.view_layer.objects.active

        # Curveが１つも選択されていなかった
        if len(selected_curve_objs) == 0:
            return{'FINISHED'}

        # 一旦今までのものを削除
        # ---------------------------------------------------------------------
        BoneManager.remove(context, selected_curve_objs)  # Boneを削除
        MeshManager.remove(context, selected_curve_objs)  # Meshも削除

        # 作り直す
        # ---------------------------------------------------------------------
        # create mesh
        meshed_curve_list_group = MeshManager.create(context, selected_curve_objs)
        # create bones
        BoneManager.create(context, selected_curve_objs, meshed_curve_list_group)
        # JOIN & 名前設定
        MeshManager.join_and_settings(selected_curve_objs, meshed_curve_list_group)

        # 後始末
        # ---------------------------------------------------------------------
        bpy.ops.object.select_all(action='DESELECT')
        for curve in selected_curve_objs:  # 対象となったCurveを選択状態に戻しておく
            curve.select_set(True)
        bpy.context.view_layer.objects.active = backup_active

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
        backup_active = bpy.context.view_layer.objects.active

        selected_curve_objs = [obj for obj in context.selected_objects if obj.type == "CURVE"]
        # Curveが１つも選択されていなかった
        if len(selected_curve_objs) == 0:
            return{'FINISHED'}

        # remove child bones
        if bpy.data.objects.get(context.scene.AHT_armature_name) != None:  # ATHのArmatureがあるときだけBoneを消せる
            BoneManager.remove(context, selected_curve_objs)  # ボーンを削除

        # remove mesh
        MeshManager.remove(context, selected_curve_objs)

        # 後始末
        # ---------------------------------------------------------------------
        bpy.ops.object.select_all(action='DESELECT')
        for curve in selected_curve_objs:  # 対象となったCurveを選択状態に戻しておく
            curve.select_set(True)
        bpy.context.view_layer.objects.active = backup_active

        return{'FINISHED'}


# UI描画設定
# =================================================================================================
classes = [
    ANIME_HAIR_TOOLS_OT_setup_armature,
    ANIME_HAIR_TOOLS_OT_create,
    ANIME_HAIR_TOOLS_OT_remove,
]

def draw(parent, context, layout):
    # Armature生成
    # ---------------------------------------------------------------------
    layout.label(text="Armature and RootBone Setting:")
    box = layout.box()
    box.enabled = context.mode == "OBJECT"

    # ATHのArmatureの設定
    box.prop(context.scene, "AHT_armature_name", text="Armature")
    box.prop(context.scene, "AHT_root_bone_name", text="RootBone")
    box.prop(context.scene, "AHT_parent_armature_name", text="ParentArmature")
    row = box.row()
    row.prop(context.scene, "AHT_parent_bone_group", text="ParentBone")
    row.prop(context.scene, "AHT_parent_bone_name", text="")

    # 実行
    box.operator("anime_hair_tools.setup_armature")

    # Mesh化&Bone生成
    # ---------------------------------------------------------------------
    layout.label(text="Mesh & Bones Setting:")
    box = layout.box()
    box.enabled = context.mode == "OBJECT" and (bpy.context.view_layer.objects.active != None and bpy.context.view_layer.objects.active.type == "CURVE")

    box.prop(context.scene, "AHT_subdivision", text="Use Subdivision Modifire")
    box.prop(context.scene, "AHT_bbone", text="Bendy Bones")
    box.prop(context.scene, "AHT_create_layer", text="Bone Create Layer")
    box.operator("anime_hair_tools.create")
    box.operator("anime_hair_tools.remove")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
