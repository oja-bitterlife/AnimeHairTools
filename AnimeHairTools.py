import bpy

from . import ArmatureManager, SelectedEditBoneSetting
from . import MeshAndBones

# Main UI
# ===========================================================================================
# 3DView Tools Panel
class ANIME_HAIR_TOOLS_PT_ui(bpy.types.Panel):
    bl_label = "Anime Hair Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AnimeHairTools"

    def draw(self, context):
        # 状態によって使うUIを切り替える
        if context.mode == "OBJECT":
            ArmatureManager.ui_draw(context, self.layout)
            MeshAndBones.ui_draw(context, self.layout)
        if context.mode == "EDIT_ARMATURE":
            SelectedEditBoneSetting.ui_draw(context, self.layout)

