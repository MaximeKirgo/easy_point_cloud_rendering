This repository contains a small extension to the [https://github.com/HTDerekLiu/BlenderToolbox](BlenderToolBox) of [https://github.com/HTDerekLiu](Hsueh-Ti Derek Liu). It provides a simple interface to render scalar fields on point clouds efficiently by leveraging Blender's geometry nodes.

The renders can be performed as panoramic renders or standard renders.

<p align="center">
  <img align="center"  src="/renders/RhombicDodecahedron.png", width=800>
</p>

# Installation
1. Download blender 3.2 alpha.
2. Install BlenderToolBox.
3. Modify ``blenderInit.py`` at line 31 as follows:
```python
#bpy.data.scenes[0].view_layers['View Layer']['cycles']['use_denoising'] = 1
bpy.context.scene.cycles.use_preview_denoising = True
```
4. [Optional] Install pip on blender's internal python (3.10).
5. [Optional] Pip install plyfile to read/write ply files.

# Run
1. Modify the run.bat (or run.sh) so that the blender python path corresponds to your blender 3.2 alpha.
2. Modify the path to BlenderToolBox in main.py.
3. launch run.bat (or run.sh).
