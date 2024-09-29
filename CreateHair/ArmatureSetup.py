import bpy, mathutils
import math

from ..Util import Naming

# AHT用のArmatureのセットアップを行う
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_setup_armature(bpy.types.Operator):
    bl_idname = "anime_hair_tools.setup_armature"
    bl_label = "Create & Setup"

    # execute
    def execute(self, context):
        scene = context.scene

        parent_armature = bpy.data.objects.get(scene.AHT_parent_armature_name)
        if parent_armature == None:
            parent_bone = None
        else:
            parent_bone = parent_armature.data.bones.get(scene.AHT_parent_bone_name)

        # armature
        # -------------------------------------------------------------------------
        # ない時だけ新たに作る
        if scene.AHT_armature_name in bpy.data.objects.keys():
            armature = bpy.data.objects[scene.AHT_armature_name]
        else:
            armature = self.create_armature(context)

        armature.parent = parent_armature

        # root_bone設定
        # -------------------------------------------------------------------------
        context.view_layer.objects.active = armature

        # 名前
        armature.data.bones[0].name = scene.AHT_root_bone_name

        # 親子付け
        if parent_armature != None:
            armature.parent = parent_armature
            armature.parent_type = 'BONE'
        if parent_bone != None:
            armature.parent_bone = parent_bone.name

        # 座標
        if parent_bone != None:
            bpy.ops.object.mode_set(mode='EDIT')
            armature.data.edit_bones[0].head = parent_bone.head + mathutils.Vector((0, 0, -0.5))
            armature.data.edit_bones[0].tail = parent_bone.head
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

        # 初回限定処理
        # -------------------------------------------------------------------------
        armature.data.collections[0].name = Naming.make_bone_collection_name("Root")

        return armature


# Delete the constraints added for management
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_remove_all(bpy.types.Operator):
    bl_idname = "anime_hair_tools.remove_all"
    bl_label = "Remove All"

    # execute ok
    def execute(self, context):
        # backup_active = bpy.context.view_layer.objects.active

        # selected_curve_objs = [obj for obj in context.selected_objects if obj.type == "CURVE"]
        # # Curveが１つも選択されていなかった
        # if len(selected_curve_objs) == 0:
        #     return{'FINISHED'}

        # # remove child bones
        # if bpy.data.objects.get(context.scene.AHT_armature_name) != None:  # ATHのArmatureがあるときだけBoneを消せる
        #     BoneManager.remove(context, selected_curve_objs)  # ボーンを削除

        # # remove mesh
        # MeshManager.remove(context, selected_curve_objs)

        # # 後始末
        # # ---------------------------------------------------------------------
        # bpy.ops.object.select_all(action='DESELECT')
        # for curve in selected_curve_objs:  # 対象となったCurveを選択状態に戻しておく
        #     curve.select_set(True)
        # bpy.context.view_layer.objects.active = backup_active

        return{'FINISHED'}


# UI描画設定
# =================================================================================================
classes = [
    ANIME_HAIR_TOOLS_OT_setup_armature,
    ANIME_HAIR_TOOLS_OT_remove_all,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
