
import bpy


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
