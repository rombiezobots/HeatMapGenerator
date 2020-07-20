###############################################################################
#                              HEAT MAP GENERATOR                             #
#                 Distance to camera stored in vertex groups                  #
###############################################################################


###############################################################################
# Imports
###############################################################################


if 'properties' in locals():
    import importlib
    properties = importlib.reload(properties)
    operators = importlib.reload(operators)
    panels = importlib.reload(panels)
else:
    from HeatMapGenerator import properties, operators, panels


###############################################################################
# Add-on information
###############################################################################


bl_info = {
    'name': 'Heat Map Generator',
    'description': 'Distance to camera stored in vertex groups',
    'author': 'Sam Van Hulle',
    'version': (1, 0, 0),
    'blender': (2, 83, 0),
    'location': 'Properties > Mesh Data > Vertex Groups',
    'category': 'Paint'
}


###############################################################################
# Registration
###############################################################################


modules = [
    properties,
    operators,
    panels
]


def register():
    for mod in modules:
        mod.register()


def unregister():
    for mod in modules:
        mod.unregister()


if __name__ == '__main__':
    register()
