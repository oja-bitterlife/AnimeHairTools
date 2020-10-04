
import bpy

from . import CurveInfo

# create bones with armature
# -------------------------------------------------------------------------------------------
class ChildBone:
    HOOK_BONE_PREFIX = "AHT_HookBone"

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
                bone_name = cls.HOOK_BONE_PREFIX + "." + curve_obj.name + "@{}.{:0=3}".format(spline_no, i)
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
            for bone in armature.data.edit_bones:
                bone.select = bone.name.startswith(cls.HOOK_BONE_PREFIX + "." + curve_obj.name + "@")

        # 一括削除
        bpy.ops.armature.delete()

        # OBJECTモードに戻すのを忘れないように
        bpy.ops.object.mode_set(mode='OBJECT')


class HookConstraint:
    pass


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

        # create bones
        ChildBone.remove(context, selected_curve_objs)  # 一旦今までのボーンを削除
        ChildBone.create(context, selected_curve_objs)

        # create hook
#        ANIME_HAIR_TOOLS_create_hook(selected_curves).execute(context)

        # create constraint
#        ANIME_HAIR_TOOLS_create_constraint(selected_curves).execute(context)

        return{'FINISHED'}

    # ATH_Armatureを先に作る必要がある
    @classmethod
    def poll(cls, context):
        return bpy.data.objects.get(context.scene.AHT_armature_name) != None

# Delete the constraints added for management
# *******************************************************************************************
class ANIME_HAIR_TOOLS_OT_remove_bone_and_hook(bpy.types.Operator):
    bl_idname = "anime_hair_tools.remove_bone_and_hook"
    bl_label = "Remove Child Bone and Hook"

    # execute ok
    def execute(self, context):
        selected_curve_objs = CurveInfo.get_selected_objects(context)
        # Curveが１つも選択されていなかった
        if len(selected_curve_objs) == 0:
            return{'FINISHED'}

        # remove added constraints
#        apply_each_curves(selected_curves, self.remove_constraints)

        # remove added modifiers
#        apply_each_curves(selected_curves, self.remove_modifiers)

        # remove added bones
        ChildBone.remove(context, selected_curve_objs)  # 一旦今までのボーンを削除

        return{'FINISHED'}

    # remove all constraint
    def remove_constraints(self, curve):
        c = curve.constraints["AHT_rotation"]
        curve.constraints.remove(c)

    # remove all hook modifiers
    def remove_modifiers(self, curve):
        bpy.context.view_layer.objects.active = curve

        # create remove name
        hook_name = ANIME_HAIR_TOOLS_create_hook.create_modifier_name(curve.name, 0)
        hook_name_base = hook_name[:-4]  # remove .000

        # remove
        for modifier in curve.modifiers:
            if modifier.name.startswith(hook_name_base):
                bpy.ops.object.modifier_remove(modifier=modifier.name)

    # remove all hook bones
    def remove_bones(self, curve):
        root_armature = None
        if ANIME_HAIR_TOOLS_ARMATURE_NAME in bpy.data.objects.keys():
            root_armature = bpy.data.objects[ANIME_HAIR_TOOLS_ARMATURE_NAME]

        # if not exists noting to do
        if root_armature == None:
            return

        # to edit-mode
        bpy.context.view_layer.objects.active = root_armature
        bpy.ops.object.mode_set(mode='EDIT')

        # create remove name
        bone_name = ANIME_HAIR_TOOLS_create_bone.create_bone_name(curve.name, 0)
        bone_name_base = bone_name[:-4]  # remove .000

        # select remove target bones
        bpy.ops.armature.select_all(action='DESELECT')
        for edit_bone in root_armature.data.edit_bones:
            if edit_bone.name.startswith(bone_name_base):
                edit_bone.select = True

        # remove selected bones
        bpy.ops.armature.delete()

        # out of edit-mode
        bpy.ops.object.mode_set(mode='OBJECT')

    # ATH_Armatureを先に作る必要がある
    @classmethod
    def poll(cls, context):
        return bpy.data.objects.get(context.scene.AHT_armature_name) != None


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
