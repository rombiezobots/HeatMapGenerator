###############################################################################
# Imports
###############################################################################


import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


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

    def visible_face_from_vertex(vertex: bpy.types.MeshVertex) -> bpy.types.MeshPolygon:
        """Convert the vertex's coordinates into camera space, and check
        whether its coordinates are within the frustum. Then cast a ray at it
        to see whether it's occluded."""
        scene = bpy.context.scene
        cam = scene.camera
        ob = bpy.context.object
        cc = world_to_camera_view(scene,
                                  cam,
                                  ob.matrix_world @ vertex.co)
        cs = cam.data.clip_start
        ce = cam.data.clip_end
        # If the vertex's screen coordinates are within camera view
        if 0.0 < cc.x < 1.0 and 0.0 < cc.y < 1.0 and cs < cc.z < ce:
            # Convert the screen coordinates to a 3D vector
            frame = cam.data.view_frame(scene=scene)
            top_left = frame[3]
            pixel_vector = Vector((cc.x, cc.y, top_left[2]))
            pixel_vector.rotate(cam.matrix_world.to_quaternion())
            # Convert to target object space
            origin = ob.matrix_world.inverted() @ (pixel_vector + cam.matrix_world.translation)
            # The ray's destination is the original vertex, in object space
            destination = ob.matrix_world.inverted() @ vertex.co
            direction = (destination - origin).normalized()
            # Cast a ray from those screen coordinates to the vertex
            result, location, normal, index = ob.ray_cast(origin, direction)
            if result and index > -1:
                # Return the face the vertex belongs to
                return ob.data.polygons[index]
        return False

    def distance_to_camera(vertex: bpy.types.MeshVertex) -> float:
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
    # Determine frame settings
    start_frame, end_frame = frame_range()
    # Store current mode
    original_mode = bpy.context.mode
    # Report logs and start progress indicator
    log(f'Calculating vertex distances for object {ob.name}')
    log(f'Using start frame {start_frame}, end frame {end_frame}, and step {scene.frame_step}')
    wm.progress_begin(0, 100)

    # Loop over frames
    for frame in range(start_frame, end_frame + 1, scene.frame_step):
        # Set the current frame (using the method is important for Blender to
        # be aware of this)
        scene.frame_set(frame)
        # Get vertices from mesh. For each vertex, if it is visible, measure
        # its distance to the camera. If it's lower than it ever has been, or
        # hasn't been in view before, store it in the vertex_distances dict.
        for vertex in ob.data.vertices:
            visible_face = visible_face_from_vertex(vertex=vertex)
            if visible_face:
                for vertex_id in visible_face.vertices:
                    vertex = ob.data.vertices[vertex_id]
                    known_vertex = vertex_distances.get(vertex_id)
                    distance = distance_to_camera(vertex=vertex)
                    if not known_vertex or distance < known_vertex:
                        vertex_distances[vertex_id] = distance
        # Update progress
        log(f'Frame: {frame}')
        progress = int((frame - start_frame) /
                       (end_frame - start_frame + 1) * 100)
        wm.progress_update(progress)

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
        # POTENTIAL DIVIDE BY ZERO ERROR
        normalised_distance = 1 - (distance - min_dist) / (max_dist - min_dist)
        vertex_group = bpy.context.object.vertex_groups.active
        vertex_group.add(index=[index],
                         weight=normalised_distance,
                         type='REPLACE')


def log(message: str):
    print(f'[Heat Map Generator] {message}')
