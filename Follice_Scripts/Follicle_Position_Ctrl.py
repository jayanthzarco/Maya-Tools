# Control the follicle position on the nurbs surface or mesh
# Best use for creating sliding control rigs1
# Created By Jayanth on 27-05-2021

import re
import pymel.core as pm
from maya import cmds


class FollicleController:
    def __init__(self):
        self.objects = {"mesh": {}, "nurbs": {}}
        self.default_uv_coordinates = [0.7, 0.3]
        self.follicle_list = []

    @staticmethod
    def _convert_uv(obj):
        if isinstance(obj, pm.PyNode):
            obj = obj.name()
        cmds.select(obj, replace=True)
        sel = cmds.ConvertSelectionToUVs()
        uv = cmds.polyEditUV(sel, query=True)
        return uv

    @staticmethod
    def _decode_vtx_string(vtx_string, typ):
        match = re.match(rf'{typ}\[(\d+):(\d+)\]', vtx_string)
        if match:
            start_index = int(match.group(1))
            end_index = int(match.group(2))
            vtx_list = [f'{typ}[{i}]' for i in range(start_index, end_index + 1)]
            return vtx_list
        return None

    def process_mesh(self, mesh_node):
        if ".vtx" in mesh_node and ":" in mesh_node and "map[" not in mesh_node:
            n, v = mesh_node.split(".")
            vtx_list = self._decode_vtx_string(v, typ="vtx")
            for vtx in vtx_list:
                uv = self._convert_uv(f"{n}.{vtx}")
                self.objects['mesh'][f"{n}.{vtx}"] = uv
        elif ".vtx" in mesh_node:
            uv = self._convert_uv(mesh_node)
            self.objects['mesh'][mesh_node] = uv
        elif ".map" in mesh_node and ":" in mesh_node:
            n, m = mesh_node.split(".")
            map_list = self._decode_vtx_string(m, typ="map")
            for m in map_list:
                uv = self._convert_uv(f"{n}.{m}")
                self.objects['mesh'][f"{n}.{m}"] = uv
        elif ".map" in mesh_node:
            uv = self._convert_uv(mesh_node)
            self.objects['mesh'][mesh_node] = uv

    def process_transform(self, transform_node):
        shape = pm.listRelatives(transform_node, shapes=True)
        if shape:
            shape = shape[0]
            if shape.nodeType() == "mesh":
                self.objects["mesh"][shape.name()] = self.default_uv_coordinates
            elif shape.nodeType() == "nurbsSurface":
                self.objects["nurbs"][shape.name()] = self.default_uv_coordinates
        else:
            pm.warning("No shape found for transform:", transform_node)

    def process_selected_objects(self):
        sel = pm.ls(sl=True)
        for obj in sel:
            if obj.nodeType() == "mesh":
                self.process_mesh(obj.name())
            elif obj.nodeType() == "nurbsSurface" and "uv" in obj.name():
                uv_index = re.findall(r'\d+\.\d+', obj.name())[-1]
                uv = [float(uv_index.split('.')[0]), float(uv_index.split('.')[1])]
                self.objects["nurbs"][obj.name()] = uv
            elif obj.nodeType() == "transform":
                self.process_transform(obj.name())
            else:
                pm.warning("Select mesh or nurbs")
        return self.objects

    def create_follicle_on_mesh(self, mesh=None, nurbs=None, pos=None):
        if mesh:
            foll_shape = cmds.createNode('follicle')
            foll_trans = cmds.listRelatives(foll_shape, parent=True)[0]
            cmds.connectAttr(mesh + '.outMesh', foll_shape + '.inputMesh', force=True)
            cmds.connectAttr(mesh + '.worldMatrix[0]', foll_shape + ".inputWorldMatrix", force=True)
        elif nurbs:
            foll_shape = cmds.createNode('follicle')
            foll_trans = cmds.listRelatives(foll_shape, parent=True)[0]
            cmds.connectAttr(nurbs + '.local', foll_shape + '.inputSurface', force=True)
            cmds.connectAttr(nurbs + '.worldMatrix[0]', foll_shape + ".inputWorldMatrix", force=True)

        cmds.connectAttr(foll_shape + '.outTranslate', foll_trans + '.translate', force=True)
        cmds.connectAttr(foll_shape + '.outRotate', foll_trans + ".rotate", force=True)

        cmds.setAttr(foll_shape + '.parameterU', pos[0])
        cmds.setAttr(foll_shape + '.parameterV', pos[1])

        print(f"Follicle created on {pos[0]}, {pos[1]}")
        self.follicle_list.append([foll_trans, foll_shape])

    def create_follicle_ctrl(self):
        for fol in self.follicle_list:
            pos = fol[-1]
            ctrl = cmds.circle(name=fol[0] + "_Ctrl", ch=False)[0]
            limit_group = cmds.group(ctrl, name=ctrl + "_Limit_Group")
            offset_group = cmds.group(limit_group, name=ctrl + "_Offset_Group")
            cmds.matchTransform(offset_group, fol[0])

            mnd = cmds.createNode("multiplyDivide", name=fol[0] + "_MND")
            for t in "XYZ":
                cmds.connectAttr(ctrl + ".translate" + t, mnd + ".input1" + t)
                cmds.setAttr(mnd + ".input2" + t, -1)
                cmds.connectAttr(mnd + ".output" + t, limit_group + ".translate" + t)

            pma = cmds.createNode("plusMinusAverage", name=fol[0] + "_PMA")
            cmds.setAttr(pma + ".input2D[0].input2Dx", pos[0])
            cmds.setAttr(pma + ".input2D[0].input2Dy", pos[1])

            if "mesh" in fol:
                cmds.connectAttr(mnd + ".outputX", pma + ".input2D[1].input2Dx")
                cmds.connectAttr(mnd + ".outputX", pma + ".input2D[1].input2Dy")
            elif "nurbs" in fol:
                cmds.connectAttr(ctrl + ".translateX", pma + ".input2D[1].input2Dx")
                cmds.connectAttr(ctrl + ".translateY", pma + ".input2D[1].input2Dy")

            cmds.connectAttr(pma + ".output2Dx", fol[1] + ".parameterU")
            cmds.connectAttr(pma + ".output2Dy", fol[1] + ".parameterV")

    def create_follicle_ctrl_last(self):
        for fol in self.follicle_list:
            ctrl = cmds.circle(name=fol[0] + "_Master_Ctrl", ch=False)[0]
            cmds.setAttr(ctrl + ".translateX", lock=True)
            cmds.setAttr(ctrl + ".translateY", lock=True)
            cmds.setAttr(ctrl + ".translateZ", lock=True)
            cmds.setAttr(ctrl + ".scaleX", lock=True)
            cmds.setAttr(ctrl + ".scaleY", lock=True)
            cmds.setAttr(ctrl + ".scaleZ", lock=True)

            cmds.matchTransform(ctrl, fol[0])

            for t in "XYZ":
                cmds.connectAttr(ctrl + ".translate" + t, fol[0] + ".translate" + t)

            cmds.parentConstraint(ctrl, fol[0], maintainOffset=True)


if __name__ == "__main__":
    fc = FollicleController()
    fc.process_selected_objects()
    fc.create_follicle_ctrl()
    fc.create_follicle_ctrl_last()
