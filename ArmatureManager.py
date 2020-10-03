import bpy


# =================================================================================================
class ANIME_HAIR_TOOLS_OT_setup_armature(bpy.types.Operator):
    bl_idname = "anime_hair_tools.setup_armature"
    bl_label = "Setup Armature and RootBone"

    # コンストレイントにつける名前
    CONSTRAINT_TRANSFORM_NAME = "AHT_transform"
    CONSTRAINT_ROTATION_NAME = "AHT_rotation"

    # execute
    def execute(self, context):
        scene = context.scene
        # armature
        # -------------------------------------------------------------------------
        # ない時だけ新たに作る
        if scene.AHT_armature_name not in bpy.data.objects.keys():
            self.create_armature(context)
        armature = bpy.data.objects[scene.AHT_armature_name]

        # root_bone
        # -------------------------------------------------------------------------
        armature.data.bones[0].name = scene.AHT_root_bone_name

        # constraint target
        # -------------------------------------------------------------------------
        for constraint in armature.constraints:
            if constraint.name == self.CONSTRAINT_TRANSFORM_NAME or constraint.name == self.CONSTRAINT_ROTATION_NAME:
                # Armature未設定
                if scene.AHT_constraint_target_name.armature == "_empty_for_delete":
                    # Armatureの削除
                    constraint.target = None
                else:
                    # Armatureの設定
                    target_armature = bpy.data.objects[scene.AHT_constraint_target_name.armature]
                    constraint.target = target_armature

                    # boneの設定
                    constraint.subtarget = scene.AHT_constraint_target_name.bone

        return{'FINISHED'}

    # find/create bone root for anime hair tools
    def create_armature(self, context):
        scene = context.scene

        # create new bone
        # -------------------------------------------------------------------------
        bpy.ops.object.armature_add(enter_editmode=False, location=(0, 0, 0))
        armature = bpy.context.active_object

        # set name
        armature.name = scene.AHT_armature_name
        armature.data.name = scene.AHT_armature_name

        # other setup
        armature.show_in_front = True
        armature.data.display_type = 'WIRE'

        # add constraint root_bone (after setting Target to face bone)
        constraint = armature.constraints.new('COPY_LOCATION')
        constraint.name = self.CONSTRAINT_TRANSFORM_NAME
        constraint = armature.constraints.new('COPY_ROTATION')
        constraint.name = self.CONSTRAINT_ROTATION_NAME

        # set transform
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='EDIT')
        armature.data.edit_bones[0].select = True
        armature.data.edit_bones[0].tail = (0, 0, -1)
        bpy.ops.object.mode_set(mode='OBJECT')


def ui_draw(context, layout):
    layout.label(text="Armature and Bone Setting:")
    box = layout.box()

    # ATHのArmatureの設定
    box.prop(context.scene, "AHT_armature_name", text="Armature")
    box.prop(context.scene, "AHT_root_bone_name", text="RootBone")

    # コンストレイント先設定
    box.label(text="Constraint Target:")
    box.prop(context.scene.AHT_constraint_target_name, "armature", text="Armature")
    box.prop(context.scene.AHT_constraint_target_name, "bone", text="Bone")

    # 実行
    box.operator("anime_hair_tools.setup_armature")


# コンストレイント先リストデータ
# =================================================================================================
# コンストレイント先のArmatureの候補
def get_armature_list(self, context):
    armature_list = [(obj.name, obj.name, "") for obj in context.scene.objects if obj.type == "ARMATURE" and obj.name != context.scene.AHT_armature_name]
    armature_list.insert(0, ("_empty_for_delete", "", ""))  # 空も設定できるように
    return armature_list

# コンストレイント先のBoneの候補
def get_bone_list(self, context):
    scene = context.scene

    # armature未設定
    if scene.AHT_constraint_target_name.armature == "_empty_for_delete":
        return []

    # 選択されているarmatureのboneをリストする
    armature = bpy.data.objects[context.scene.AHT_constraint_target_name.armature]
    return [(bone.name, bone.name, "") for bone in armature.data.bones]

# コンストレイント先データ
class ConstraintTargetProperty(bpy.types.PropertyGroup):
    armature: bpy.props.EnumProperty(items=get_armature_list)
    bone: bpy.props.EnumProperty(items=get_bone_list)


# =================================================================================================
def register():
    bpy.types.Scene.AHT_armature_name = bpy.props.StringProperty(name = "armature name", default="AHT_Armature")
    bpy.types.Scene.AHT_root_bone_name = bpy.props.StringProperty(name = "bone root name", default="AHT_RootBone")

#    bpy.types.Scene.constraint_target_name = bpy.props.EnumProperty(items=get_armature_list)
    bpy.types.Scene.AHT_constraint_target_name = bpy.props.PointerProperty(type=ConstraintTargetProperty)
