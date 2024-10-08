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


# UI描画設定
# =================================================================================================
classes = [
    ANIME_HAIR_TOOLS_OT_setup_armature,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
