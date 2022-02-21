import bpy

from . import ArmatureManager
from . import MeshAndBones
from . import RollManager

# Main UI
# ===========================================================================================
# 3DView Tools Panel
class ANIME_HAIR_TOOLS_PT_ui(bpy.types.Panel):
    bl_label = "Anime Hair Tools (for Curve)"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AnimeHairTools"

    def draw(self, context):
        ArmatureManager.ui_draw(context, self.layout)
        MeshAndBones.ui_draw(context, self.layout)
        RollManager.ui_draw(context, self.layout)

    # オブジェクトモード時のみ利用可能に
    @classmethod
    def poll(cls, context):
        return (context.mode == "OBJECT")
