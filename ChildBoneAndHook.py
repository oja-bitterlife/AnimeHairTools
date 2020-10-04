import bpy

from . import ChildBoneManager, HookManager


# create constraints and controll bone
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_create_bone_and_hook(bpy.types.Operator):
    bl_idname = "anime_hair_tools.create_bone_and_hook"
    bl_label = "Create ChildBone and Hook"

    # execute ok
    def execute(self, context):
        selected_curve_objs = [obj for obj in context.selected_objects if obj.type == "CURVE"]

        # Curveが１つも選択されていなかった
        if len(selected_curve_objs) == 0:
            return{'FINISHED'}

        # 一旦今までのものを削除
        # ---------------------------------------------------------------------
        HookManager.remove(context, selected_curve_objs)  # Hookを削除
        ChildBoneManager.remove(context, selected_curve_objs)  # ボーンを削除

        # 作り直す
        # ---------------------------------------------------------------------
        # create bones
        ChildBoneManager.create(context, selected_curve_objs)

        # create hook
        HookManager.create(context, selected_curve_objs)

        return{'FINISHED'}

    # ATH_Armatureを先に作る必要がある
    @classmethod
    def poll(cls, context):
        return bpy.data.objects.get(context.scene.AHT_armature_name) != None


# Delete the constraints added for management
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_remove_bone_and_hook(bpy.types.Operator):
    bl_idname = "anime_hair_tools.remove_bone_and_hook"
    bl_label = "Remove ChildBone and Hook"

    # execute ok
    def execute(self, context):
        selected_curve_objs = [obj for obj in context.selected_objects if obj.type == "CURVE"]
        # Curveが１つも選択されていなかった
        if len(selected_curve_objs) == 0:
            return{'FINISHED'}

        # remove modifiers
        HookManager.remove(context, selected_curve_objs)  # Hookを削除

        # remove child bones
        if bpy.data.objects.get(context.scene.AHT_armature_name) != None:  # ATHのArmatureがあるときだけBoneを消せる
            ChildBoneManager.remove(context, selected_curve_objs)  # ボーンを削除

        return{'FINISHED'}


# UI描画設定
# =================================================================================================
def ui_draw(context, layout):
    layout.label(text="Bone and Hook Setting:")

    box = layout.box()

    # 実行
    box.operator("anime_hair_tools.create_bone_and_hook")
    box.operator("anime_hair_tools.remove_bone_and_hook")
