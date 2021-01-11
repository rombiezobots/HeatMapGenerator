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
# Panels
##############################################################################


class PROPERTIES_PT_heat_map_generator(bpy.types.Panel):

    bl_label = 'Heat Map Generator'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_parent_id = 'DATA_PT_vertex_groups'
    bl_context = 'data'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        lay = self.layout
        lay.use_property_split = True
        lay.use_property_decorate = False
        row = lay.row(align=True)
        row.scale_y = 1.5
        row.operator('heat_map_generator.run', icon='OUTLINER_OB_CAMERA')
        row.operator('heat_map_generator.paint', icon='BRUSHES_ALL')
        settings = context.scene.heat_map_generator_settings
        lay.separator()
        col_paint = lay.column()
        col_paint.prop(settings, 'use_tresholds')
        col_paint.enabled = functions.distance_dict_is_not_empty()
        sub_tresholds = col_paint.column(align=True)
        sub_tresholds.enabled = settings.use_tresholds
        sub_tresholds.prop(settings, 'weight_low_bound')
        sub_tresholds.prop(settings, 'weight_high_bound')
        lay.separator()
        if not functions.active_object_is_local_mesh():
            lay.label(text='Active object is not a local mesh.', icon='ERROR')
        elif not functions.scene_has_active_camera():
            lay.label(text='Scene has no active Camera.', icon='ERROR')
        elif not functions.distance_dict_is_not_empty():
            lay.label(text='Measure vertex distances first.', icon='ERROR')
        elif not functions.active_vertex_group():
            lay.label(text='There is no active Vertex Group.', icon='ERROR')


##############################################################################
# Registration
##############################################################################


register, unregister = bpy.utils.register_classes_factory([
    PROPERTIES_PT_heat_map_generator
])
