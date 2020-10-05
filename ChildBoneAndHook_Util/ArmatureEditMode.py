import bpy


# Armatureのエディットモードに変更
def to_edit_mode(context, armature):
    # 復帰できるように状態を保存
    state_backup = {
        "armature": armature,
        "hide": armature.hide_get(),
    }

    armature.hide_set(False)  # 非表示だとEDITモードにできないので必ず表示
    context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')

    return state_backup


# オブジェクトモードに戻す
def return_obuject_mode(state_backup):
    state_backup["armature"].hide_set(state_backup["hide"])
    bpy.ops.object.mode_set(mode='OBJECT')



