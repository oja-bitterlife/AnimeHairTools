import bpy

from . import ChildBoneManager

# create hook modifiers
# -------------------------------------------------------------------------------------------
class HookManager:
    HOOK_MODIFIRE_PREFIX = "AHT_HookModifire"
    HOOK_MODIFIRE_SEPALATER = "@"

    @classmethod
    def make_modifier_basename(cls, base_name):
        return cls.HOOK_MODIFIRE_PREFIX + "." + base_name

    @classmethod
    def make_modifier_name(cls, base_name, spline_no, point_no):
        return cls.make_modifier_basename(base_name) + cls.HOOK_MODIFIRE_SEPALATER + "{}.{:0=3}".format(spline_no, point_no)

    # execute create constraints
    @classmethod
    def create(cls, context, selected_curve_objs):
        for curve in selected_curve_objs:
            # create hook modifiers
            cls.create_modifiers(context, curve)

            # assign point to modifier
#            cls.assign_points(curve)

        return{'FINISHED'}

    # create modifier every segment and sort
    @classmethod
    def create_modifiers(cls, context, curve_obj):
        armature = bpy.data.objects[context.scene.AHT_armature_name]

        # spline単位で処理
        for spline_no, spline in enumerate(curve_obj.data.splines):

            # 頂点ごとにHookを作成する
            for point_no in range(len(spline.points)-2, -1, -1):  # asc sorting
                hook_name = cls.make_modifier_name(curve_obj.name, spline_no, point_no)

                # create not exists hook modifier
                curve_obj.modifiers.new(hook_name, type="HOOK")
                new_modifier = curve_obj.modifiers[hook_name]

                # setup
                # -------------------------------------------------------------------------
                new_modifier.object = armature
#                no = point_no
#                if(len(spline.points)-1 <= no):
#                    no = len(spline.points)-2  # edge limit
                new_modifier.subtarget = ChildBoneManager.ChildBone.make_bone_name(curve_obj.name, spline_no, point_no)

                # sort modifier
                # -------------------------------------------------------------------------
#                move_up_count = curve_obj.modifiers.keys().index(new_modifier.name)

#                bpy.context.view_layer.objects.active = curve_obj  # for modifier_move_up
#                for j in range(move_up_count):
#                    bpy.ops.object.modifier_move_up(modifier=modifier.name)




    def assign_points(self, curve):
        # assign segment
        bpy.context.view_layer.objects.active = curve
        bpy.ops.object.mode_set(mode='EDIT')

        # get points in edit mode
        segment_count = len(get_curve_all_points(curve))  # bettween points

        # assign hook
        for segment_no in range(segment_count):
            # need for each assign
            hook_points = get_curve_all_points(curve)

            # select is only assign target point
            for point_no, p in enumerate(hook_points):
                p.select = segment_no == point_no
                
            # assign to modifier
            hook_name = ANIME_HAIR_TOOLS_create_hook.create_modifier_name(curve.name, segment_no)
            bpy.ops.object.hook_assign(modifier=hook_name)

        bpy.ops.object.mode_set(mode='OBJECT')


    @classmethod
    def remove(cls, context, selected_curve_objs):
        # remove
        for curve_obj in selected_curve_objs:
            # CurveオブジェクトについているすべてのATH用モディファイアを消す
            hook_basename = cls.make_modifier_basename(curve_obj.name) + cls.HOOK_MODIFIRE_SEPALATER
            for modifier in curve_obj.modifiers:
                if modifier.name.startswith(hook_basename):
                    bpy.ops.object.modifier_remove(modifier=modifier.name)

