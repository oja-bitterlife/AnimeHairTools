import bpy
import math

from .Util.ListupUtil import ListupProperty


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


# UI描画設定
# =================================================================================================
def ui_draw(context, layout):
    layout.label(text="Armature and RootBone Setting:")
    box = layout.box()

    # ATHのArmatureの設定
    box.prop(context.scene, "AHT_armature_name", text="Armature")
    box.prop(context.scene, "AHT_root_bone_name", text="RootBone")

    # コンストレイント先設定
    box.label(text="Parent Target:")
    box.prop(context.scene.AHT_parent_target_name, "armature", text="Armature")
    box.prop(context.scene.AHT_parent_target_name, "bone", text="Bone")

    # 実行
    box.operator("anime_hair_tools.setup_armature")


# =================================================================================================
def register():
    # Armature設定用
    bpy.types.Scene.AHT_armature_name = bpy.props.StringProperty(name = "armature name", default="AHT_Armature")
    bpy.types.Scene.AHT_root_bone_name = bpy.props.StringProperty(name = "bone root name", default="AHT_RootBone")

    bpy.types.Scene.AHT_parent_target_name = bpy.props.PointerProperty(type=ListupProperty)
