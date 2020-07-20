##############################################################################
# Imports
##############################################################################


if 'functions' in locals():
    import importlib
    functions = importlib.reload(functions)
else:
    from HeatMapGenerator import functions
    import bpy


##############################################################################
# Properties
##############################################################################


class Settings(bpy.types.PropertyGroup):
    use_frame_step: bpy.props.BoolProperty(name="Use Frame Step",
                                           options={'SKIP_SAVE'},
                                           default=True,
                                           description='Use the Scene\'s Frame Step')
    group_name: bpy.props.StringProperty(name='New Vertex Group',
                                         default='HeatMap',
                                         options={'SKIP_SAVE'})
    frame_range: bpy.props.EnumProperty(name='Frame Range',
                                        items=[
                                            ('output', 'Scene Output',
                                             'Use the frame range defined in the Scene\'s output settings'),
                                            ('preview', 'Timeline Preview',
                                             'Use the Preview frame range defined in the Timeline')
                                        ],
                                        options={'SKIP_SAVE'})


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
