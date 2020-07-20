##############################################################################
# Imports
##############################################################################


import bpy
from HeatMapGenerator import functions


##############################################################################
# Panels
##############################################################################


class VIEW3D_PT_heat_map_generator(bpy.types.Panel):

    bl_idname = 'VIEW3D_PT_heat_map_generator'
    bl_label = 'Heat Map Generator'
    bl_category = 'Tool'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):

        settings = context.scene.heat_map_generator_settings
        lay = self.layout
        lay.use_property_split = True
        lay.prop(settings, 'mesh')
        lay.prop(settings, 'group_name')
        lay.separator()
        col = lay.column()
        col.enabled = functions.dont_use_scene_start_end_frames()
        col.prop(settings, 'start_frame')
        col.prop(settings, 'end_frame')
        lay.prop(settings, 'use_scene_start_end')
        lay.prop(settings, 'use_frame_step')
        lay.separator()
        row = lay.row()
        row.scale_y = 1.5
        row.operator('heat_map_generator.run')


##############################################################################
# Registration
##############################################################################


register, unregister = bpy.utils.register_classes_factory([
    VIEW3D_PT_heat_map_generator
])
