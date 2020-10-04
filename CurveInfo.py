import bpy

# curve functions
# ===========================================================================================
# return the selected cuve objects
def get_selected_objects(context):
    return [obj for obj in context.selected_objects if obj.type == "CURVE"]
