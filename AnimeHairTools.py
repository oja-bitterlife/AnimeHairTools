import bpy

from . import ArmatureManager
from . import EditBoneSetting
from . import IKSetup, CopyAction
from . import CurveStraighten
from . import MirrorEdit

# Main UI
# ===========================================================================================
# 3DView Tools Panel
class ANIME_HAIR_TOOLS_PT_ui(bpy.types.Panel):
    bl_label = "Anime Hair Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Animation"
    bl_idname = "APT_HAIR_PT_UI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        # 状態によって使うUIを切り替える
        if context.mode == "EDIT_CURVE":
            MirrorEdit.ui_draw(context, self.layout)
            CurveStraighten.ui_draw(context, self.layout)
        if context.mode == "EDIT_MESH":
            MirrorEdit.ui_draw(context, self.layout)
