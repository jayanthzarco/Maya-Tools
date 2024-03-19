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


def __create_follicle_on_mesh(mesh__, nurbs__, pos=None):
    foll_shape_ = cmds.createNode('follicle')
    foll_trans = cmds.listRelatives(foll_shape_, parent=True)[0]
    print(foll_trans)
    if nurbs__ is None:
        cmds.connectAttr(mesh__ + '.outMesh', foll_shape_ + '.inputMesh', force=True)
        cmds.connectAttr(mesh__ + '.worldMatrix[0]', foll_shape_ + ".inputWorldMatrix", force=True)
    if mesh__ is None:
        cmds.connectAttr(nurbs__ + '.local', foll_shape_ + '.inputSurface', force=True)
        cmds.connectAttr(nurbs__ + '.worldMatrix[0]', foll_shape_ + ".inputWorldMatrix", force=True)

    cmds.connectAttr(foll_shape_ + '.outTranslate', foll_trans + '.translate', force=True)
    cmds.connectAttr(foll_shape_ + '.outRotate', foll_trans + ".rotate", force=True)

    cmds.setAttr(foll_shape_ + '.parameterU', pos[0])
    cmds.setAttr(foll_shape_ + '.parameterV', pos[1])

    print(f"Follicle created on {pos[0]}, {pos[1]}")
    return [foll_trans, foll_shape_]


mesh_pro = MeshProcessor()
objects = mesh_pro.process_selected_objects()

foll_list = []
for each in objects['mesh']:
    pos = objects['mesh'].get(each)
    if ".vtx" or ".map" in each:
        mesh = each.split(".")[0]
    else:
        mesh = each
    if len(pos) != 2:
        continue
    foll = __create_follicle_on_mesh(mesh__=mesh, nurbs__=None, pos=pos)
    foll.append("mesh")
    foll.append(pos)
    foll_list.append(foll)


for each in objects['nurbs']:
    pos = objects['nurbs'].get(each)
    foll__ = __create_follicle_on_mesh(mesh__=None, nurbs__=each, pos=pos)
    foll__.append("nurbs")
    foll__.append(pos)
    foll_list.append(foll__)

def __create_follicle_ctrl(foll__):
    for each_ in foll__:
        pos = each_[-1]
        ctrl__ = cmds.circle(name=each_[0] + "_Ctrl", ch=False)[0]
        limit_group__ = cmds.group(ctrl__, name=ctrl__ + "_Limit_Group")
        offset_group__ = cmds.group(limit_group__, name=ctrl__ + "_Offset_Group")
        cmds.matchTransform(offset_group__, each_[0])
        mnd = cmds.createNode("multiplyDivide", name=each_[0]+"_MND")

        for t in "XYZ":
            cmds.connectAttr(ctrl__+".translate"+t, mnd+".input1"+t)
            cmds.setAttr(mnd + ".input2" + t, -1)
            cmds.connectAttr(mnd + ".output" + t, limit_group__ + ".translate" + t)

        cmds.parentConstraint(each_[0], offset_group__, maintainOffset=True)
        pma = cmds.createNode("plusMinusAverage", name=each_[0]+"_PMA")

        cmds.setAttr(pma+".input2D[0].input2Dx", pos[0])
        cmds.setAttr(pma+".input2D[0].input2Dy", pos[1])

        if "mesh" in each_:
            cmds.connectAttr(mnd + ".output.outputX", pma + ".input2D[1].input2Dx")
            cmds.connectAttr(mnd + ".output.outputX", pma + ".input2D[1].input2Dy")

        if "nurbs" in each_:
            cmds.connectAttr(ctrl__+".tx", pma+".input2D[1].input2Dx")
            cmds.connectAttr(ctrl__+".ty", pma+".input2D[1].input2Dy")

        cmds.connectAttr(pma+".output2Dx", each_[0]+".parameterU")
        cmds.connectAttr(pma+".output2Dy", each_[0]+".parameterV")


__create_follicle_ctrl(foll__=foll_list)
