import bpy


# IK Setup
# =================================================================================================
class ANIME_HAIR_TOOLS_OT_center_of_xmirror(bpy.types.Operator):
    bl_idname = "anime_hair_tools.center_of_xmirror"
    bl_label = "Center Of XMirror"

    # execute ok
    def execute(self, context):
        # 3Dカーソルを動かして中央に
        bpy.ops.view3d.snap_cursor_to_selected()
        context.scene.cursor.location[0] = 0
        context.scene.tool_settings.transform_pivot_point = 'CURSOR'

        return {'FINISHED'}

# UI描画設定
# =================================================================================================
def ui_draw(context, layout):
    layout.label(text="3DCursor:")
    box = layout.box()
    box.operator("anime_hair_tools.center_of_xmirror")
