This repository contains a small extension to the [BlenderToolBox](https://github.com/HTDerekLiu/BlenderToolbox) of [Hsueh-Ti Derek Liu](https://github.com/HTDerekLiu). It provides a simple interface to render scalar fields on point clouds efficiently by leveraging Blender's geometry nodes.

<p align="center">
  <img align="center"  src="/renders/RhombicDodecahedron.png", width=400>
</p>

# Features
- Usage of geometry nodes to efficiently render large-scale point clouds;
- panoramic or standard rendering option;
- parula colormap for scalar field rendering;
- RGB point cloud rendering from ply scalar fields.

# Installation
1. Download blender 3.2 alpha.
2. Install [BlenderToolBox](https://github.com/HTDerekLiu/BlenderToolbox).
3. Modify ``blenderInit.py`` at line 31 as follows:
```python
#bpy.data.scenes[0].view_layers['View Layer']['cycles']['use_denoising'] = 1
bpy.context.scene.cycles.use_preview_denoising = True
```
4. Install [pip](https://pypi.org/project/pip/) on blender's internal python (3.10).
5. Pip install [plyfile](https://pypi.org/project/plyfile/) to read/write ply files.

# Run
1. Modify the ``run.bat`` (or ``run.sh``) so that the blender python path corresponds to your blender 3.2 alpha.
2. Modify the path to the BlenderToolBox in ``main.py``.
3. launch ``run.bat`` (or ``run.sh``).
