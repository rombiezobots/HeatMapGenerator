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
