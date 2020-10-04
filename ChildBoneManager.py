
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
            # 一旦今までのボーンを削除
            bpy.ops.armature.select_all(action='DESELECT')
            for bone in armature.data.edit_bones:
                bone.select = bone.name.startswith(cls.HOOK_BONE_PREFIX + "." + curve_obj.name + "_")
            bpy.ops.armature.delete()

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
            parent = None  # hair root is free
            for i in range(len(spline.points)-1):
                # Bone生成
                bone_name = cls.HOOK_BONE_PREFIX + "." + curve_obj.name + "@{}.{:0=3}".format(spline_no, i)
                bpy.ops.armature.bone_primitive_add(name=bone_name)
                new_bone = armature.data.edit_bones[bone_name]

                # Bone設定
                new_bone.parent = parent

                new_bone.use_connect = i != 0  # not connect to root

                bgn = root_matrix @ spline.points[i].co
                end = root_matrix @ spline.points[i+1].co
                if i == 0:
                    new_bone.head = bgn.xyz  # disconnected head setup
                new_bone.tail = end.xyz

                # 自分を親にして次をつなげていく
                parent = new_bone



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
        ChildBone.create(context, selected_curve_objs)

        # create hook
#        ANIME_HAIR_TOOLS_create_hook(selected_curves).execute(context)

        # create constraint
#        ANIME_HAIR_TOOLS_create_constraint(selected_curves).execute(context)

        # restore active object
#        bpy.ops.object.select_all(action='DESELECT')

        return{'FINISHED'}

    # use dialog
#    def invoke(self, context, event):
#        return context.window_manager.invoke_props_dialog(self)


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
