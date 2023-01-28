import bpy

from . import ArmatureManager, MeshAndBones
from . import EditBoneSetup
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
    bl_category = "AnimeTools"

    def draw(self, context):
        # 状態によって使うUIを切り替える
        if context.mode == "OBJECT":
            ArmatureManager.ui_draw(context, self.layout)
            MeshAndBones.ui_draw(context, self.layout)
        if context.mode == "EDIT_ARMATURE":
            EditBoneSetup.ui_draw(context, self.layout)
        if context.mode == "POSE":
            IKSetup.ui_draw(context, self.layout)
            CopyAction.ui_draw(context, self.layout)
        if context.mode == "EDIT_CURVE":
            CurveStraighten.ui_draw(context, self.layout)
            MirrorEdit.ui_draw(context, self.layout)
        if context.mode == "EDIT_MESH":
            MirrorEdit.ui_draw(context, self.layout)
