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
    weight_low_bound: bpy.props.FloatProperty(name='Lower Treshold',
                                              subtype='DISTANCE',
                                              options={'SKIP_SAVE'},
                                              min=0.0, soft_min=0.0,
                                              precision=2,
                                              description='If higher than the sampled minimum, this replaces it as the lower limit of the vertex weights')
    weight_high_bound: bpy.props.FloatProperty(name='Upper Treshold',
                                               subtype='DISTANCE',
                                               options={'SKIP_SAVE'},
                                               precision=2,
                                               min=0.1, soft_min=0.1,
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
