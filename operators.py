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
        ob_is_local_mesh = functions.active_object_is_local_mesh()
        scene_has_camera = functions.scene_has_active_camera()
        return ob_is_local_mesh and scene_has_camera

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
        ob_is_local_mesh = functions.active_object_is_local_mesh()
        have_distances = functions.distance_dict_is_not_empty()
        vertex_group_ok = functions.vertex_group_is_writable()
        return ob_is_local_mesh and have_distances and vertex_group_ok

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
