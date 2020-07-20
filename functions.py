###############################################################################
# Imports
###############################################################################


import bpy
import bmesh
from bpy_extras.object_utils import world_to_camera_view


###############################################################################
# Functions
###############################################################################


def dont_use_scene_start_end_frames():
    return not bpy.context.scene.heat_map_generator_settings.use_scene_start_end


def object_is_local_mesh(self, ob) -> bool:
    return ob.type == 'MESH' and not ob.library


def generator_can_run() -> bool:
    scene = bpy.context.scene
    settings = scene.heat_map_generator_settings
    return settings.mesh and settings.group_name and scene.camera


def generate_heatmap():
    """Create vertex group on target mesh with values based on distance to camera"""

    def vertices_from_screen(vertices: dict) -> dict:
        scene = bpy.context.scene
        clip_start = scene.camera.data.clip_start
        clip_end = scene.camera.data.clip_end
        bpy.ops.object.mode_set(mode='EDIT')
        bmesh_data = bmesh.from_edit_mesh(settings.mesh.data)
        for v in bmesh_data.verts:
            # Convert the vertex's coordinates into camera space, and check
            # whether its X and Y coordinates are within the frustum, and its
            # Z value between the clipping boundaries.
            co_ndc = world_to_camera_view(scene,
                                          scene.camera,
                                          settings.mesh.matrix_world @ v.co)
            if 0.0 < co_ndc.x < 1.0 and 0.0 < co_ndc.y < 1.0 and clip_start < co_ndc.z < clip_end:
                distance = (settings.mesh.matrix_world @ v.co -
                            scene.camera.matrix_world.translation).length
                if vertices.get(v.index):
                    if distance < vertices.get(v.index):
                        vertices[v.index] = distance
                else:
                    vertices[v.index] = distance
        return vertices

    def assign_vertex_weights(vertex_group: bpy.types.VertexGroup, vertices: dict):
        bpy.ops.object.mode_set(mode='OBJECT')
        # Calculate min and max distance
        distances = [distance for distance in vertices.values()]
        min_dist = min(distances)
        max_dist = max(distances)
        # Normalize
        for index in vertices:
            distance = vertices[index]
            normalised_distance = 1 - \
                (distance - min_dist) / (max_dist - min_dist)
            vertex_group.add(
                index=[index], weight=normalised_distance, type='REPLACE')

    scene = bpy.context.scene
    settings = scene.heat_map_generator_settings
    # Set the active object
    bpy.context.view_layer.objects.active = settings.mesh
    # Create the vertex group
    vertex_group = settings.mesh.vertex_groups.new(name=settings.group_name)
    # Create empty vertex distance dict
    vertices = {}

    # Switch to camera view
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].region_3d.view_perspective = 'CAMERA'

    # Determine frame settings
    step = 1
    start_frame = scene.frame_start
    end_frame = scene.frame_end
    if not settings.use_scene_start_end:
        start_frame = settings.start_frame
        end_frame = settings.end_frame
    if settings.use_frame_step:
        step = scene.frame_step

    # Let's go
    log(f'Generating heat map {vertex_group.name} for object {settings.mesh.name}')
    log(f'Using start frame {start_frame}, end frame {end_frame}, and step {step}')
    for i in range(start_frame, end_frame + 1, step):
        # Set the current frame (using the context is important for Blender to be aware of this)
        bpy.context.scene.frame_set(i)
        # Update vertex distance dict
        vertices = vertices_from_screen(vertices=vertices)
        # Update progress
        log(f'Progress: {int((i - start_frame) / (end_frame - start_frame) * 100)}% (frame: {i})')
    assign_vertex_weights(vertex_group=vertex_group,
                          vertices=vertices)


def log(message: str):
    print(f'[Heat Map Generator] {message}')
