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
# Operators
##############################################################################


class HEATMAPGENERATOR_OT_run(bpy.types.Operator):
    """Create vertex group on target mesh with values based on distance to camera"""

    bl_idname = "heat_map_generator.run"
    bl_label = "Run"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return functions.generator_can_run()

    def execute(self, context):
        functions.generate_heatmap()
        return {'FINISHED'}


##############################################################################
# Registration
##############################################################################


register, unregister = bpy.utils.register_classes_factory([
    HEATMAPGENERATOR_OT_run
])
