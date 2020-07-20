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
    use_tresholds: bpy.props.BoolProperty(name='Use Tresholds',
                                          options={'SKIP_SAVE'},
                                          update=functions.update_tresholds,
                                          description='Use custom distance tresholds instead of the sampled extremes')
    weight_low_bound: bpy.props.FloatProperty(name='Low Treshold',
                                              subtype='DISTANCE',
                                              options={'SKIP_SAVE'},
                                              description='If higher than the sampled minimum, this replaces it as the lower limit of the vertex weights')
    weight_high_bound: bpy.props.FloatProperty(name='High Treshold',
                                               subtype='DISTANCE',
                                               options={'SKIP_SAVE'},
                                               description='If lower than the sampled maximum, this replaces it as the higher limit of the vertex weights')


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
