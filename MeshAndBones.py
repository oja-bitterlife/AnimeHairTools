import bpy, sys

from .Util import BoneManager, MeshManager


# create constraints and controll bone
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_create(bpy.types.Operator):
    bl_idname = "anime_hair_tools.create"
    bl_label = "Create Mesh & Bones"

    # execute ok
    def execute(self, context):
        selected_curve_objs = [obj for obj in context.selected_objects if obj.type == "CURVE"]

        # Curveが１つも選択されていなかった
        if len(selected_curve_objs) == 0:
            return{'FINISHED'}

        # 一旦今までのものを削除
        # ---------------------------------------------------------------------
        BoneManager.remove(context, selected_curve_objs)  # Boneを削除
        MeshManager.remove(context, selected_curve_objs)  # Meshも削除

        # 作り直す
        # ---------------------------------------------------------------------
        # create bones
        BoneManager.create(context, selected_curve_objs)

        # create mesh
        MeshManager.create(context, selected_curve_objs)

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
    box.prop(context.scene, "AHT_bbone", text="BendyBones")
    box.operator("anime_hair_tools.create")
    box.operator("anime_hair_tools.remove")


# =================================================================================================
def register():
    # Bone設定
    bpy.types.Scene.AHT_bbone = bpy.props.IntProperty(name = "BendyBone split", default=4)
    # モディファイア設定
    bpy.types.Scene.AHT_subdivision = bpy.props.BoolProperty(name = "With Subdivision", default=True)
