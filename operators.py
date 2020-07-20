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
    """Measure vertex distances, retaining lowest values over time"""

    bl_idname = "heat_map_generator.run"
    bl_label = "Measure"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ob_is_local_mesh = functions.active_object_is_local_mesh()
        scene_has_camera = functions.scene_has_active_camera()
        return ob_is_local_mesh and scene_has_camera

    def execute(self, context):
        functions.calculate_distances()
        return {'FINISHED'}


class HEATMAPGENERATOR_OT_paint(bpy.types.Operator):
    """Normalise sampled distances and store them in the active Vertex Group"""

    bl_idname = "heat_map_generator.paint"
    bl_label = "Paint"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ob_is_local_mesh = functions.active_object_is_local_mesh()
        have_distances = functions.distance_dict_is_not_empty()
        active_vertex_group = functions.active_vertex_group()
        return ob_is_local_mesh and have_distances and active_vertex_group

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
