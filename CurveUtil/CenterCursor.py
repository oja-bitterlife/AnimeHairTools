import bpy


# IK Setup
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_center_of_xmirror(bpy.types.Operator):
    bl_idname = "anime_hair_tools.center_of_xmirror"
    bl_label = "Center Of X"

    # execute ok
    def execute(self, context):
        # 3Dカーソルを動かして中央に
        bpy.ops.view3d.snap_cursor_to_selected()
        context.scene.cursor.location[0] = 0
        context.scene.tool_settings.transform_pivot_point = 'CURSOR'

        return {'FINISHED'}


# UI描画設定
# =================================================================================================
label = "3D Cursor"

classes = [
    ANIME_HAIR_TOOLS_OT_center_of_xmirror,
]

def draw(parent, context, layout):
    if context.mode != "EDIT_CURVE" and context.mode != "EDIT_MESH":
        layout.enabled = False

    box = layout.box()
    box.operator("anime_hair_tools.center_of_xmirror")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
