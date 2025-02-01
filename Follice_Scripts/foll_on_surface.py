import maya.cmds as cmds

# Select the NURBS surface first, then the control object, and run the script
sel = cmds.ls(sl=True)

if len(sel) < 2:
    cmds.warning("Select a NURBS surface and a control object.")
else:
    nurbs_surface = sel[0]
    ctrl = sel[1].replace("Ctrl", "Master_ctrl")

    # Create nodes
    closest_point = cmds.createNode("closestPointOnSurface", n="closestPointOnSurface_node")
    arc_length = cmds.createNode("arcLengthDimension", n="arcLengthDimension_node")

    # Get world position of the control object
    pos = cmds.xform(ctrl, q=True, t=True, ws=True)

    # Connect attributes
    cmds.connectAttr(nurbs_surface + ".local", closest_point + ".inputSurface")
    cmds.setAttr(closest_point + ".inPosition", pos[0], pos[1], pos[2])

    cmds.connectAttr(nurbs_surface + ".worldSpace", arc_length + ".nurbsGeometry")

    # Create a temporary group
    temp_grp = cmds.group(em=True, n="temp")
    cmds.connectAttr(closest_point + ".parameterU", temp_grp + ".tx")
    cmds.connectAttr(closest_point + ".parameterV", temp_grp + ".ty")

    # Get parameter values
    paraU = cmds.getAttr(temp_grp + ".tx")
    paraV = cmds.getAttr(temp_grp + ".ty")

    cmds.setAttr(arc_length + ".uParamValue", paraU)
    cmds.setAttr(arc_length + ".vParamValue", paraV)
    cmds.connectAttr(arc_length + ".arcLength", temp_grp + ".sx")

    # Get arc length values
    arclenU = cmds.getAttr(temp_grp + ".sx")
    arclenV = cmds.getAttr(temp_grp + ".sy")

    # Clean up temporary nodes
    cmds.delete(temp_grp, cmds.listRelatives(arc_length, p=True), arc_length, closest_point)

    # Create follicle node
    follicle = cmds.createNode("follicle", n=ctrl + "_follicleShape")
    cmds.connectAttr(nurbs_surface + ".local", follicle + ".inputSurface")
    cmds.connectAttr(nurbs_surface + ".worldMatrix", follicle + ".inputWorldMatrix")
    cmds.setAttr(follicle + ".parameterU", paraU)
    cmds.setAttr(follicle + ".parameterV", paraV)

    cmds.connectAttr(follicle + ".outTranslate", follicle.replace("Shape", ".t"))
    cmds.connectAttr(follicle + ".outRotate", follicle.replace("Shape", ".r"))

    # Create control circle
    cmds.circle(nrx=0, nry=0, nrz=1, d=3, ch=False, n=ctrl)
    grp = cmds.group(em=True, n=ctrl + "_Group")

    # Create transformation group
    off = cmds.group(em=True, n=ctrl + "_Xform_Group")
    cmds.parent(ctrl, grp)
    cmds.parent(grp, off)
    cmds.delete(cmds.parentConstraint(follicle.replace("Shape", ""), off, mo=False))
    cmds.parent(off, follicle.replace("Shape", ""))

    # Add attributes to control
    cmds.addAttr(ctrl, ln="ArcLengthU", at="float")
    cmds.setAttr(ctrl + ".ArcLengthU", arclenU * 2)

    cmds.addAttr(ctrl, ln="ArcLengthV", at="float")
    cmds.setAttr(ctrl + ".ArcLengthV", arclenV * 2)

    cmds.addAttr(ctrl, ln="DefaultParameterU", at="float")
    cmds.setAttr(ctrl + ".DefaultParameterU", paraU)

    cmds.addAttr(ctrl, ln="DefaultParameterV", at="float")
    cmds.setAttr(ctrl + ".DefaultParameterV", paraV)

    # Create decompose matrix node
    dmat = cmds.createNode("decomposeMatrix", n=grp + "_DMAT")
    cmds.connectAttr(ctrl + ".inverseMatrix", dmat + ".inputMatrix")
    cmds.connectAttr(dmat + ".outputTranslate", grp + ".translate")
    cmds.connectAttr(dmat + ".outputRotate", grp + ".rotate")
    cmds.connectAttr(dmat + ".outputScale", grp + ".scale")

    # Create multiplyDivide node
    md = cmds.createNode("multiplyDivide", n=ctrl + "_Conversion_MD")
    cmds.connectAttr(ctrl + ".ArcLengthU", md + ".input1X")
    cmds.connectAttr(ctrl + ".ArcLengthV", md + ".input1Y")
    cmds.setAttr(md + ".input2X", -1)
    cmds.setAttr(md + ".input2Y", -1)

    # Create setRange node
    sr = cmds.createNode("setRange", n=ctrl + "_Conversion_SR")
    cmds.connectAttr(md + ".outputX", sr + ".oldMinX")
    cmds.connectAttr(md + ".outputY", sr + ".oldMinY")
    cmds.connectAttr(ctrl + ".ArcLengthU", sr + ".oldMaxX")
    cmds.connectAttr(ctrl + ".ArcLengthV", sr + ".oldMaxY")
    cmds.setAttr(sr + ".minX", -1)
    cmds.setAttr(sr + ".minY", -1)
    cmds.setAttr(sr + ".maxX", 1)
    cmds.setAttr(sr + ".maxY", 1)

    cmds.connectAttr(ctrl + ".tx", sr + ".valueX")
    cmds.connectAttr(ctrl + ".ty", sr + ".valueY")

    # Create plusMinusAverage node
    pma = cmds.createNode("plusMinusAverage", n=ctrl + "_Parameter_PMA")
    cmds.connectAttr(ctrl + ".DefaultParameterU", pma + ".input2D[0].input2Dx")
    cmds.connectAttr(ctrl + ".DefaultParameterV", pma + ".input2D[0].input2Dy")
    cmds.connectAttr(sr + ".outValueX", pma + ".input2D[1].input2Dx")
    cmds.connectAttr(sr + ".outValueY", pma + ".input2D[1].input2Dy")
    cmds.connectAttr(pma + ".output2Dx", follicle + ".parameterU")
    cmds.connectAttr(pma + ".output2Dy", follicle + ".parameterV")

    print("Follicle-driven control setup complete!")
