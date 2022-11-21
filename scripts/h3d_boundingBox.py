#!/usr/bin/python
# ================================
# (C)2021 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# boundingBox v1.0
# Bounding box creation for selected meshes
# ================================

import modo
import lx
import modo.constants as c

scene = modo.scene.current()

bool_delete_source = lx.eval('user.value h3d_bb_del_src ?')
bb_mesh_list = list()


def strip_name(name='', replace=True):
    if not replace:
        return name
    if name == '':
        return ''
    strip_index = name.rfind(' (')
    if strip_index > 0:
        return name[:strip_index]
    else:
        return name


def get_source_of_instance(input_item=None):
    if input_item is None:
        return None
    if not input_item.isAnInstance:
        return input_item
    source_item = input_item.itemGraph('source').forward(0)
    if source_item.isAnInstance:
        return get_source_of_instance(source_item)
    else:
        return source_item


def create_bounding_box(items_list=None):
    if items_list is None:
        return
    for current_item in items_list:
        if current_item.isAnInstance:
            instance_source = get_source_of_instance(current_item)
            corners = instance_source.geometry.boundingBox
        else:
            corners = current_item.geometry.boundingBox
        current_item.select(replace=True)
        item_name = strip_name(name=lx.eval('item.name ?'), replace=False)
        scene.deselect()
        lx.eval('layer.new')
        lx.eval('item.name "{}"'.format(item_name + '_BoundingBox'))
        lx.eval('tool.set prim.cube on')
        lx.eval('tool.attr prim.cube minX {}'.format(corners[0][0]))
        lx.eval('tool.attr prim.cube minY {}'.format(corners[0][1]))
        lx.eval('tool.attr prim.cube minZ {}'.format(corners[0][2]))
        lx.eval('tool.attr prim.cube maxX {}'.format(corners[1][0]))
        lx.eval('tool.attr prim.cube maxY {}'.format(corners[1][1]))
        lx.eval('tool.attr prim.cube maxZ {}'.format(corners[1][2]))
        lx.eval('tool.apply')
        lx.eval('tool.set prim.cube off')

        item_parent = current_item.parent
        bb_mesh = scene.selectedByType(c.MESH_TYPE)[0]

        current_item.select(replace=False)
        lx.eval('item.match item pos')
        lx.eval('item.match item rot')
        lx.eval('item.match item scl')

        bb_mesh.select(replace=True)
        bb_mesh_list.append(bb_mesh)
        lx.eval('item.draw add locator')
        # set wireframe display mode for the item
        lx.eval('item.channel locator$style wire')
        lx.eval('select.color "item.channel locator$wireColor ?"')
        lx.eval('item.channel locator$wireColor {1.0 1.0 0.0}')
        lx.eval('item.channel locator$wireOptions user')
        lx.eval('item.channel oc_general_visibility 0.0')
        lx.eval('item.channel locator$render off')
        lx.eval('mesh.setBBox true')
        if item_parent is not None:
            item_parent.select()
            lx.eval('item.parent position:0 inPlace:1')
        if bool_delete_source:
            current_item.select(replace=True)
            if not current_item.isAnInstance:
                try:
                    lx.eval('item.channel locator$lock off')
                    lx.eval('!!xref.manageOptions unlessForbid ifAllow unlessForbid always unlessForbid')
                except RuntimeError:
                    print('Item: <' +
                          current_item.name +
                          '> Runtime Error exception in Manage XREF Options command. Ignored.')
            scene.removeItems(current_item)


selectedMeshes = scene.selectedByType(c.MESH_TYPE)
selectedInstances = scene.selectedByType(c.MESHINST_TYPE)

# work with instances first (delete instances first)
create_bounding_box(selectedInstances)
create_bounding_box(selectedMeshes)

# select newly created bounding boxes
scene.deselect()
for item in bb_mesh_list:
    item.select()
