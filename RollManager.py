import bpy
import math

from .Util.ListupUtil import ListupProperty


# AHT用のArmatureのセットアップを行う
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_setup_bone_roll(bpy.types.Operator):
    bl_idname = "anime_hair_tools.setup_bone_roll"
    bl_label = "Setup Bone Roll"

    # execute
    def execute(self, context):

        # 頂点の回収(法線とペアで)
        mesh = bpy.data.objects[context.scene.AHT_roll_reference.roll_reference].data
        points = []
        normals = []
        for v in mesh.vertices:
            points.append(v.co)
            normals.append(v.normal)

        # 編集対象ボーンの回収
        armature = bpy.context.active_object
        selected_bones = []
        for bone in armature.data.edit_bones:
            if bone.select:
                selected_bones.append(bone)

        # 最近点を探る
        for bone in selected_bones:
            index = self.get_nearest_point(armature.matrix_world @ bone.head, points)
            if index >= 0:
                # 最近点の法線をボーンのXZ軸上にプロット
                xprot = normals[index].dot(bone.x_axis)
                zprot = normals[index].dot(bone.z_axis)
                v = bone.x_axis * xprot + bone.z_axis * zprot
                v.normalize()

                # 角度計算
                cs = math.max(1, math.min(-1, v.dot(bone.z_axis)))
                rad = math.acos(cs)  # 角度差分(CW/CCWはわからない)
                dir = v.cross(bone.z_axis).dot(bone.y_axis)  # 3重積で方向
                if dir > 0:
                    rad = -rad
                bone.roll += rad

        return{'FINISHED'}

    # 最近点のインデックスを返す。最近点を見つけきらなければ-1を返す
    def get_nearest_point(self, bone_pos, points):
        min_index = -1
        min_pos = math.inf
        for i, p in enumerate(points):
            if min_pos > (p - bone_pos).length:
                min_pos = (p - bone_pos).length
                min_index = i

        return min_index



# UI描画設定
# =================================================================================================
def ui_draw(context, layout):
    layout.label(text="Bone Roll Setting:")
    box = layout.box()

    # Roll参照先設定
    box.prop(context.scene.AHT_roll_reference, "roll_reference", text="Roll Reference Object")

    # 実行
    box.operator("anime_hair_tools.setup_bone_roll")


# =================================================================================================
def register():
    # Bone設定
    bpy.types.Scene.AHT_roll_reference = bpy.props.PointerProperty(type=ListupProperty)
