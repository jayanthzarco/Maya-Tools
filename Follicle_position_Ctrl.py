import re
from maya import cmds
import pymel.core as pm


class MeshProcessor:
    def __init__(self):
        self.objects = {"mesh": {}, "nurbs": {}}
        self.default_uv_coordinates = [0.7, 0.3]

    @staticmethod
    def _list_index(node):
        numbers = re.findall(r'\d+\.\d+', node)
        return [float(num) for num in numbers]

    @staticmethod
    def _convert_uv(obj_):
        cmds.select(obj_, replace=True)
        sel = cmds.ConvertSelectionToUVs()
        uv = cmds.polyEditUV(sel, query=True)
        return uv

    @staticmethod
    def decode_vtx_string(vtx_string, typ):
        match = re.match(rf'{typ}\[(\d+):(\d+)\]', vtx_string)
        if match:
            start_index = int(match.group(1))
            end_index = int(match.group(2))
            vtx_list = [f'{typ}[{i}]' for i in range(start_index, end_index + 1)]
            return vtx_list
        else:
            return None

    def process_mesh(self, mesh_node):
        if ".vtx" in mesh_node and ":" in mesh_node and "map[" not in mesh_node:
            n, v = mesh_node.split(".")
            cord = self.decode_vtx_string(v, typ="vtx")
            for i in cord:
                ocd = n + "." + i
                uv = self._convert_uv(ocd)
                self.objects['mesh'][ocd] = uv
        elif ".vtx" in mesh_node:
            cord = self._convert_uv(mesh_node)
            self.objects['mesh'][mesh_node] = cord
        elif ".map" in mesh_node and ":" in mesh_node:
            n, m = mesh_node.split(".")
            cord = self.decode_vtx_string(m, typ="map")
            for i in cord:
                ocd = n + "." + i
                uv = self._convert_uv(ocd)
                self.objects['mesh'][ocd] = uv
        elif ".map" in mesh_node:
            uv = self._convert_uv(mesh_node)
            self.objects['mesh'][mesh_node] = uv

    def process_transform(self, transform_node):
        shape = pm.listRelatives(transform_node, shapes=True)
        if shape:
            shape = shape[0]
            if pm.nodeType(shape) == "mesh":
                self.objects["mesh"][shape.name()] = self.default_uv_coordinates
            elif pm.nodeType(shape) == "nurbsSurface":
                self.objects["nurbs"][shape.name()] = self.default_uv_coordinates
        else:
            pm.warning("No shape found for transform:", transform_node)

    def process_selected_objects(self):
        sel_ = pm.ls(sl=True)
        for x in sel_:
            if pm.nodeType(x) == "mesh":
                self.process_mesh(x.name())
            elif pm.nodeType(x) == "nurbsSurface" and "uv" in x.name():
                cor = x.name().split('uv')[-1]
                uv = self._list_index(cor)
                self.objects["nurbs"][x.name()] = uv
            elif pm.nodeType(x) == "transform":
                self.process_transform(x)
            else:
                pm.warning("Select mesh or nurbs")
        return self.objects
    # Example usage:


mesh_processor = MeshProcessor()
obj = mesh_processor.process_selected_objects()
print(obj)


def __create_follicle_on_mesh(mesh__, pos=None):
    foll_shape_ = cmds.createNode('follicle')
    foll_trans = cmds.listRelatives(foll_shape_, parent=True)[0]
    print(foll_trans)

    cmds.connectAttr(mesh__ + '.outMesh', foll_shape_ + '.inputMesh', force=True)
    cmds.connectAttr(mesh__ + '.worldMatrix[0]', foll_shape_ + ".inputWorldMatrix", force=True)

    cmds.connectAttr(foll_shape_ + '.outTranslate', foll_trans + '.translate', force=True)
    cmds.connectAttr(foll_shape_ + '.outRotate', foll_trans + ".rotate", force=True)

    cmds.setAttr(foll_shape_ + '.parameterU', pos[0])
    cmds.setAttr(foll_shape_ + '.parameterV', pos[1])

    print(f"Follicle created on {pos[0]}, {pos[1]}")
    return [foll_trans, foll_shape_]


for each in obj['mesh']:
    if ".vtx" or ".map" in each:
        mesh = each.split(".")[0]
    else:
        mesh = each
    position = obj['mesh'].get(each)
    if len(position) != 2:
        continue
    foll_ = __create_follicle_on_mesh(mesh, position)



