import os
import sys
import numpy as np

sys.path.append('path/to/BlenderToolbox/BlenderToolbox/') # change this to your path to “path/to/BlenderToolbox/"

import BlenderToolBox as bt
import os, bpy, bmesh
import numpy as np
import glob

sys.path.append("./")
from utils import *

def init_scene(camLocation=(-1., -1., 1.), lookAtLocation=(0.5,0.5,0.), fov=np.pi/3., use_pano=False, imgRes_x = 2000, imgRes_y = 2000, numSamples = 1, exposure = 1.5, ao_factor = 0.25):
    ## initialize blender
    bt.blenderInit(imgRes_x, imgRes_y, numSamples, exposure)

    bpy.context.scene.world.light_settings.use_ambient_occlusion = True  # turn AO on
    bpy.context.scene.world.light_settings.ao_factor = ao_factor


    # to accelerate rendering
    bpy.context.scene.cycles.denoising_input_passes = 'RGB_ALBEDO'
    bpy.context.scene.cycles.denoising_prefilter = 'NONE'

    ## set gray shadow to completely white with a threshold
    bt.shadowThreshold(alphaThreshold = 0.05, interpolationMode = 'CARDINAL')

    ## set camera (recommend to change mesh instead of camera, unless you want to adjust the Elevation)
    cam = bt.setCamera(camLocation, lookAtLocation, 10)
    cam.data.lens_unit = "FOV"
    cam.data.angle = fov

    if use_pano:
        # If a panoramic camera is required:
        bpy.context.scene.objects["Camera"].data.type = "PANO"
        bpy.context.scene.objects["Camera"].data.cycles.panorama_type = 'EQUIRECTANGULAR'

    return cam

cwd = os.getcwd()

ptSize = 0.002

cloud_name = "RhombicDodecahedron"


cam = init_scene()

lamp_loc = (-1.,-1.,4.)
## set light
lamp = bt.setLight_sun(lamp_loc, 1.)

ply = read_ply_CC_ls("./{}.ply".format(cloud_name), ["vertex","Planarity"])
xyz = ply["vertex"]
# ply dict has to contain "R","G","B" and/or "red","green","blue" keys when using the "RGB" colormap.
ply["R"] = xyz[:,0]
ply["G"] = xyz[:,1]
ply["B"] = xyz[:,2]

outputPath = os.path.join(cwd, './renders/{}.png'.format(cloud_name)) # make it abs path for windows

# create_blender_cloud("{}".format(cloud_name), ply, ptSize)
create_blender_cloud(cloud_name, ply, ptSize, min_val=None,max_val=None, cmap="RGB")

# ## save blender file so that you can adjust parameters in the UI
bpy.ops.wm.save_mainfile(filepath='{}/{}.blend'.format(cwd,cloud_name))

# save rendering
bt.renderImage(outputPath, cam)

# # reset before processing next file
# bpy.ops.wm.read_factory_settings(use_empty=True)
