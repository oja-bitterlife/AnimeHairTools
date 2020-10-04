
import bpy

from . import CurveInfo, HookManager

# create bones with armature
# -------------------------------------------------------------------------------------------
class ChildBone:
    HOOK_BONE_PREFIX = "AHT_HookBone"
    HOOK_BONE_SEPALATER = "@"

    @classmethod
    def make_bone_basename(cls, base_name):
        return cls.HOOK_BONE_PREFIX + "." + base_name

    @classmethod
    def make_bone_name(cls, base_name, spline_no, point_no):
        return cls.make_bone_basename(base_name) + cls.HOOK_BONE_SEPALATER + "{}.{:0=3}".format(spline_no, point_no)

    @classmethod
    def create(cls, context, selected_curve_objs):
        armature = bpy.data.objects[context.scene.AHT_armature_name]
        bpy.context.view_layer.objects.active = armature

        # to edit-mode
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='EDIT')

        # Curveごとに回す
        for curve_obj in selected_curve_objs:
            cls._create_curve_bones(context, armature, curve_obj)  # Curve１本１本処理する

        # OBJECTモードに戻すのを忘れないように
        bpy.ops.object.mode_set(mode='OBJECT')

    # create bone for selected curves
    @classmethod
    def _create_curve_bones(cls, context, armature, curve_obj):
        # create bone chain
        # -------------------------------------------------------------------------
        root_matrix = armature.matrix_world.inverted() @ curve_obj.matrix_world

        # spline単位で処理
        for spline_no, spline in enumerate(curve_obj.data.splines):
            # 頂点ごとにボーンを作成する
            parent = armature.data.edit_bones[context.scene.AHT_root_bone_name]  # 最初はRootBoneが親
            for i in range(len(spline.points)-1):
                # Bone生成
                bone_name = cls.make_bone_name(curve_obj.name, spline_no, i)
                bpy.ops.armature.bone_primitive_add(name=bone_name)
                new_bone = armature.data.edit_bones[bone_name]

                # Bone設定
                new_bone.parent = parent  # 親子設定

                new_bone.use_connect = i != 0  # チェインの開始位置をrootとは接続しない

                # ボーンをCurveに合わせて配置
                bgn = root_matrix @ spline.points[i].co
                end = root_matrix @ spline.points[i+1].co
                if i == 0:
                    new_bone.head = bgn.xyz  # disconnected head setup
                new_bone.tail = end.xyz

                # 自分を親にして次をつなげていく
                parent = new_bone

    @classmethod
    def remove(cls, context, selected_curve_objs):
        armature = bpy.data.objects[context.scene.AHT_armature_name]
        bpy.context.view_layer.objects.active = armature

        # to edit-mode
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='EDIT')

        # 一旦全部選択解除
        bpy.ops.armature.select_all(action='DESELECT')

        # 消すべきBoneを選択
        for curve_obj in selected_curve_objs:
            bone_basename = cls.make_bone_basename(curve_obj.name) + cls.HOOK_BONE_SEPALATER
            for bone in armature.data.edit_bones:
                bone.select = bone.name.startswith(bone_basename)

        # 一括削除
        bpy.ops.armature.delete()

        # OBJECTモードに戻すのを忘れないように
        bpy.ops.object.mode_set(mode='OBJECT')


# create constraints and controll bone
# -------------------------------------------------------------------------------------------
class ANIME_HAIR_TOOLS_OT_create_bone_and_hook(bpy.types.Operator):
    bl_idname = "anime_hair_tools.create_bone_and_hook"
    bl_label = "Create ChildBone and Hook"

    # execute ok
    def execute(self, context):
        selected_curve_objs = CurveInfo.get_selected_objects(context)
        # Curveが１つも選択されていなかった
        if len(selected_curve_objs) == 0:
            return{'FINISHED'}

        # 一旦今までのものを削除
        HookManager.HookManager.remove(context, selected_curve_objs)  # Hookを削除
        ChildBone.remove(context, selected_curve_objs)  # ボーンを削除

        # 作り直す
        # ---------------------------------------------------------------------
        # create bones
        ChildBone.create(context, selected_curve_objs)

        # create hook
        HookManager.HookManager.create(context, selected_curve_objs)

        return{'FINISHED'}

    # ATH_Armatureを先に作る必要がある
    @classmethod
    def poll(cls, context):
        return bpy.data.objects.get(context.scene.AHT_armature_name) != None


# Delete the constraints added for management
# *******************************************************************************************
class ANIME_HAIR_TOOLS_OT_remove_bone_and_hook(bpy.types.Operator):
    bl_idname = "anime_hair_tools.remove_bone_and_hook"
    bl_label = "Remove ChildBone and Hook"

    # execute ok
    def execute(self, context):
        selected_curve_objs = CurveInfo.get_selected_objects(context)
        # Curveが１つも選択されていなかった
        if len(selected_curve_objs) == 0:
            return{'FINISHED'}

        # remove modifiers
        HookManager.HookManager.remove(context, selected_curve_objs)  # Hookを削除

        # remove child bones
        if bpy.data.objects.get(context.scene.AHT_armature_name) != None:  # ATHのArmatureがあるときだけBoneを消せる
            ChildBone.remove(context, selected_curve_objs)  # ボーンを削除

        return{'FINISHED'}


# UI描画設定
# =================================================================================================
def ui_draw(context, layout):
    layout.label(text="Bone and Hook Setting:")

    box = layout.box()

    # 実行
    box.operator("anime_hair_tools.create_bone_and_hook")
    box.operator("anime_hair_tools.remove_bone_and_hook")


# =================================================================================================
def register():
    pass
