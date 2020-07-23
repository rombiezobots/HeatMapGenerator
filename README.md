# Heat Map Generator for Blender

## What it does
Heat maps, in this context, are Vertex Groups containing a normalised (1-0) representation of the required amount of detail of a given mesh. These can be used as a foundation for sculpting, and even as a direct input for particle systems and modifiers such as Decimate, Displace, etc.

## How it works
1. Make sure your active object is local.
1. Vertex distances are measured from the active scene camera, including those triggered by timeline markers. Make sure the scene has an active camera before you start.
1. The generator uses the global output frame range, and switches to the preview range if you've enabled it (see Timeline). It also uses the global frame step, so be sure to increase it if you have a very dense mesh, or for any reason don't need to sample every frame.
1. Look for the Heat Map Generator panel inside Vertex Groups in your active object's mesh data properties, and hit Measure to get started. Please note that depending on the amount of vertices in your mesh, this can take a while.

### Remapping and painting
Because you might want to tweak the mapping of the normalised vertex weights, painting the vertex group has been decoupled from the measuring process.
- This allows you to tweak the lower and upper tresholds (in BU), since you're unlikely to need every tiny weight decrease between distant vertices.
- Keep in mind that in order for the result to utilise the full 1-0 range, the lower treshold will not be used if it's lower than the smallest sampled vertex distance. Likewise for the upper treshold.
- To reset the tresholds to the sampled extremes, simply toggle the Use Tresholds checkbox.

## To do
- Occlusion from other objects
- Vertex bleed control

## Acknowledgements
Heat Map Generator is based on some work I did on a similar tool, originally written in 2016 for Maya, by Zeno Pelgrims and Wim Coene at Grid VFX.
