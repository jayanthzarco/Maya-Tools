# this script helps to create a follicle on selected position
# select any vertices or uv and run the script
# code is created on 20-05-2021
# published 08-March-2024 by Jayanth

from maya import cmds
def __create_follicle(mesh, pos=None):
    if pos is None:
        pos = [0.7, 0.1]
    foll_shape_ = cmds.createNode('follicle')
    foll_trans = cmds.listRelatives(foll_shape_, parent=True)[0]
    print(foll_trans)

    cmds.connectAttr(mesh+'.outMesh', foll_shape_+'.inputMesh', force=True)
    cmds.connectAttr(mesh+'.worldMatrix[0]', foll_shape_+".inputWorldMatrix", force=True)

    cmds.connectAttr(foll_shape_+'.outTranslate', foll_trans+'.translate', force=True)
    cmds.connectAttr(foll_shape_+'.outRotate', foll_trans+".rotate", force=True)

    cmds.setAttr(foll_shape_+'.parameterU', pos[0])
    cmds.setAttr(foll_shape_ + '.parameterV', pos[1])

    print(f"Follicle created on {pos[0]}, {pos[1]}")


def __follicle_on_selection():
    selection_ = cmds.ls(sl=True)
    if not selection_:
        return cmds.warning("select something")
    for each in selection_:
        mesh_ = each.split('.')[0]
        if not cmds.nodeType(cmds.listRelatives(mesh_, shapes=True)[0]) == "mesh":
            return cmds.warning("select polygon mesh")
        cmds.select(each, replace=True)
        convert_ = cmds.ConvertSelectionToUVs()
        uv = cmds.polyEditUV(convert_, query=True) or None
        __create_follicle(mesh=mesh_, pos=uv)

if __name__ == '__main__':
    __follicle_on_selection()

"""
created by Jayanth K
"""

