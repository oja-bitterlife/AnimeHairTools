import bpy
from .EditIK import IKSetup

modules = [
    IKSetup,
]

class ANIME_HAIR_TOOLS_PT_edit_ik(bpy.types.Panel):
    bl_label = "Edit IK"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "APT_HAIR_PT_UI"
    bl_idname = "APT_HAIR_PT_EDIT_IK"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        for i, module in enumerate(modules):
            if hasattr(module, "draw"):
                if hasattr(module, "label"):
                    self.layout.label(text=module.label)
                module.draw(self, context, self.layout.box())

def register():
    for module in modules:
        if hasattr(module, "register"):
            module.register()

def unregister():
    for module in modules:
        if hasattr(module, "unregister"):
            module.unregister()
