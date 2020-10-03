import bpy


# =================================================================================================
class ANIME_HAIR_TOOLS_OT_setup_armature(bpy.types.Operator):
    bl_idname = "anime_hair_tools.setup_armature"
    bl_label = "Setup Armature and BoneRoot"

    # execute ok
    def execute(self, context):
        # no active object
        if bpy.context.view_layer.objects.active == None:
            return{'FINISHED'}

def ui_draw(context, layout):
    layout.label(text="Armature and Bone Setting:")
    layout.prop(context.scene, "armature_name", text="Armature")
    layout.prop(context.scene, "root_bone_name", text="BoneRoot")
    layout.operator("anime_hair_tools.setup_armature")


# =================================================================================================
def register():
    bpy.types.Scene.armature_name = bpy.props.StringProperty(name = "armature name", default="AHT_Armature")
    bpy.types.Scene.bone_root_name = bpy.props.StringProperty(name = "bone root name", default="AHT_BoneRoot")
