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
# Operators
##############################################################################


class HEATMAPGENERATOR_OT_run(bpy.types.Operator):
    """For every vertex, calculate its lowest distance to the camera over time"""

    bl_idname = "heat_map_generator.run"
    bl_label = "Calculate Distances"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return functions.generator_can_run()

    def execute(self, context):
        functions.calculate_distances()
        return {'FINISHED'}


class HEATMAPGENERATOR_OT_paint(bpy.types.Operator):
    """Normalize vertex distances and store them in a vertex group"""

    bl_idname = "heat_map_generator.paint"
    bl_label = "Paint Vertex Weights"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return functions.painter_can_run()

    def execute(self, context):
        functions.paint_vertex_weights()
        return {'FINISHED'}


##############################################################################
# Registration
##############################################################################


register, unregister = bpy.utils.register_classes_factory([
    HEATMAPGENERATOR_OT_run,
    HEATMAPGENERATOR_OT_paint
])
