###############################################################################
# Imports
###############################################################################


import bpy
import bmesh
from bpy_extras.object_utils import world_to_camera_view


###############################################################################
# Local variables
###############################################################################


vertex_distances = {}


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


def painter_can_run() -> bool:
    scene = bpy.context.scene
    settings = scene.heat_map_generator_settings
    # Need to check for distance dict and existing vertex group
    return settings.mesh != None


def calculate_distances():
    """Create vertex group on target mesh with values based on distance to camera"""

    def vertex_is_visible(vertex: bmesh.types.BMVert) -> bool:
        """Convert the vertex's coordinates into camera space, and check
        whether its X and Y coordinates are within the frustum, and its
        Z value between the clipping boundaries."""
        scene = bpy.context.scene
        settings = scene.heat_map_generator_settings
        cs = scene.camera.data.clip_start
        ce = scene.camera.data.clip_end
        cc = world_to_camera_view(scene,
                                  scene.camera,
                                  settings.mesh.matrix_world @ v.co)
        return 0.0 < cc.x < 1.0 and 0.0 < cc.y < 1.0 and cs < cc.z < ce

    def distance_to_camera(vertex: bmesh.types.BMVert) -> float:
        """Calculate the vertex's distance to the camera."""
        scene = bpy.context.scene
        settings = scene.heat_map_generator_settings
        return (settings.mesh.matrix_world @ vertex.co -
                scene.camera.matrix_world.translation).length

    scene = bpy.context.scene
    settings = scene.heat_map_generator_settings
    # Set the active object
    bpy.context.view_layer.objects.active = settings.mesh

    # Clear the vertex distance dict
    vertex_distances.clear()
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
    # Report logs and start progress indicator
    log(f'Calculating vertex distances for object {settings.mesh.name}')
    log(f'Using start frame {start_frame}, end frame {end_frame}, and step {step}')
    bpy.context.window_manager.progress_begin(0, 100)

    for i in range(start_frame, end_frame + 1, step):
        # Set the current frame (using the context is important
        # for Blender to be aware of this)
        bpy.context.scene.frame_set(i)
        # Get vertices from mesh
        bpy.ops.object.mode_set(mode='EDIT')
        bmesh_data = bmesh.from_edit_mesh(settings.mesh.data)
        for v in bmesh_data.verts:
            if vertex_is_visible(vertex=v):
                distance = distance_to_camera(vertex=v)
                if vertex_distances.get(v.index):
                    if distance < vertex_distances.get(v.index):
                        vertex_distances[v.index] = distance
                else:
                    vertex_distances[v.index] = distance
        # Update progress
        log(f'Frame: {i}')
        progress = int((i - start_frame) / (end_frame - start_frame) * 100)
        bpy.context.window_manager.progress_update(progress)
    # End progress indicator
    bpy.context.window_manager.progress_end()
    # Switch to Object Mode
    bpy.ops.object.mode_set(mode='OBJECT')


def paint_vertex_weights():
    scene = bpy.context.scene
    settings = scene.heat_map_generator_settings
    # Create the vertex group
    vertex_group = settings.mesh.vertex_groups.new(name=settings.group_name)
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    # Calculate min and max distance
    distances = [distance for distance in vertex_distances.values()]
    min_dist = min(distances)
    max_dist = max(distances)
    # Normalize
    for index in vertex_distances:
        distance = vertex_distances[index]
        normalised_distance = 1 - (distance - min_dist) / (max_dist - min_dist)
        vertex_group.add(
            index=[index], weight=normalised_distance, type='REPLACE')


def log(message: str):
    print(f'[Heat Map Generator] {message}')
