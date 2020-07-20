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


def active_object_is_local_mesh() -> bool:
    active_ob = bpy.context.object
    return active_ob and active_ob.type == 'MESH' and not active_ob.library


def scene_has_active_camera() -> bool:
    return bpy.context.scene.camera != None


def distance_dict_is_not_empty() -> bool:
    return len(vertex_distances) > 0


def active_vertex_group() -> bool:
    active_ob = bpy.context.object
    return active_ob.vertex_groups and active_ob.vertex_groups.active


def update_tresholds(self, context) -> None:
    distances = vertex_distances.values()
    settings = bpy.context.scene.heat_map_generator_settings
    settings.weight_low_bound = min(distances)
    settings.weight_high_bound = max(distances)
    return None


def calculate_distances():
    """Measure vertex distances, retaining lowest values over time"""

    # bpy.context.mode returns different values than
    # bpy.ops.object.mode_set(mode) accepts.
    context_mode_remap = {
        'EDIT_MESH': 'EDIT',
        'PAINT_WEIGHT': 'WEIGHT_PAINT',
        'PAINT_VERTEX': 'VERTEX_PAINT',
        'PAINT_TEXTURE': 'TEXTURE_PAINT'
    }

    def frame_range() -> tuple:
        """Return the frame range based on whether we want the Scene settings or the Preview ones."""
        scene = bpy.context.scene
        if scene.use_preview_range:
            return scene.frame_preview_start, scene.frame_preview_end
        return scene.frame_start, scene.frame_end

    def vertex_is_visible(vertex: bmesh.types.BMVert) -> bool:
        """Convert the vertex's coordinates into camera space, and check
        whether its X and Y coordinates are within the frustum, and its
        Z value between the clipping boundaries."""
        scene = bpy.context.scene
        cam = scene.camera
        ob = bpy.context.object
        cs = scene.camera.data.clip_start
        ce = scene.camera.data.clip_end
        cc = world_to_camera_view(scene,
                                  cam,
                                  ob.matrix_world @ v.co)
        return 0.0 < cc.x < 1.0 and 0.0 < cc.y < 1.0 and cs < cc.z < ce

    def distance_to_camera(vertex: bmesh.types.BMVert) -> float:
        """Calculate the vertex's distance to the camera."""
        cam = bpy.context.scene.camera
        ob = bpy.context.object
        return (ob.matrix_world @ vertex.co -
                cam.matrix_world.translation).length

    scene = bpy.context.scene
    ob = bpy.context.object
    wm = bpy.context.window_manager

    # Clear the vertex distance dict
    vertex_distances.clear()
    # Switch to camera view
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].region_3d.view_perspective = 'CAMERA'
    # Determine frame settings
    start_frame, end_frame = frame_range()
    # Store current mode
    original_mode = bpy.context.mode
    # Report logs and start progress indicator
    log(f'Calculating vertex distances for object {ob.name}')
    log(f'Using start frame {start_frame}, end frame {end_frame}, and step {scene.frame_step}')
    wm.progress_begin(0, 100)

    # Create BMesh
    bpy.ops.object.mode_set(mode='EDIT')
    bmesh_data = bmesh.from_edit_mesh(ob.data)
    # Loop over frames
    for i in range(start_frame, end_frame + 1, scene.frame_step):
        # Set the current frame (using the method is important
        # for Blender to be aware of this)
        scene.frame_set(i)
        # Get vertices from mesh
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
        wm.progress_update(progress)

    # Clean up the bmesh to lower memory impact
    bmesh_data.free()
    # End progress indicator
    wm.progress_end()
    # Go back to previous mode
    if context_mode_remap.get(original_mode):
        original_mode = context_mode_remap[original_mode]
    bpy.ops.object.mode_set(mode=original_mode)
    # Set tresholds
    settings = bpy.context.scene.heat_map_generator_settings
    settings.weight_low_bound = min(vertex_distances.values())
    settings.weight_high_bound = max(vertex_distances.values())


def paint_vertex_weights():
    """Normalise sampled distances and store them in the active Vertex Group"""
    settings = bpy.context.scene.heat_map_generator_settings
    # Go into Weight Paint mode so we can see the result
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    # Determine min and max distance
    distances = vertex_distances.values()
    min_dist = min(distances)
    max_dist = max(distances)
    if settings.use_tresholds:
        min_dist = max(settings.weight_low_bound, min_dist)
        max_dist = min(settings.weight_high_bound, max_dist)
    # Normalize
    for index in vertex_distances:
        distance = vertex_distances[index]
        normalised_distance = 1 - (distance - min_dist) / (max_dist - min_dist)
        vertex_group = bpy.context.object.vertex_groups.active
        vertex_group.add(index=[index],
                         weight=normalised_distance,
                         type='REPLACE')


def log(message: str):
    print(f'[Heat Map Generator] {message}')
