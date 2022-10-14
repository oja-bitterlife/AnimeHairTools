import bpy


# 更新関数
# =================================================================================================
# ペアレント先のArmatureの候補
def get_armature_list(self, context):
    armature_list = [(obj.name, obj.name, "") for obj in context.scene.objects if obj.type == "ARMATURE" and obj.name != context.scene.AHT_armature_name]
    armature_list.insert(0, ("_empty_for_delete", "", ""))  # 空も設定できるように
    return armature_list

# ペアレント先のBoneの候補
def get_bone_list(self, context):
    scene = context.scene

    # armature未設定
    if scene.AHT_parent_target_name.armature == "_empty_for_delete":
        return []

    # 選択されているarmatureのboneをリストする
    armature = bpy.data.objects[context.scene.AHT_parent_target_name.armature]
    return [(bone.name, bone.name, "") for bone in armature.data.bones if bone.use_deform]


# ペアレント設定用データ
# =================================================================================================
class ListupProperty(bpy.types.PropertyGroup):
    armature: bpy.props.EnumProperty(items=get_armature_list)
    bone: bpy.props.EnumProperty(items=get_bone_list)
