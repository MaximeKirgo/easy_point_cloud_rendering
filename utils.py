import os, bpy, bmesh
import numpy as np

from plyfile import PlyData, PlyElement


# color palette from brewer
# light_gray = (233./255., 233./255., 233./255., 1)
light_gray = (186./255.,186./255.,186./255.,1.)
dark_gray = (64./255.,64./255.,64./255.,1.)

brewer_blue = (43./255.,131./255.,186./255.,1)
brewer_orange = (253./255.,174./255.,97./255.,1)
brewer_yellow = (255./255.,255./255.,191./255.,1)
brewer_lightgreen = (171./255.,221./255.,164./255.,1)
brewer_red = (215./255.,25./255.,28./255.,1)

brewer_darkblue = (5/255.,113/255.,176/255.,1.)
brewer_darkred = (202/255.,0/255.,32/255.,1.)
brewer_lightblue = (146/255.,197/255.,222/255.,1.)
brewer_lightred = (244/255.,165/255.,130/255.,1.)


# Matlab colormap
# parula = [
#    (0, 0.447, 0.741, 1),
#    (0.85, 0.325, 0.098, 1),
#    (0.929, 0.694, 0.125, 1),
#    (0.466, 0.674, 0.188, 1),
#    (0.494, 0.184, 0.556, 1),
#    (0.301, 0.745, 0.933, 1),
#    (0.635, 0.078, 0.184, 1)
# ]
# parula = [(0.2422, 0.1504, 0.6603, 1.),
#         (0.2803, 0.2782, 0.9221, 1.),
#         (0.2440, 0.4358, 0.9988, 1.),
#         (0.1540, 0.5902, 0.9218, 1.),
#         (0.0297, 0.7082, 0.8163, 1.),
#         (0.1938, 0.7758, 0.6251, 1.),
#         (0.5044, 0.7993, 0.3480, 1.),
#         (0.8634, 0.7406, 0.1596, 1.),
#         (0.9892, 0.8136, 0.1885, 1.),
#         (0.9769, 0.9839, 0.0805, 1.)]

# 3E26A8
# 4747EB
# 3E6FFF
# 3E6FFF
# 2797EB
# 08B5D0
# 31C69F
# 81CC59
# DCBD29
# FCCF30
# F9FB15
# parula = [(0.048172,)]
# parula = [
# 0x3E26A8,
# 0x4747EB,
# 0x3E6FFF,
# 0x3E6FFF,
# 0x2797EB,
# 0x08B5D0,
# 0x31C69F,
# 0x81CC59,
# 0xDCBD29,
# 0xFCCF30,
# 0xF9FB15
# ]
parula = [
0x3e26a8,
0x4747eb,
0x3e6fff,
0x2797eb,
0x08b5d0,
0x31c69f,
0x81cc59,
0xdcbd29,
0xfccf30,
0xf9fb15,
]
def srgb_to_linearrgb(c):
    if   c < 0:       return 0
    elif c < 0.04045: return c/12.92
    else:             return ((c+0.055)/1.055)**2.4

def hex_to_rgb(h,alpha=1):
    r = (h & 0xff0000) >> 16
    g = (h & 0x00ff00) >> 8
    b = (h & 0x0000ff)
    return tuple([srgb_to_linearrgb(c/0xff) for c in (r,g,b)] + [alpha])


TPTNFPFN = [brewer_red,brewer_blue,light_gray,dark_gray]


MAPS = {"parula":parula,"TPTNFPFN":TPTNFPFN}


def get_dtype_dict(name):
    dtype_dict = {'names':["scalar_{}".format(name)],'formats':['f4']}
    if name=="vertex" or name=="point":
        dtype_dict = {'names':['x','y','z'], 'formats':['f4','f4','f4']}
    elif name=="intensity":
        dtype_dict = {'names':['variation'],'formats':['f4']}
    elif name=="normal":
        dtype_dict = {'names':['nx','ny','nz'], 'formats':['f4','f4','f4']}
    return dtype_dict
def read_ply_ls(directory,ls,print_infos=False):
    '''
    Reads ply files with custom scalar fields
    '''
    plydata = PlyData.read(directory)
    if print_infos:
        print(plydata)
    out_dict = {}
    for name in ls:
        name = (name,name)
        dtype_dict = get_dtype_dict(name[1])
        dat = plydata[name[0]]
        elems_ls = []
        for channel in dtype_dict["names"]:
            elems_ls.append(dat[channel])
        out_dict[name[1]] = np.transpose(np.array(elems_ls,dtype=np.float32))

    return out_dict
def read_ply_CC_ls(directory,ls,print_infos=False):
    '''
    Reads ply files with scalar fields on "vertex" element only
    '''
    plydata = PlyData.read(directory)
    if print_infos:
        print(plydata)
    out_dict = {}
    for name in ls:
        dtype_dict = get_dtype_dict(name)
        dat = plydata["vertex"]
        elems_ls = []
        for channel in dtype_dict["names"]:
            elems_ls.append(dat[channel])
        out_dict[name] = np.transpose(np.array(elems_ls,dtype=np.float32))

    return out_dict


def set_node_output(object,geo_mod,attribute_name):
    inputs = geo_mod.node_group.inputs
    if attribute_name not in inputs:
        inputs.new("NodeSocketColor", attribute_name)
    id = inputs[attribute_name].identifier

def create_point_cloud_structure(geo_mod, point_size):
    # create the point cloud structure
    tree = geo_mod.node_group

    inputnode = None
    outputnode = None
    for n in tree.nodes:
        if n.name=="Group Output":
            outputnode = n
        elif n.name=="Group Input":
            inputnode = n
    pointnode = tree.nodes.new('GeometryNodeMeshToPoints')
    pointnode.inputs['Radius'].default_value = point_size
    matnode = tree.nodes.new('GeometryNodeSetMaterial')
    tree.links.new(inputnode.outputs['Geometry'], pointnode.inputs['Mesh'])
    tree.links.new(pointnode.outputs['Points'], matnode.inputs['Geometry'])
    tree.links.new(matnode.outputs['Geometry'], outputnode.inputs['Geometry'])

    return tree,matnode


def create_attr_and_range_nodes(tree,min_val,max_val,sf):
    attr_node = tree.nodes.new(type="ShaderNodeAttribute")
    attr_node.name = "ShaderNodeAttribute_{}".format(sf)
    attr_node.attribute_name = sf
    range_node = tree.nodes.new(type="ShaderNodeMapRange")
    range_node.name="ShaderNodeMapRange_{}".format(sf)
    range_node.inputs[1].default_value = min_val[sf]# min value of sf
    range_node.inputs[2].default_value = max_val[sf]# max value of sf
    tree.links.new(attr_node.outputs['Fac'], range_node.inputs['Value'])

    return attr_node,range_node

def create_point_cloud_material(matnode,cloud_name,cloud_dict, min_val=None, max_val=None, cmap="parula"):
    obj = bpy.data.objects[cloud_name]

    mat_name = "{}_Mat".format(cloud_name)
    mat = bpy.data.materials.new(name=mat_name)
    obj.data.materials.append(mat)
    obj.active_material = mat
    mat.use_nodes = True

    # link to object
    matnode.inputs[2].default_value = bpy.data.materials[mat_name]

    tree = mat.node_tree

    main_node = tree.nodes['Principled BSDF']

    main_node.inputs["Roughness"].default_value = 1.
    main_node.inputs["Specular"].default_value = 0.
    main_node.inputs["Sheen"].default_value = 0.

    scalar_fields = [k for k in cloud_dict.keys() if k!="vertex"]

    if min_val is None:
        min_val = {}
        for sf in scalar_fields:
            min_val[sf] = cloud_dict[sf].min()
    if max_val is None:
        max_val = {}
        for sf in scalar_fields:
            max_val[sf] = cloud_dict[sf].max()

    if cmap.upper()=="RGB":
        attr_nodes = {}
        range_nodes = {}
        for sf in scalar_fields:
            if sf.upper()=="R" or sf.upper()=="RED":
                attr_node,range_node = create_attr_and_range_nodes(tree,min_val,max_val,sf)
                attr_nodes["R"] = attr_node
                range_nodes["R"] = range_node
            elif sf.upper()=="G" or sf.upper()=="GREEN":
                attr_node,range_node = create_attr_and_range_nodes(tree,min_val,max_val,sf)
                attr_nodes["G"] = attr_node
                range_nodes["G"] = range_node
            elif sf.upper()=="B" or sf.upper()=="BLUE":
                attr_node,range_node = create_attr_and_range_nodes(tree,min_val,max_val,sf)
                attr_nodes["B"] = attr_node
                range_nodes["B"] = range_node
        rgb_combine = tree.nodes.new(type="ShaderNodeCombineRGB")
        tree.links.new(range_nodes["R"].outputs['Result'], rgb_combine.inputs[0])
        tree.links.new(range_nodes["G"].outputs['Result'], rgb_combine.inputs[1])
        tree.links.new(range_nodes["B"].outputs['Result'], rgb_combine.inputs[2])
        tree.links.new(rgb_combine.outputs[0], main_node.inputs['Base Color'])
    else:
        attr_nodes = []
        range_nodes = []
        for sf in scalar_fields:
            attr_node,range_node = create_attr_and_range_nodes(tree,min_val,max_val,sf)
            attr_nodes.append(attr_node)
            range_nodes.append(range_node)
        colormap = MAPS[cmap]
        ramp_node = tree.nodes.new(type="ShaderNodeValToRGB")
        cmap_pos = np.linspace(0,1,len(colormap))
        cmap_pos = cmap_pos[1:-1] # first and last already exist
        for cpos in cmap_pos:
            ramp_node.color_ramp.elements.new(position = cpos)
        for cmap_node,hex in zip(ramp_node.color_ramp.elements,colormap):
            cmap_node.color = hex_to_rgb(hex)


        tree.links.new(range_nodes[0].outputs['Result'], ramp_node.inputs['Fac'])
        tree.links.new(ramp_node.outputs['Color'], main_node.inputs['Base Color'])


def create_blender_cloud(name, cloud_dict, point_size=0.005, min_val=None, max_val=None, cmap="parula",collection_name="Collection"):

    pos = cloud_dict["vertex"]


    # load the python points
    mesh = bpy.data.meshes.new(name)
    mesh.name = name
    obj = bpy.data.objects.new(name, mesh)
    obj.name = name

    collection = bpy.data.collections.get(collection_name)
    collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    mesh.from_pydata(pos, [], [])

    # create the modifier
    geo_mod = obj.modifiers.new(name="GeometryNodes", type='NODES')

    scalar_fields = [k for k in cloud_dict.keys() if k!="vertex"]
    for sf in scalar_fields:
        bpy.ops.geometry.attribute_add(name=sf)#, type='FLOAT', domain='POINT')
        obj.data.attributes[sf].data.foreach_set('value', cloud_dict[sf])

        set_node_output(obj,geo_mod,sf)



    geomod_tree,matnode = create_point_cloud_structure(geo_mod, point_size)
    create_point_cloud_material(matnode, name, cloud_dict, min_val, max_val, cmap=cmap)
