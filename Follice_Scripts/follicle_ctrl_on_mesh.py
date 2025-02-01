import pymel.core as pm

def create_follicle(mesh, pos=None):
    """Creates a follicle on the given mesh at the specified UV position."""
    if pos is None:
        pos = [0.7, 0.1]

    foll_shape = pm.createNode('follicle')
    foll_trans = foll_shape.getParent()

    mesh.outMesh.connect(foll_shape.inputMesh, force=True)
    mesh.worldMatrix[0].connect(foll_shape.inputWorldMatrix, force=True)

    foll_shape.outTranslate.connect(foll_trans.translate, force=True)
    foll_shape.outRotate.connect(foll_trans.rotate, force=True)

    foll_shape.parameterU.set(pos[0])
    foll_shape.parameterV.set(pos[1])

    print(f"Follicle created on {pos[0]}, {pos[1]}")
    return foll_trans, foll_shape


def create_follicle_ctrl(fol):
    """Creates a control for the follicle, constraining it properly."""
    fol_trans, fol_shape = fol

    ctrl = pm.circle(ch=False)[0]
    limit_group = pm.group(ctrl, name=ctrl + '_Limit_Group')
    offset_group = pm.group(limit_group, name=ctrl + "_Offset_Group")
    pm.matchTransform(offset_group, fol_trans)

    mnd = pm.createNode("multiplyDivide", name=fol_trans + "_MND")

    for t in ["X", "Y", "Z"]:
        ctrl.attr(f"translate{t}") >> mnd.attr(f"input1{t}")
        mnd.attr(f"input2{t}").set(-1)
        mnd.attr(f"output{t}") >> limit_group.attr(f"translate{t}")

    pma = pm.createNode("plusMinusAverage", name=fol_trans + "_PMA")
    pma.input2D[0].input2Dx.set(fol_shape.parameterU.get())
    pma.input2D[0].input2Dy.set(fol_shape.parameterV.get())

    mnd.outputX >> pma.input2D[1].input2Dx
    mnd.outputY >> pma.input2D[1].input2Dy

    pma.output2D.output2Dx >> fol_shape.parameterU
    pma.output2D.output2Dy >> fol_shape.parameterV

    pm.parentConstraint(fol_trans, offset_group, mo=True)
    pm.scaleConstraint(fol_trans, offset_group, mo=True)


def get_selected_meshes():
    """Returns selected mesh transforms only."""
    return [obj for obj in pm.ls(selection=True, long=True) if obj.getShape() and obj.getShape().type() == "mesh"]


# Example Usage
selected_meshes = get_selected_meshes()
if selected_meshes:
    follicle = create_follicle(selected_meshes[0])
    create_follicle_ctrl(follicle)
else:
    pm.warning("No mesh selected!")
