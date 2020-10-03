import bpy


# =================================================================================================
class ANIME_HAIR_TOOLS_OT_setup_armature(bpy.types.Operator):
    bl_idname = "anime_hair_tools.setup_armature"
    bl_label = "Setup Armature and RootBone"

    # execute ok
    def execute(self, context):
        scene = context.scene
        # ない時だけ新たに作る
        # -------------------------------------------------------------------------
        # armature
        if scene.armature_name not in bpy.data.objects.keys():
            self.create_armature(context)

        # root_bone
        armature = bpy.data.objects[scene.armature_name]
        armature.data.bones[0].name = scene.root_bone_name

        # constraint target


        return{'FINISHED'}

    # find/create bone root for anime hair tools
    def create_armature(self, context):
        scene = context.scene

        # create new bone
        # -------------------------------------------------------------------------
        bpy.ops.object.armature_add(enter_editmode=False, location=(0, 0, 0))
        armature = bpy.context.active_object

        # set name
        armature.name = scene.armature_name
        armature.data.name = scene.armature_name

        # other setup
        armature.show_in_front = True
        armature.data.display_type = 'WIRE'

        # add constraint root_bone (after setting Target to face bone)
        constraint = armature.constraints.new('COPY_LOCATION')
        constraint.name = "AHT_transform"
        constraint = armature.constraints.new('COPY_ROTATION')
        constraint.name = "AHT_rotation"

        # set transform
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='EDIT')
        armature.data.edit_bones[0].select = True
        armature.data.edit_bones[0].tail = (0, 0, -1)
        bpy.ops.object.mode_set(mode='OBJECT')



def ui_draw(context, layout):
    layout.label(text="Armature and Bone Setting:")

    layout.prop(context.scene, "AHT_armature_name", text="Armature")
    layout.prop(context.scene, "AHT_root_bone_name", text="RootBone")

    layout.prop(context.scene.AHT_constraint_target_name, "armature", text="ConstraintTarget")

    layout.operator("anime_hair_tools.setup_armature")


def get_armature_list(self, context):
    return [(obj.name, obj.name, "") for obj in context.scene.objects if obj.type == "ARMATURE" and obj.name != context.scene.armature_name]

# コンストレイント先
class ConstraintTargetProperty(bpy.types.PropertyGroup):
    armature: bpy.props.EnumProperty(items=get_armature_list)
    bone: bpy.props.StringProperty( name="Bone" )

# =================================================================================================
def register():
    bpy.types.Scene.AHT_armature_name = bpy.props.StringProperty(name = "armature name", default="AHT_Armature")
    bpy.types.Scene.AHT_root_bone_name = bpy.props.StringProperty(name = "bone root name", default="AHT_RootBone")

#    bpy.types.Scene.constraint_target_name = bpy.props.EnumProperty(items=get_armature_list)
    bpy.types.Scene.AHT_constraint_target_name = bpy.props.PointerProperty(type=ConstraintTargetProperty)
