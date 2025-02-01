import maya.cmds as cmds


def __create_follicle(mesh, pos=None):
    if pos is None:
        pos = [0.7, 0.1]
    foll_shape_ = cmds.createNode('follicle')
    foll_trans = cmds.listRelatives(foll_shape_, parent=True)[0]
    print(foll_trans)

    cmds.connectAttr(mesh + '.outMesh', foll_shape_ + '.inputMesh', force=True)
    cmds.connectAttr(mesh + '.worldMatrix[0]', foll_shape_ + ".inputWorldMatrix", force=True)

    cmds.connectAttr(foll_shape_ + '.outTranslate', foll_trans + '.translate', force=True)
    cmds.connectAttr(foll_shape_ + '.outRotate', foll_trans + ".rotate", force=True)

    cmds.setAttr(foll_shape_ + '.parameterU', pos[0])
    cmds.setAttr(foll_shape_ + '.parameterV', pos[1])

    print(f"Follicle created on {pos[0]}, {pos[1]}")
    return [foll_trans, foll_shape_]


def __create_follicle_ctrl(fol):
    pos = fol[-1]
    ctrl = cmds.circle(ch=False)[0]
    limit_group = cmds.group(ctrl, name=ctrl + '_Limit_Group')
    offset_group = cmds.group(limit_group, name=ctrl + "_Offset_Group")
    cmds.matchTransform(offset_group, fol[0])

    mnd = cmds.createNode("multiplyDivide", name=fol[0] + "_MND")

    for t in ["X", "Y", "Z"]:
        cmds.connectAttr(ctrl + ".translate" + t, mnd + ".input1" + t)
        cmds.setAttr(mnd + ".input2" + t, -1)
        cmds.connectAttr(mnd + ".output" + t, limit_group + ".translate" + t)

    pma = cmds.createNode("plusMinusAverage", name=fol[0] + "_PMA")
    cmds.setAttr(pma + ".input2D[0].input2Dx", pos[0])
    cmds.setAttr(pma + ".input2D[0].input2Dy", pos[1])

    cmds.connectAttr(mnd + ".outputX", pma + ".input2D[1].input2Dx")
    cmds.connectAttr(mnd + ".outputX", pma + ".input2D[1].input2Dy")

    cmds.connectAttr(pma + ".output2Dx", fol[1] + ".parameterU")
    cmds.connectAttr(pma + ".output2Dy", fol[1] + ".parameterV")

    cmds.parentConstraint(fol[0], offset_group, mo=True)


def __get_selected_meshes():
    return [obj for obj in cmds.ls(selection=True, long=True)
            if cmds.listRelatives(obj, shapes=True, type="mesh")]


mesh = __get_selected_meshes()
follicle = __create_follicle(mesh[0])
__create_follicle_ctrl(follicle)


