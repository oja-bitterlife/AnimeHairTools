
import bpy

from . import CurveInfo

# create bones with armature
# -------------------------------------------------------------------------------------------
class ChildBone:
    HOOK_BONE_PREFIX = "AHT_HookBone"

    @classmethod
    def make_bone_name(cls, base_name, no):
        return cls.HOOK_BONE_PREFIX + "." + base_name + ".{:0=3}".format(no)

    @classmethod
    def create(cls, context, selected_curve_objs):
        armature = bpy.data.objects[context.scene.AHT_armature_name]
        bpy.context.view_layer.objects.active = armature

        # to edit-mode
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='EDIT')

        # 一旦今までのボーンを削除
        bpy.ops.armature.select_all(action='DESELECT')
        for bone in armature.data.edit_bones:
            bone.select = bone.name.startswith(cls.HOOK_BONE_PREFIX + ".")
        bpy.ops.armature.delete()

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

        parent = None  # hair root is free
        for spline in curve_obj.data.splines:
            for i in range(len(spline.points)-1):
                bgn = root_matrix @ spline.points[i].co
                end = root_matrix @ spline.points[i+1].co
                parent = cls._create_child_bone(curve_obj.name, i, parent, bgn, end)


    # create chain child bone
    @classmethod
    def _create_child_bone(cls, base_name, i, parent, bgn, end):
        bone_name = cls.make_bone_name(base_name, i)

        # create bone if not exists
        # -------------------------------------------------------------------------
        bpy.ops.armature.bone_primitive_add(name=bone_name)

        # (re)setup
        # -------------------------------------------------------------------------
#        child_bone = self.root_armature.data.edit_bones[bone_name]

#        child_bone.parent = parent
#        child_bone.use_connect = i != 0  # not connect to root
#        if i == 0:
#            child_bone.head = bgn.xyz  # disconnected head setup
#        child_bone.tail = end.xyz
    
#        return child_bone
        return None


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
