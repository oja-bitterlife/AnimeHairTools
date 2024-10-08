import bpy
from .CurveUtil import CreateXMirror, CurveStraighten

modules = [
    CreateXMirror,
    CurveStraighten,
]

class ANIME_HAIR_TOOLS_PT_curve_util(bpy.types.Panel):
    bl_label = "Curve Util"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "APT_HAIR_PT_UI"
    bl_idname = "APT_HAIR_PT_CURVE_UTIL"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        for i, module in enumerate(modules):
            if hasattr(module, "draw"):
                module.draw(self, context, self.layout.column())

def register():
    for module in modules:
        if hasattr(module, "register"):
            module.register()

    bpy.types.Scene.AHT_x_mirror_join = bpy.props.BoolProperty(name = "x_mirror_join", default = True)

def unregister():
    for module in modules:
        if hasattr(module, "unregister"):
            module.unregister()
