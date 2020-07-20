##############################################################################
# Imports
##############################################################################


if 'functions' in locals():
    import importlib
    functions = importlib.reload(functions)
else:
    import HeatMapGenerator.functions
    import bpy


##############################################################################
# Properties
##############################################################################


class Settings(bpy.types.PropertyGroup):

    mesh: bpy.props.PointerProperty(type=bpy.types.Object,
                                    options={'SKIP_SAVE'},
                                    name="Target Mesh",
                                    poll=functions.object_is_local_mesh)
    use_frame_step: bpy.props.BoolProperty(name="Use Frame Step",
                                           options={'SKIP_SAVE'},
                                           default=True,
                                           description='Use the Scene\'s Frame Step')
    group_name: bpy.props.StringProperty(name='New Vertex Group',
                                         default='HeatMap',
                                         options={'SKIP_SAVE'})
    start_frame: bpy.props.IntProperty(name='Start frame',
                                       default=bpy.context.scene.frame_start,
                                       options={'SKIP_SAVE'})
    end_frame: bpy.props.IntProperty(name='End frame',
                                     default=bpy.context.scene.frame_end,
                                     options={'SKIP_SAVE'})
    use_scene_start_end: bpy.props.BoolProperty(name="Use Scene Values",
                                                options={'SKIP_SAVE'},
                                                default=True,
                                                description='Use the Scene\'s start and end frame')


##############################################################################
# Registration
##############################################################################


def register():
    bpy.utils.register_class(Settings)
    bpy.types.Scene.heat_map_generator_settings = bpy.props.PointerProperty(
        type=Settings)


def unregister():
    bpy.utils.unregister_class(Settings)
    try:
        del bpy.types.Scene.heat_map_generator_settings
    except:
        pass
