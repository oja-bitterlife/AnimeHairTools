import bpy

# curve functions
# ===========================================================================================
# return the selected cuve objects
def get_all():
    return [obj for obj in bpy.context.selected_objects if obj.type == "CURVE"]
