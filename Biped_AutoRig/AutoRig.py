import maya.cmds as cmds
import pymel.core as pm

def lock_attrs(obj, t, r, s, v):
    if cmds.objExists(obj):
        # Translate
        if t[0] == 1:
            cmds.setAttr("{}.tx".format(obj), lock=True, keyable=False)
        elif t[0] == 0:
            cmds.setAttr("{}.tx".format(obj), lock=False, keyable=True)

        if t[1] == 1:
            cmds.setAttr("{}.ty".format(obj), lock=True, keyable=False)
        elif t[1] == 0:
            cmds.setAttr("{}.ty".format(obj), lock=False, keyable=True)

        if t[2] == 1:
            cmds.setAttr("{}.tz".format(obj), lock=True, keyable=False)
        elif t[2] == 0:
            cmds.setAttr("{}.tz".format(obj), lock=False, keyable=True)

        # Rotate
        if r[0] == 1:
            cmds.setAttr("{}.rx".format(obj), lock=True, keyable=False)
        elif r[0] == 0:
            cmds.setAttr("{}.rx".format(obj), lock=False, keyable=True)

        if r[1] == 1:
            cmds.setAttr("{}.ry".format(obj), lock=True, keyable=False)
        elif r[1] == 0:
            cmds.setAttr("{}.ry".format(obj), lock=False, keyable=True)

        if r[2] == 1:
            cmds.setAttr("{}.rz".format(obj), lock=True, keyable=False)
        elif r[2] == 0:
            cmds.setAttr("{}.rz".format(obj), lock=False, keyable=True)

        # Scale
        if s[0] == 1:
            cmds.setAttr("{}.sx".format(obj), lock=True, keyable=False)
        elif s[0] == 0:
            cmds.setAttr("{}.sx".format(obj), lock=False, keyable=True)

        if s[1] == 1:
            cmds.setAttr("{}.sy".format(obj), lock=True, keyable=False)
        elif s[1] == 0:
            cmds.setAttr("{}.sy".format(obj), lock=False, keyable=True)

        if s[2] == 1:
            cmds.setAttr("{}.sz".format(obj), lock=True, keyable=False)
        elif s[2] == 0:
            cmds.setAttr("{}.sz".format(obj), lock=False, keyable=True)

        # Visibility
        if v == 1:
            cmds.setAttr("{}.visibility".format(obj), lock=True, keyable=False)
        elif v == 0:
            cmds.setAttr("{}.visibility".format(obj), lock=False, keyable=True)
    else:
        raise ValueError("lock_attrs: {} does not exist".format(obj))

def set_pivots(source, dest):
    locator = cmds.spaceLocator()
    cmds.pointConstraint(source, locator[0])

    t = cmds.getAttr("{}.translate".format(locator[0]))[0]
    cmds.move(t[0], t[1], t[2], "{}.scalePivot".format(dest), "{}.rotatePivot".format(dest), absolute=True)

    cmds.delete(locator[0])

def find_namespace(string):
    namespace = ""
    buffer = string.split(":")

    for i in range(len(buffer) - 1):
        namespace += buffer[i] + ":"

    return namespace

def stretch_nodes(start, end, use_one_node, base_name, end_name, stretch_on_off, min_stretch, save_volume, attr, min_distance):
    cond_node = ""
    b2attr = ""
    stretch_on_off_x = ""
    stretch_on_off_y = ""

    for i in range(start, end + 1):
        joint = "{}{}{}".format(base_name, i, end_name)

        if (use_one_node and i == start) or not use_one_node:
            mul_node = cmds.createNode('multiplyDivide')
            mul_node = cmds.rename(mul_node, "{}_stretch_multiplyDivide".format(joint))

            cmds.setAttr("{}.operation".format(mul_node), 2)  # divide

            if cmds.objExists(min_distance):
                cmds.connectAttr(min_distance, "{}.input1Y".format(mul_node))
                cmds.connectAttr(min_distance, "{}.input2X".format(mul_node))
            else:
                cmds.setAttr("{}.input1Y".format(mul_node), cmds.getAttr(attr))
                cmds.setAttr("{}.input2X".format(mul_node), cmds.getAttr(attr))

            cmds.connectAttr(attr, "{}.input1X".format(mul_node))
            cmds.connectAttr(attr, "{}.input2Y".format(mul_node))
            cmds.setAttr("{}.input1Z".format(mul_node), 1)
            # ------------------------------------
            cond_node = cmds.createNode('condition')
            cond_node = cmds.rename(cond_node, "{}_stretch_condition".format(joint))

            cmds.setAttr("{}.operation".format(cond_node), 2)  # greater than

            cmds.connectAttr("{}.outputX".format(mul_node), "{}.firstTerm".format(cond_node))
            cmds.connectAttr("{}.outputX".format(mul_node), "{}.colorIfTrueR".format(cond_node))
            cmds.connectAttr("{}.outputY".format(mul_node), "{}.colorIfTrueG".format(cond_node))

            cmds.connectAttr("{}.outputZ".format(mul_node), "{}.colorIfFalseG".format(cond_node))

            if cmds.objExists(min_stretch):
                cmds.connectAttr(min_stretch, "{}.input2Z".format(mul_node))
                cmds.connectAttr(min_stretch, "{}.colorIfFalseR".format(cond_node))
                cmds.connectAttr(min_stretch, "{}.secondTerm".format(cond_node))
            else:
                cmds.setAttr("{}.input2Z".format(mul_node), float(min_stretch))
                cmds.setAttr("{}.colorIfFalseR".format(cond_node), float(min_stretch))
                cmds.setAttr("{}.secondTerm".format(cond_node), float(min_stretch))

            if cmds.objExists(save_volume):
                b2attr = cmds.createNode('blendTwoAttr', name="{}_saveVolume_blendTwoAttr".format(joint))
                cmds.setAttr("{}.i[0]".format(b2attr), 1)
                cmds.connectAttr("{}.outColorG".format(cond_node), "{}.i[1]".format(b2attr))
                cmds.connectAttr(save_volume, "{}.attributesBlender".format(b2attr))

            if cmds.objExists(stretch_on_off):
                stretch_on_off_x = cmds.createNode('blendTwoAttr', name="{}_stretchOnOffX_blendTwoAttr".format(joint))
                stretch_on_off_y = cmds.createNode('blendTwoAttr', name="{}_stretchOnOffY_blendTwoAttr".format(joint))

                cmds.connectAttr(stretch_on_off, "{}.attributesBlender".format(stretch_on_off_x))
                cmds.connectAttr(stretch_on_off, "{}.attributesBlender".format(stretch_on_off_y))

                cmds.setAttr("{}.i[0]".format(stretch_on_off_x), 1)
                cmds.setAttr("{}.i[0]".format(stretch_on_off_y), 1)

                if cmds.objExists(save_volume):
                    cmds.connectAttr("{}.outColorR".format(cond_node), "{}.i[1]".format(stretch_on_off_x))
                    cmds.connectAttr("{}.output".format(b2attr), "{}.i[1]".format(stretch_on_off_y))
                else:
                    cmds.connectAttr("{}.outColorR".format(cond_node), "{}.i[1]".format(stretch_on_off_x))
                    cmds.connectAttr("{}.outColorG".format(cond_node), "{}.i[1]".format(stretch_on_off_y))
            # if $stretchOnOff

        # if $useOneNode

        if cmds.objExists(save_volume):
            if cmds.objExists(stretch_on_off):
                cmds.connectAttr("{}.output".format(stretch_on_off_x), "{}.sx".format(joint))
                cmds.connectAttr("{}.output".format(stretch_on_off_y), "{}.sy".format(joint))
                cmds.connectAttr("{}.output".format(stretch_on_off_y), "{}.sz".format(joint))
            else:
                cmds.connectAttr("{}.outColorR".format(cond_node), "{}.sx".format(joint))
                cmds.connectAttr("{}.output".format(b2attr), "{}.sy".format(joint))
                cmds.connectAttr("{}.output".format(b2attr), "{}.sz".format(joint))
        else:  # no volume preservation
            if cmds.objExists(stretch_on_off):
                cmds.connectAttr("{}.output".format(stretch_on_off_x), "{}.sx".format(joint))
                cmds.connectAttr("{}.output".format(stretch_on_off_y), "{}.sy".format(joint))
                cmds.connectAttr("{}.output".format(stretch_on_off_y), "{}.sz".format(joint))
            else:
                cmds.connectAttr("{}.outColorR".format(cond_node), "{}.sx".format(joint))
                cmds.connectAttr("{}.outColorG".format(cond_node), "{}.sy".format(joint))
                cmds.connectAttr("{}.outColorG".format(cond_node), "{}.sz".format(joint))
    # for

    return [cond_node, b2attr, stretch_on_off_x, stretch_on_off_y]

def add_to_set(set_name, objects):
    if not cmds.objExists(set_name):
        cmds.sets(name=set_name, empty=True)

    cmds.sets(objects, add=set_name)

def connect_10_01(driver, attrs1, attrs0):
    name = driver.replace(".", "_")
    plus = ""

    if not cmds.objExists("{}_plusMinusAverage".format(name)):
        plus = cmds.createNode('plusMinusAverage', name="{}_plusMinusAverage".format(name))
        cmds.setAttr("{}.operation".format(plus), 2)  # subtraction

        cmds.setAttr("{}.input2D[0].input2Dx".format(plus), 1)
        cmds.connectAttr(driver, "{}.input2D[1].input2Dx".format(plus))

        cmds.connectAttr(driver, "{}.input2D[0].input2Dy".format(plus))
        cmds.setAttr("{}.input2D[1].input2Dy".format(plus), 0)
    else:
        plus = "{}_plusMinusAverage".format(name)

    for a in attrs1:
        if cmds.objExists(a):
            cmds.connectAttr("{}.output2Dx".format(plus), a)

    for a in attrs0:
        if cmds.objExists(a):
            cmds.connectAttr("{}.output2Dy".format(plus), a)

    return plus

def shape_parent(parent, objects, new_name):
    for obj in objects:
        if obj == parent:
            continue

        cmds.lockNode(obj, lock=False)
        cmds.parent(obj, parent)

        obj_shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
        cmds.makeIdentity(obj, apply=True, translate=True, rotate=True, scale=True, normal=False)

        for shape in obj_shapes:
            if new_name:
                shape = cmds.rename(shape, new_name)
            cmds.parent(shape, parent, shape=True)

        cmds.delete(obj)

def make_dynamic_parent(control, parent_to, data):
    if len(data) == 0:
        raise ValueError("makeDynamicParent: 'data' is not specified")

    dyn_names = []
    dyn_constraints = []

    for item in data:
        parts = item.split("=")
        dyn_names.append(parts[0].strip())
        dyn_constraints.append(parts[1].strip())

    enum_names = "(no parent):" + ":".join(dyn_names)
    cmds.addAttr(control, longName="parent", attributeType="enum", enumName=enum_names, keyable=True)

    parent_constraint = cmds.parentConstraint(dyn_constraints, parent_to, maintainOffset=True)
    cmds.setAttr(parent_constraint[0] + ".interpType", 2)  # shortness

    for i in range(len(dyn_constraints)):
        if not cmds.objExists(dyn_constraints[i]):
            raise RuntimeError("makeDynamicParent: No object matched {}".format(dyn_constraints[i]))

        cmds.disconnectAttr("{}.scale".format(dyn_constraints[i]), "{}.target[{}].targetScale".format(parent_constraint[0], i))

        cmds.setDrivenKeyframe("{}.W{}".format(parent_constraint[0], i), currentDriver=control + ".parent", driverValue=i, value=0)
        cmds.setDrivenKeyframe("{}.W{}".format(parent_constraint[0], i), currentDriver=control + ".parent", driverValue=i + 1, value=1)
        cmds.setDrivenKeyframe("{}.W{}".format(parent_constraint[0], i), currentDriver=control + ".parent", driverValue=i + 2, value=0)


def create_control(type, objects, params, visible_attr):
    coeff = cmds.getAttr("character_tuners.controlsSize")

    curves_list = []

    if type == "sphere":
        curve1 = cmds.circle(nr=(1, 0, 0), r=params[0] * coeff)
        curve2 = cmds.circle(nr=(0, 1, 0), r=params[0] * coeff)
        curve3 = cmds.circle(nr=(0, 0, 1), r=params[0] * coeff)

        cmds.select(curve1, curve2, curve3)
        cmds.DeleteHistory()

        curves_list = [curve1[0], curve2[0], curve3[0]]

    elif type == "circle":
        if params[2] == 0:
            curve = cmds.circle(nr=(1, 0, 0), r=params[0] * coeff)
        elif params[2] == 1:
            curve = cmds.circle(nr=(0, 1, 0), r=params[0] * coeff)
        elif params[2] == 2:
            curve = cmds.circle(nr=(0, 0, 1), r=params[0] * coeff)
        else:
            cmds.warning("createControl: {} must be 0, 1, or 2. Skipped".format(params[2]))
            return

        cmds.select(curve)
        cmds.DeleteHistory()

        curves_list = [curve[0]]

    elif type == "flag":
        curve = cmds.curve(d=1, p=[(0, 0, 0), (0, params[0] * coeff * 2, 0),
                                   (params[0] * coeff * 1, params[0] * coeff * 2, 0),
                                   (0, params[0] * coeff * 3, 0), (-params[0] * coeff * 1, params[0] * coeff * 2, 0),
                                   (0, params[0] * coeff * 2, 0)])
        cmds.scale(1, params[2], 1, curve)
        cmds.makeIdentity(curve, apply=True, translate=True, rotate=True, scale=True, normal=False)

        cmds.select(curve)
        cmds.DeleteHistory()

        curves_list = [curve]

    elif type == "rect":
        width = params[2] * params[0] * coeff
        height = params[3] * params[0] * coeff

        if params[4] == 0:
            curve = cmds.curve(d=1, p=[(0, -width / 2, -height / 2), (0, -width / 2, height / 2),
                                       (0, -width / 2, height / 2), (0, width / 2, height / 2),
                                       (0, width / 2, -height / 2), (0, -width / 2, -height / 2)])
        elif params[4] == 1:
            curve = cmds.curve(d=1, p=[(-width / 2, 0, -height / 2), (-width / 2, 0, height / 2),
                                       (-width / 2, 0, height / 2), (width / 2, 0, height / 2),
                                       (width / 2, 0, -height / 2), (-width / 2, 0, -height / 2)])
        elif params[4] == 2:
            curve = cmds.curve(d=1, p=[(-width / 2, -height / 2, 0), (-width / 2, height / 2, 0),
                                       (-width / 2, height / 2, 0), (width / 2, height / 2, 0),
                                       (width / 2, -height / 2, 0), (-width / 2, -height / 2, 0)])

        cmds.select(curve)
        cmds.DeleteHistory()

        curves_list = [curve]

    elif type == "cube":
        size = params[0] * coeff
        step = 0.5
        curve = cmds.curve(d=1, p=[(-step * size, -step * size, step * size), (step * size, -step * size, step * size),
                                   (step * size, -step * size, -step * size),
                                   (-step * size, -step * size, -step * size),
                                   (-step * size, -step * size, step * size), (-step * size, step * size, step * size),
                                   (-step * size, step * size, step * size), (-step * size, step * size, -step * size),
                                   (-step * size, step * size, -step * size), (step * size, step * size, -step * size),
                                   (step * size, step * size, -step * size), (step * size, -step * size, -step * size),
                                   (step * size, -step * size, step * size), (step * size, step * size, step * size),
                                   (step * size, step * size, step * size), (-step * size, step * size, step * size)])

        cmds.select(curve)
        cmds.DeleteHistory()

        curves_list = [curve]

    shape_parent(curves_list[0], curves_list, "")
    cmds.delete(cmds.parentConstraint(objects[1], curves_list[0]))

    shape_parent(objects[0], [curves_list[0]], objects[0] + "Shape1")

    cmds.color(objects[0], ud=int(params[1]))

    if visible_attr:
        if not cmds.attributeQuery(visible_attr, node=objects[0], exists=True):
            cmds.addAttr(objects[0], ln=visible_attr, at="bool", dv=True, k=True)

        cmds.lockNode(objects[0], lock=False)
        cmds.connectAttr("main." + visible_attr, objects[0] + ".v")
        cmds.lockNode(objects[0], lock=True)


def draw_help_line(objs, base_name, visible_attr):
    curve_cmd = "curve -n {}_helpLine_curve -d 1 ".format(base_name)

    for i, obj in enumerate(objs):
        curve_cmd += "-p {} 0 0 ".format(i)

    cmds.evalDeferred(curve_cmd)

    group = cmds.group(n="{}_helpLine_group".format(base_name), em=True, p="others")
    cmds.connectAttr(visible_attr, "{}.v".format(group))
    cmds.lockNode(group, lock=True)

    cmds.parent("{}_helpLine_curve".format(base_name), group)
    cmds.setAttr("{}.template".format("{}_helpLine_curve".format(base_name)), True)
    cmds.lockNode("{}_helpLine_curve".format(base_name), lock=True)

    for i, obj in enumerate(objs):
        locator = cmds.spaceLocator(n="{}_helpLine_locator{}".format(base_name, i + 1))
        cmds.connectAttr("{}.t".format(locator[0]), "{}.controlPoints[{}]".format("{}_helpLine_curve".format(base_name), i))
        cmds.parent(locator[0], group)

        cmds.setAttr("{}.v".format(locator[0]), False)
        cmds.pointConstraint(obj, locator[0])
        cmds.lockNode(locator[0], lock=True)

def create_main_hierarchy():
    cmds.group(n="character", em=True)
    cmds.group(n="skeleton", em=True, p="character")
    cmds.group(n="controls", em=True, p="character")
    cmds.group(n="other_controls", em=True, p="controls")
    cmds.group(n="fingers_controls", em=True, p="controls")
    cmds.group(n="others", em=True, p="character")
    cmds.group(n="preferences", em=True, p="character")

    cmds.addAttr(ln="id", dt="string", at="string", k=True, dv="auto-character v1", parent="preferences")
    rotY = cmds.getAttr("character_tuners.ry")
    axis = "x" if rotY in [0, 180, -180] else "z" if rotY in [-90, 90] else ""
    cmds.addAttr(ln="axis", dt="string", at="string", k=True, dv=axis, parent="preferences")

    cmds.group(n="geometry", em=True, p="character")
    cmds.group(n="main", em=True, p="character")

    cmds.addAttr("main", ln="scaleFactor", at="double", min=0.01, dv=1, k=True)
    cmds.addAttr("main", at="bool", ln="visibilities", dv=True, k=True)
    cmds.addAttr("main", at="bool", ln="mesh", dv=True, k=True)
    cmds.connectAttr("main.mesh", "geometry.v")
    cmds.addAttr("main", at="bool", ln="others", dv=True, k=True)
    cmds.connectAttr("main.others", "others.v")

    cmds.connectAttr("main.scaleFactor", "main.sx")
    cmds.connectAttr("main.scaleFactor", "main.sy")
    cmds.connectAttr("main.scaleFactor", "main.sz")
    cmds.connectAttr("main.t", "controls.t")
    cmds.connectAttr("main.r", "controls.r")
    cmds.connectAttr("main.s", "controls.s")
    cmds.connectAttr("main.s", "skeleton.s")

    cmds.createControl("circle", ["main", "main"], [5.0, 8, 1], "")

    cmds.lockNode("character", lock=False)
    cmds.lockNode("geometry", lock=True)
    cmds.lockNode("others", lock=True)
    cmds.lockNode("preferences", lock=True)
    cmds.lockNode("skeleton", lock=False)
    cmds.lockNode("controls", lock=False)
    cmds.lockNode("other_controls", lock=True)
    cmds.lockNode("fingers_controls", lock=True)
    cmds.lockNode("main", lock=True)


def create_distance(name, point1, point2):
    distance_dimension = cmds.createNode('distanceDimShape')

    sp1 = cmds.spaceLocator()
    sp2 = cmds.spaceLocator()
    cmds.connectAttr("{}.translate".format(sp1[0]), "{}.startPoint".format(distance_dimension))
    cmds.connectAttr("{}.translate".format(sp2[0]), "{}.endPoint".format(distance_dimension))

    cmds.pointConstraint(point1, sp1[0])
    cmds.pointConstraint(point2, sp2[0])

    cmds.group(sp1[0], sp2[0], distance_dimension, n="{}_group".format(name), p="others")
    cmds.setAttr("{}.v".format(name + "_group"), False)

    lock_attrs("{}_group".format(name), [1, 1, 1], [1, 1, 1], [1, 1, 1], 1)

    cmds.rename(cmds.listRelatives(distance_dimension, parent=True)[0], name)

    return [distance_dimension, sp1[0], sp2[0]]

def create_stretch_rig(params, base_name, points, rotates, constraints, parent_to):
    num_joints = params[0]
    num_controls = params[1]

    if num_joints < 2:
        cmds.warning("createStretchRig: {} must be > 1".format(num_joints))
        return
    if num_controls < 2:
        cmds.warning("createStretchRig: {} must be > 1".format(num_controls))
        return

    start_locator = cmds.spaceLocator(n="{}_startPoint".format(base_name))
    end_locator = cmds.spaceLocator(n="{}_endPoint".format(base_name))

    cmds.parent(end_locator[0], start_locator[0])
    cmds.parent(start_locator[0], parent_to)

    end_rotator = cmds.group(em=True, n="{}_endPointRotator".format(base_name), p=start_locator[0])

    nurbs_plane = cmds.nurbsPlane(p=[0, 0, 0], ax=[0, 1, 0], w=1, lr=1, d=3, u=num_joints, v=1, ch=False, n="{}_plane".format(base_name))
    cmds.setAttr("{}.v".format(nurbs_plane[0]), False)
    cmds.setAttr("{}.inheritsTransform".format(nurbs_plane[0]), False)
    cmds.setAttr("{}.template".format(nurbs_plane[1]), True)

    cmds.parent(nurbs_plane[0], start_locator[0])

    lock_attrs(nurbs_plane[0], [1, 1, 1], [1, 1, 1], [1, 1, 1], 1)

    joints_group = cmds.group(em=True, n="{}_joints_group".format(base_name), p=start_locator[0])
    follicle_group = cmds.group(em=True, n="{}_follicles_group".format(base_name), p=start_locator[0])

    lock_attrs(joints_group, [1, 1, 1], [1, 1, 1], [1, 1, 1], 1)
    lock_attrs(follicle_group, [1, 1, 1], [1, 1, 1], [1, 1, 1], 1)

    joints = []
    for i in range(1, num_joints + 1):
        follicle = cmds.createNode('follicle', n="{}_follicleShape{}".format(base_name, i))
        follicle_parent = cmds.listRelatives(follicle, parent=True)
        follicle_parent[0] = cmds.rename(follicle_parent[0], "{}_follicle{}".format(base_name, i))
        cmds.setAttr("{}.inheritsTransform".format(follicle_parent[0]), False)

        cmds.parent(follicle_parent[0], follicle_group)

        cmds.connectAttr("{}.outTranslate".format(follicle), "{}.t".format(follicle_parent[0]))
        cmds.connectAttr("{}.outRotate".format(follicle), "{}.r".format(follicle_parent[0]))

        cmds.connectAttr("{}.worldSpace".format(nurbs_plane[0]), "{}.inputSurface".format(follicle))

        step = (2 / float(num_joints) - 1 / float(num_joints)) / 2
        cmds.setAttr("{}.parameterU".format(follicle), (i / float(num_joints)) - step)
        cmds.setAttr("{}.parameterV".format(follicle), 0.5)
        cmds.setAttr("{}.visibility".format(follicle), False, lock=True)

        joint = cmds.joint(r=True, p=[0, 0, 0], radius=0.5, n="{}_joint{}".format(base_name, i))
        cmds.parent(joint, joints_group)
        cmds.joint(joint, e=True, zso=True, oj='xyz', sao='yup')

        cmds.parentConstraint(follicle_parent[0], joint)

        cmds.connectAttr("{}.sy".format(points[0]), "{}.sy".format(joint))
        cmds.connectAttr("{}.sz".format(points[0]), "{}.sz".format(joint))

        lock_attrs(follicle_parent[0], [1, 1, 1], [1, 1, 1], [1, 1, 1], 1)
        lock_attrs(joint, [1, 1, 1], [1, 1, 1], [1, 1, 1], 1)

        joints.append(joint)

    cmds.sets(joints, add="bindJointsSet")

    draw_help_line(joints, base_name, "{}.v".format(start_locator[0]))

    lattice = cmds.lattice(nurbs_plane[0], divisions=[num_controls, 2, 2], objectCentered=True, ldv=[2, 2, 2], ol=True, exclusive="characterPartition", n="{}_lattice".format(base_name))
    cmds.parent(lattice[1], lattice[2], start_locator[0])
    cmds.setAttr("{}.inheritsTransform".format(lattice[1]), False)
    cmds.setAttr("{}.inheritsTransform".format(lattice[2]), False)
    cmds.setAttr("{}.v".format(lattice[1]), False)
    cmds.setAttr("{}.v".format(lattice[2]), False)

    lock_attrs(lattice[1], [1, 1, 1], [1, 1, 1], [1, 1, 1], 1)
    lock_attrs(lattice[2], [1, 1, 1], [1, 1, 1], [1, 1, 1], 1)

    clusters_group = cmds.group(em=True, n="{}_clusters_group".format(base_name), p=start_locator[0])
    cmds.setAttr("{}.v".format(clusters_group), False)

    lock_attrs(clusters_group, [1, 1, 1], [1, 1, 1], [1, 1, 1], 1)

    for locator in [start_locator[0], end_locator[0]]:
        shape = cmds.listRelatives(locator, shapes=True)
        cmds.setAttr("{}.v".format(shape[0]), False, lock=True)

    for i in range(1, num_controls + 1):
        mult = cmds.createNode('multiplyDivide', n="{}_poser{}_multiplyDivide".format(base_name, i))
        cmds.connectAttr("{}.tx".format(end_locator[0]), "{}.input1X".format(mult))
        cmds.setAttr("{}.input2X".format(mult), (i - 1) / float(num_controls - 1))

        cmds.connectAttr("{}.rx".format(end_locator[0]), "{}.input1Y".format(mult))
        cmds.setAttr("{}.input2Y".format(mult), (i - 1) / float(num_controls - 1))

        group = cmds.group(em=True, n="{}_control{}_group".format(base_name, i), p=start_locator[0])
        cmds.connectAttr("{}.outputX".format(mult), "{}.tx".format(group))
        cmds.connectAttr("{}.outputY".format(mult), "{}.rx".format(group))

        control = cmds.group(em=True, n="{}_control{}".format(base_name, i), p=group)

        cluster = cmds.cluster("{}.pt[{}][0:1][0:1]".format(lattice[1], i - 1), n="{}_cluster{}".format(base_name, i))
        cmds.parent(cluster[1], clusters_group)
        cmds.parentConstraint(control, cluster[1])

        create_control("sphere", [control, control], [0.2, 1.0, 0], "stretchRig")

        lock_attrs(group, [1, 1, 1], [1, 1, 1], [1, 1, 1], 1)
        lock_attrs(control, [0, 0, 0], [1, 1, 1], [1, 1, 1], 1)

    for i in range(1, len(constraints) + 1):
        if cmds.objExists(constraints[i - 1]):
            cmds.pointConstraint(constraints[i - 1], "{}_control{}".format(base_name, i))
            lock_attrs("{}_control{}_group".format(base_name, i), [1, 1, 1], [1, 1, 1], [1, 1, 1], 0)
            cmds.setAttr("{}_control{}_group.v".format(base_name, i), False)
            lock_attrs("{}_control{}_group".format(base_name, i), [1, 1, 1], [1, 1, 1], [1, 1, 1], 1)

    cmds.pointConstraint(points[0], start_locator[0])
    cmds.pointConstraint(points[1], end_locator[0], skip=['y', 'z'])

    cmds.orientConstraint(rotates[0], start_locator[0])
    cmds.orientConstraint(rotates[1], end_rotator, mo=True)
    cmds.orientConstraint(end_rotator, end_locator[0], skip=['y', 'z'])

    lock_attrs(start_locator[0], [1, 1, 1], [1, 1, 1], [1, 1, 1], 1)
    lock_attrs(end_locator[0], [1, 1, 1], [1, 1, 1], [1, 1, 1], 1)
    lock_attrs(end_rotator, [1, 1, 1], [1, 1, 1], [1, 1, 1], 1)

def create_arm_leg(pref, type, stretch, stretchRigParams):
    # Additional joints and labels initialization
    additional_joints = []
    arm_tuner_label = ""
    elbow_tuner_label = ""
    hand_tuner_label = ""
    controls_label = "controls"
    arm_controls_label = ""
    arm_ik_controls_label = ""
    arm_fk_controls_label = ""
    arm_control_label = ""
    arm_joints_label = ""
    arm_label = ""
    arm_ik_label = ""
    elbow_ik_label = ""
    arm_fix_label = ""
    fix_label = ""
    arm_fk_label = ""
    elbow_fk_label = ""
    hand_fk_label = ""

    if type == "arm":
        additional_joints = [pref + "shoulder3_joint", pref + "hand1_joint", pref + "shoulder2_stretchRig_control2", "clavicle_joint"]
        arm_tuner_label = "arm_tuner"
        elbow_tuner_label = "elbow_tuner"
        hand_tuner_label = "hand_tuner"
        arm_controls_label = "arm_controls"
        arm_ik_controls_label = "armIK_controls"
        arm_fk_controls_label = "armFK_controls"
        arm_control_label = "arm_control"
        arm_joints_label = "arm_joints"
        arm_label = "arm"
        arm_ik_label = "armIK"
        elbow_ik_label = "elbowIK"
        arm_fix_label = "armElbowFix"
        fix_label = "elbowFix"
        arm_fk_label = "armFK"
        elbow_fk_label = "elbowFK"
        hand_fk_label = "handFK"

    elif type == "leg":
        additional_joints = ["hip_joint", pref + "footAux1_joint", pref + "foot1_joint", pref + "footAux9_joint", pref + "foot"]
        arm_tuner_label = "leg_tuner"
        elbow_tuner_label = "knee_tuner"
        hand_tuner_label = "foot1_tuner"
        arm_controls_label = "leg_controls"
        arm_ik_controls_label = "legIK_controls"
        arm_fk_controls_label = "legFK_controls"
        arm_control_label = "leg_control"
        arm_joints_label = "leg_joints"
        arm_label = "leg"
        arm_ik_label = "legIK"
        elbow_ik_label = "kneeIK"
        arm_fix_label = "legKneeFix"
        fix_label = "kneeFix"
        arm_fk_label = "legFK"
        elbow_fk_label = "kneeFK"
        hand_fk_label = "footFK"

    else:
        raise RuntimeError("createArmLeg: type must be 'arm' or 'leg'")

    # Clear selection
    pm.select(cl=True)

    # Fetch positions of arm components
    arm1_pos = pm.getAttr(pref + arm_tuner_label + ".worldPosition")[0]
    arm2_pos = pm.getAttr(pref + elbow_tuner_label + ".worldPosition")[0]
    arm3_pos = pm.getAttr(pref + hand_tuner_label + ".worldPosition")[0]

    # Compute vectors
    arm_elbow = arm2_pos - arm1_pos
    elbow_hand = arm3_pos - arm2_pos

    # Compute magnitudes
    mag_arm_elbow = arm_elbow.length()
    mag_elbow_hand = elbow_hand.length()

    # Initialize joint list
    arm_joints = []

    if type == "arm":
        coeff = 1
        orient = (0, 0, 0)

        if pref == "r_":
            coeff = 1
            orient = (0, 0, 0)

        # Create arm joints
        arm_joints.append(pm.joint(p=(0, 0, 0)))
        arm_joints.append(pm.joint(p=(coeff * mag_arm_elbow, 0, 0)))
        arm_joints.append(pm.joint(p=(coeff * mag_arm_elbow + coeff * mag_elbow_hand, 0, 0)))

        pm.setAttr(arm_joints[0] + ".jointOrient", orient)
        pm.setAttr(arm_joints[1] + ".preferredAngleY", -45)

    else:  # type == "leg"
        coeff = 1
        orient = (180, 0, 0)

        if pref == "r_":
            coeff = 1
            orient = (180, 0, 0)

        # Create leg joints
        arm_joints.append(pm.joint(p=(0, 0, 0)))
        arm_joints.append(pm.joint(p=(coeff * mag_arm_elbow, 0, 0)))
        arm_joints.append(pm.joint(p=(coeff * mag_arm_elbow + coeff * mag_elbow_hand, 0, 0)))

        pm.setAttr(arm_joints[0] + ".jointOrient", orient)
        pm.setAttr(arm_joints[1] + ".preferredAngleY", -45)

    # Create IK handle
    ik_handle = pm.ikHandle(startJoint=arm_joints[0], endEffector=arm_joints[2], solver="ikRPsolver")[0]
    pm.xform(ik_handle, ws=True, t=arm1_pos)

    # Cleanup and group creation steps
    # ...

    # Additional steps and constraints
    # ...

    # Return any necessary data
# FK
    cmds.group("-n {}_group -em -p {}".format(pref+arm_ik_label, pref+arm_fk_controls_label))
    cmds.group("-n {} -em -p {}_group".format(pref+arm_fk_label, pref+arm_fk_label))
    cmds.group("-n {}_group -em -p {}".format(pref+elbow_fk_label, pref+arm_fk_label))
    cmds.group("-n {} -em -p {}_group".format(pref+elbow_fk_label, pref+elbow_fk_label))
    cmds.group("-n {}_group -em -p {}".format(pref+hand_fk_label, pref+elbow_fk_label))
    cmds.group("-n {} -em -p {}_group".format(pref+hand_fk_label, pref+hand_fk_label))

    # Delete orient constraints
    cmds.delete('orientConstraint {} {}'.format(chainFK[0], pref+arm_fk_label+"_group"))
    cmds.delete('orientConstraint {} {}'.format(chainFK[1], pref+elbow_fk_label+"_group"))

    cmds.delete('orientConstraint {} {}'.format(pref+arm_ik_label, pref+hand_fk_label+"_group"))

    # Point constraints
    cmds.pointConstraint(chainFK[0], pref+arm_fk_label+"_group")
    cmds.pointConstraint(chainFK[1], pref+elbow_fk_label+"_group")
    cmds.pointConstraint(chainFK[2], pref+hand_fk_label+"_group")

    # Orient constraint
    cmds.orientConstraint(pref+arm_fk_label, chainFK[0])

    # BlendWeighted node creation and setup
    bw = cmds.createNode('blendWeighted', n="{}_blendWeighted".format(pref+elbow_fk_label))
    cmds.setAttr("{}.i[0]".format(bw), cmds.getAttr("{}.ry".format(chainFK[1])))
    cmds.connectAttr("{}.ry".format(pref+elbow_fk_label), "{}.i[1]".format(bw))
    cmds.connectAttr("{}.output".format(bw), "{}.ry".format(chainFK[1]))

    # IK FK switch attributes
    cmds.group("-n {}_ikRotate -em -p {}_group".format(pref+arm_fk_label, pref+arm_fk_label))
    cmds.orientConstraint(chainIK[0], pref+arm_fk_label+"_ikRotate")
    cmds.connectAttr("{}.rotateOrder".format(pref+arm_fk_label), "{}_ikRotate.rotateOrder".format(pref+arm_fk_label))

    cmds.group("-n {}_ikRotate -em -p {}_group".format(pref+hand_fk_label, pref+hand_fk_label))
    cmds.orientConstraint(pref+arm_ik_label, pref+hand_fk_label+"_ikRotate")
    cmds.connectAttr("{}.rotateOrder".format(pref+hand_fk_label), "{}_ikRotate.rotateOrder".format(pref+hand_fk_label))

    cmds.lockNode("{}_ikRotate".format(pref+arm_fk_label), lock=True, lockUnpublished=True)
    cmds.lockNode("{}_ikRotate".format(pref+hand_fk_label), lock=True, lockUnpublished=True)

    # Dynamic parent poser and translate rotate setup
    cmds.group("-n {}_dynamicParentPoser -em -p {}_group".format(pref+arm_ik_label, pref+arm_ik_label+"_group"))
    cmds.xform(ws=True, t=arm3Pos[0], arm3Pos[1], arm3Pos[2], pref+arm_ik_label+"_dynamicParentPoser")
    cmds.makeIdentity(apply=True, t=True, r=True, s=True, n=0, pref+arm_ik_label+"_dynamicParentPoser")
    cmds.connectAttr("{}.rotateOrder".format(pref+arm_ik_label), "{}_dynamicParentPoser.rotateOrder".format(pref+arm_ik_label))

    cmds.group("-n {}_fkTranslateRotate -em -p {}_group".format(pref+arm_ik_label, pref+arm_ik_label+"_group"))
    cmds.xform(ws=True, t=arm3Pos[0], arm3Pos[1], arm3Pos[2], pref+arm_ik_label+"_fkTranslateRotate")
    cmds.makeIdentity(apply=True, t=True, r=True, s=True, n=0, pref+arm_ik_label+"_fkTranslateRotate")
    cmds.connectAttr("{}.rotateOrder".format(pref+arm_ik_label), "{}_fkTranslateRotate.rotateOrder".format(pref+arm_ik_label))

    cmds.pointConstraint(chainFK[2], "{}_fkTranslateRotate".format(pref+arm_ik_label))
    cmds.orientConstraint(pref+hand_fk_label, "{}_fkTranslateRotate".format(pref+arm_ik_label))

    cmds.lockNode("{}_fkTranslateRotate".format(pref+arm_ik_label), lock=True, lockUnpublished=True)

    # Dynamic parent poser for elbow_ik_label
    cmds.group("-n {}_dynamicParentPoser -em -p {}_dynamicParent_group".format(pref+elbow_ik_label, pref+elbow_ik_label))
    cmds.delete('pointConstraint {} {}'.format(pref+elbow_ik_label+"_poser", pref+elbow_ik_label+"_dynamicParentPoser"))
    cmds.makeIdentity(apply=True, t=True, r=True, s=True, n=0, "{}_dynamicParentPoser".format(pref+elbow_ik_label))

    # Translate setup for elbow_ik_label
    cmds.group("-n {}_fkTranslate -em -p {}_dynamicParent_group".format(pref+elbow_ik_label, pref+elbow_ik_label))
    cmds.delete('pointConstraint {} {}'.format(pref+elbow_ik_label+"_poser", pref+elbow_ik_label+"_fkTranslate"))
    cmds.makeIdentity(apply=True, t=True, r=True, s=True, n=0, "{}_fkTranslate".format(pref+elbow_ik_label))

    cmds.pointConstraint(pref+elbow_ik_label+"_poser", "{}_fkTranslate".format(pref+elbow_ik_label))
    cmds.lockNode("{}_fkTranslate".format(pref+elbow_ik_label), lock=True, lockUnpublished=True)

    # Add attributes for IK FK switching
    cmds.addAttr(ln="{}_ik2fk_script".format(pref+type), dt="string", sn="preferences")
    cmds.addAttr(ln="{}_fk2ik_script".format(pref+type), dt="string", sn="preferences")

    ik2fk_script = ""
    if type == "leg" and cmds.objExists(AdditionalJoints[1]):
        foot_leg_scriptAux = "{{setAttr NAMESPACE{}.rx 0;setAttr NAMESPACE{}.rz 0;setAttr NAMESPACE{}.heelToToes 0;setAttr NAMESPACE{}.toesSide 0;setAttr NAMESPACE{}.heelSide 0;}}".format(AdditionalJoints[4], AdditionalJoints[4], AdditionalJoints[4], AdditionalJoints[4], AdditionalJoints[4])
        ik2fk_script = foot_leg_scriptAux

    ik2fk_script += "{{setAttr NAMESPACE{}.minSquash 1;setAttr NAMESPACE{}.minSquash 1;float $posIK[] = `getAttr NAMESPACE{}_fkTranslateRotate.t`;float $rotIK[] = `xform -q -ws -ro NAMESPACE{}_fkTranslateRotate`;float $posElbow[] = `getAttr NAMESPACE{}_fkTranslate.t`;setAttr NAMESPACE{}.t $posIK[0] $posIK[1] $posIK[2];xform -ws -ro $rotIK[0] $rotIK[1] $rotIK[2] NAMESPACE{};setAttr NAMESPACE{}.t $posElbow[0] $posElbow[1] $posElbow[2];}}".format(pref+arm_ik_label, pref+arm_ik_label, pref+arm_ik_label, pref+arm_ik_label, pref+elbow_ik_label, pref+arm_ik_label, pref+arm_ik_label, pref+elbow_ik_label)

    cmds.setAttr("preferences.{}_ik2fk_script".format(pref+type), ik2fk_script, type="string")
    cmds.setAttr("preferences.{}_ik2fk_script".format(pref+type), lock=True)

    # FK to IK script
    fk2ik_script = ""

    setScaleFactors_script = "{{float $s1[] = `getAttr NAMESPACE{}.s`;float $s2[] = `getAttr NAMESPACE{}.s`;setAttr NAMESPACE{}.scaleFactor1X $s1[0];setAttr NAMESPACE{}.scaleFactor1Y $s1[1];setAttr NAMESPACE{}.scaleFactor2X $s2[0];setAttr NAMESPACE{}.scaleFactor2Y $s2[1];}}".format(chainIK[0], chainIK[1], pref+arm_control_label, pref+arm_control_label, pref+arm_control_label, pref+arm_control_label)

    fk2ik_script += "{{float $rot[] = `getAttr NAMESPACE{}_ikRotate.r`;setAttr NAMESPACE{}.r $rot[0] $rot[1] $rot[2];float $rotY = `getAttr NAMESPACE{}_2_joint.ry`;float $rotYTmp = `getAttr NAMESPACE{}_group.ry`;setAttr NAMESPACE{}.ry ($rotY-$rotYTmp);float $rot[] = `xform -q -ws -ro NAMESPACE{}_ikRotate`;xform -ws -ro $rot[0] $rot[1] $rot[2] NAMESPACE{};}}".format(pref+arm_fk_label, pref+arm_fk_label, pref+elbow_fk_label, pref+elbow_fk_label, pref+elbow_fk_label, pref+hand_fk_label, pref+hand_fk_label)

    fk2ik_script += setScaleFactors_script

    cmds.setAttr("preferences.{}_fk2ik_script".format(pref+type), fk2ik_script, type="string")
    cmds.setAttr("preferences.{}_fk2ik_script".format(pref+type), lock=True)

927 - 1302

def create_finger(pref, finger_type, stretch, stretch_rig_params):
    tuner1_label = finger_type + "1_tuner"
    tuner2_label = finger_type + "2_tuner"
    tuner3_label = finger_type + "3_tuner"
    tuner4_label = finger_type + "4_tuner"

    controls_label = "fingers_controls"
    finger_controls_label = finger_type + "_controls"
    finger_ik_controls_label = finger_type + "IK_controls"
    finger_fk_controls_label = finger_type + "FK_controls"
    finger_control_label = finger_type + "_control"
    finger_joints_label = finger_type + "_joints"
    finger_label = finger_type
    finger_ik_label = finger_type + "IK"
    finger_ik_orientation_label = finger_type + "IKOrientation"
    finger_fk1_label = finger_type + "FK1"
    finger_fk2_label = finger_type + "FK2"
    finger_fk3_label = finger_type + "FK3"
    finger_transform_label = finger_type + "Transform"

    cmds.select(clear=True)

    finger1_pos = cmds.getAttr(pref + tuner1_label + ".worldPosition")[0]
    finger2_pos = cmds.getAttr(pref + tuner2_label + ".worldPosition")[0]
    finger3_pos = cmds.getAttr(pref + tuner3_label + ".worldPosition")[0]
    finger4_pos = cmds.getAttr(pref + tuner4_label + ".worldPosition")[0]

    finger12 = [finger2_pos[i] - finger1_pos[i] for i in range(3)]
    finger23 = [finger3_pos[i] - finger2_pos[i] for i in range(3)]
    finger34 = [finger4_pos[i] - finger3_pos[i] for i in range(3)]

    finger12_mag = sum([x ** 2 for x in finger12]) ** 0.5
    finger23_mag = sum([x ** 2 for x in finger23]) ** 0.5
    finger34_mag = sum([x ** 2 for x in finger34]) ** 0.5

    finger_joints = []

    coeff = 1
    orient = [0, 0, 0]

    if pref == "r_":
        coeff = 1
        orient = [0, 0, 0]

    finger_joints.append(cmds.joint(position=(0, 0, 0), name=pref + finger_label + "1_joint"))
    finger_joints.append(cmds.joint(position=(coeff * finger12_mag, 0, 0), name=pref + finger_label + "2_joint"))
    finger_joints.append(cmds.joint(position=(coeff * (finger12_mag + finger23_mag), 0, 0), name=pref + finger_label + "3_joint"))
    finger_joints.append(cmds.joint(position=(coeff * (finger12_mag + finger23_mag + finger34_mag), 0, 0), name=pref + finger_label + "4_joint"))

    cmds.setAttr(finger_joints[1] + ".preferredAngleZ", -45)

    ik_handle1 = cmds.ikHandle(startJoint=finger_joints[0], endEffector=finger_joints[2], solver="ikRPsolver")[0]
    cmds.xform(ik_handle1, translation=finger1_pos, worldSpace=True)
    cmds.xform(ik_handle1 + '.poleVectorConstraint', finger2_pos)

    ik_handle2 = cmds.ikHandle(startJoint=finger_joints[2], endEffector=finger_joints[3], solver="ikSCsolver")[0]
    cmds.xform(ik_handle2, translation=finger4_pos, worldSpace=True)

    cmds.delete(cmds.orientConstraint(finger_joints[1], ik_handle2))

    cmds.setAttr(finger_joints[2] + ".jointOrient", 0, 0, 0)
    cmds.setAttr(finger_joints[3] + ".jointOrient", 0, 0, 0)

    chain = cmds.duplicate(finger_joints[0], renameChildren=True)
    for i in range(4):
        chain[i] = cmds.rename(chain[i], pref + finger_label + str(i + 1) + "_joint")
        cmds.delete(cmds.orientConstraint(finger_joints[i], chain[i]))

    cmds.delete(cmds.listRelatives(chain[0], allDescendents=True, type='ikEffector'))
    cmds.delete(finger_joints[0])

    cmds.group(name=pref + finger_controls_label, empty=True)
    cmds.group(name=pref + finger_ik_controls_label, empty=True, parent=pref + finger_controls_label)
    cmds.group(name=pref + finger_fk_controls_label, empty=True, parent=pref + finger_controls_label)

    chain_fk = cmds.duplicate(chain[0], renameChildren=True)
    for i in range(3):
        chain_fk[i] = cmds.rename(chain_fk[i], pref + finger_label + "FK" + str(i + 1) + "_joint")

    chain_ik = cmds.duplicate(chain[0], renameChildren=True)
    for i in range(3):
        chain_ik[i] = cmds.rename(chain_ik[i], pref + finger_label + "IK" + str(i + 1) + "_joint")

    chain_no_rotate = cmds.duplicate(chain[0], renameChildren=True)
    cmds.delete(chain_no_rotate[2])

    cmds.parent(cmds.group(name=pref + finger_joints_label, *chain, *chain_ik, *chain_fk, *chain_no_rotate), world=True)

    finger_transform_group = cmds.group(name=pref + finger_transform_label + "_group", empty=True, parent=pref + finger_controls_label)
    finger_transform = cmds.group(name=pref + finger_transform_label, empty=True, parent=finger_transform_group)

    cmds.parentConstraint(pref + finger_joints_label, finger_transform_group)
    cmds.delete(cmds.pointConstraint(pref + finger_joints_label, finger_transform))
    cmds.makeIdentity(finger_transform, apply=True, translate=True, rotate=True, scale=True, normal=False)
    cmds.pointConstraint(finger_transform, pref + finger_joints_label)

    cmds.setAttr(chain_ik[0] + ".visibility", False)
    cmds.setAttr(chain_fk[0] + ".visibility", False)
    cmds.setAttr(chain_no_rotate[0] + ".visibility", False)

    cmds.group(name=pref + finger_control_label, empty=True, parent=pref + finger_controls_label)
    cmds.parentConstraint(chain[0], pref + finger_control_label)

    cmds.addAttr(pref + finger_control_label, longName="kinematic", attributeType="double", min=0, max=1, defaultValue=1, keyable=True)

    plus = connect_10_01(pref + finger_control_label + ".kinematic", [pref + finger_ik_controls_label + ".visibility"], [pref + finger_fk_controls_label + ".visibility"])

    for i in range(3):
        oc = cmds.orientConstraint(chain_ik[i], chain_fk[i], chain[i])[0]
        cmds.setAttr(oc + ".interpType", 0)

        cmds.connectAttr(plus + ".output2Dx", oc + "." + chain_ik[i] + "W0")
        cmds.connectAttr(plus + ".output2Dy", oc + "." + chain_fk[i] + "W1")

    ik_handle_no_rotate = cmds.ikHandle(name=pref + finger_label + "NoRotate_IKHandle", startJoint=chain_no_rotate[0], endEffector=chain_no_rotate[1], solver="ikSCsolver")[0]
    cmds.pointConstraint(chain[1], ik_handle_no_rotate)
    cmds.parent(ik_handle_no_rotate, pref + finger_joints_label)

    cmds.setAttr(ik_handle_no_rotate + ".visibility", False)
    cmds.lockNode(ik_handle_no_rotate, lock=True)

    cmds.ikHandle(name=pref + finger_label + "IK_IKHandle", startJoint=chain_ik[0], endEffector=chain_ik[2], solver="ikRPsolver")
    cmds.parent(ik_handle_no_rotate, pref + finger_joints_label)

    cmds.setAttr(ik_handle_no_rotate + ".visibility", False)
    cmds.lockNode(ik_handle_no_rotate, lock=True)

    cmds.group(name=pref + finger_ik_label + "_group", empty=True, parent=pref + finger_ik_controls_label)
    cmds.group(name=pref + finger_ik_label, empty=True, parent=pref + finger_ik_label + "_group")
    cmds.xform(pref + finger_ik_label, translation=finger4_pos)
    cmds.makeIdentity(pref + finger_ik_label, apply=True, translate=True, rotate=True, scale=True, normal=False)

    grp = cmds.group(empty=True, name=pref + finger_ik_orientation_label + "_poser", parent=chain_fk[1])
    cmds.setAttr(grp + ".translateY", (finger12_mag + finger23_mag + finger34_mag) / 2.0)
    cmds.lockNode(grp, lock=True)

    cmds.group(name=pref + finger_ik_orientation_label + "_group", empty=True, parent=pref + finger_ik_controls_label)
    cmds.group(name=pref + finger_ik_orientation_label, empty=True, parent=pref + finger_ik_orientation_label + "_group")
    cmds.delete(cmds.pointConstraint(pref + finger_ik_orientation_label + "_poser", pref + finger_ik_orientation_label))
    cmds.lockNode(pref + finger_ik_orientation_label, lock=True)


def create_hand(pref, fingers, num_controls, stretchable):
    hand1_tuner_label = "hand_tuner"
    hand2_tuner_label = "hand2_tuner"
    joints_label = "hand_joints"
    palm_label = "palm"

    cmds.select(clear=True)
    hand1_pos = cmds.getAttr("{}.worldPosition".format(pref + hand1_tuner_label))[0]
    hand2_pos = cmds.getAttr("{}.worldPosition".format(pref + hand2_tuner_label))[0]

    hand_vec = [hand2_pos[0] - hand1_pos[0], hand2_pos[1] - hand1_pos[1], hand2_pos[2] - hand1_pos[2]]
    mag_hand_vec = sum(v * v for v in hand_vec) ** 0.5

    hand_joints = []
    coeff = 1
    orient = [0, 0, 0]

    if pref == "r_":
        coeff = 1
        orient = [0, 0, 0]

    hand_joints.append(cmds.joint(position=[0, 0, 0], name="{}hand1_joint".format(pref)))
    hand_joints.append(cmds.joint(position=[coeff * mag_hand_vec, 0, 0], name="{}hand2_joint".format(pref)))
    cmds.setAttr(hand_joints[0] + ".jointOrient", orient[0], orient[1], orient[2], type="double3")

    ik_handle = cmds.ikHandle(startJoint=hand_joints[0], endEffector=hand_joints[1], solver="ikSCsolver")[0]
    cmds.xform(ik_handle, translation=hand1_pos, worldSpace=True)
    cmds.xform(hand_joints[1], translation=hand2_pos, worldSpace=True)
    cmds.delete(cmds.orientConstraint("{}{}".format(pref, hand2_tuner_label), ik_handle))

    joints = cmds.duplicate(hand_joints[0], renameChildren=True)
    for i in range(2):
        joints[i] = cmds.rename(joints[i], "{}hand{}_joint".format(pref, i + 1))
        cmds.orientConstraint(hand_joints[i], joints[i])

    cmds.delete(cmds.listRelatives(joints[0], allDescendents=True, type='ikEffector'))
    cmds.delete(hand_joints[0])

    palm_group = cmds.group(empty=True, name="{}{}_group".format(pref, palm_label), parent="other_controls")
    palm = cmds.group(empty=True, name="{}{}".format(pref, palm_label), parent=palm_group)

    cmds.parentConstraint(joints[1], palm_group, delete=True)
    cmds.parentConstraint(hand_joints[0], palm_group, maintainOffset=True)
    cmds.orientConstraint(palm, joints[1])

    color = 7
    if pref == "r_":
        color = 6

    create_control("circle", [palm, palm], [0.4, color, 0], "fingers")

    group = cmds.group(joints[0], name="{}{}".format(pref, joints_label), parent="skeleton")
    cmds.sets(joints[0], add="bindJointsSet")
    lock_attrs("{}{}".format(pref, joints_label), [1, 1, 1], [1, 1, 1], [1, 1, 1], 1)
    lock_attrs("{}{}_group".format(pref, palm_label), [1, 1, 1], [1, 1, 1], [1, 1, 1], 1)
    lock_attrs("{}{}".format(pref, palm_label), [1, 1, 1], [0, 0, 0], [1, 1, 1], 1)

    if fingers[0]:
        create_finger(pref, "thumbFinger", stretchable, num_controls)
    if fingers[1]:
        create_finger(pref, "indexFinger", stretchable, num_controls)
    if fingers[2]:
        create_finger(pref, "middleFinger", stretchable, num_controls)
    if fingers[3]:
        create_finger(pref, "ringFinger", stretchable, num_controls)
    if fingers[4]:
        create_finger(pref, "pinkyFinger", stretchable, num_controls)


def create_foot(pref):
    foot1_tuner_label = "foot1_tuner"
    foot2_tuner_label = "foot2_tuner"
    heel_tuner_label = "heel_tuner"
    toe_tuner_label = "toe_tuner"
    side1_tuner_label = "foot_side1_tuner"
    side2_tuner_label = "foot_side2_tuner"
    controls_label = "foot_controls"
    joints_label = "foot_joints"
    foot_label = "foot"
    toes_label = "toes"

    foot1_pos = cmds.getAttr("{}.worldPosition".format(pref + foot1_tuner_label))[0]
    foot2_pos = cmds.getAttr("{}.worldPosition".format(pref + foot2_tuner_label))[0]
    heel_pos = cmds.getAttr("{}.worldPosition".format(pref + heel_tuner_label))[0]
    toe_pos = cmds.getAttr("{}.worldPosition".format(pref + toe_tuner_label))[0]
    side1_pos = cmds.getAttr("{}.worldPosition".format(pref + side1_tuner_label))[0]
    side2_pos = cmds.getAttr("{}.worldPosition".format(pref + side2_tuner_label))[0]

    joints_group = cmds.group(empty=True, name="{}{}".format(pref, joints_label), parent="skeleton")
    tmp_group = cmds.group(empty=True)
    cmds.parentConstraint("{}{}".format(pref, foot1_tuner_label), tmp_group)

    joints_aux = []
    joints_aux.append(cmds.joint(position=foot1_pos, name="{}footAux1_joint".format(pref), parent=tmp_group))
    joints_aux.append(cmds.joint(position=heel_pos, name="{}footAux2_joint".format(pref), parent=joints_aux[0]))
    joints_aux.append(cmds.joint(position=foot2_pos, name="{}footAux3_joint".format(pref), parent=joints_aux[1]))
    joints_aux.append(cmds.joint(position=side2_pos, name="{}footAux4_joint".format(pref), parent=joints_aux[2]))
    joints_aux.append(cmds.joint(position=side1_pos, name="{}footAux5_joint".format(pref), parent=joints_aux[3]))
    joints_aux.append(cmds.joint(position=foot2_pos, name="{}footAux6_joint".format(pref), parent=joints_aux[4]))
    joints_aux.append(cmds.joint(position=toe_pos, name="{}footAux7_joint".format(pref), parent=joints_aux[5]))
    joints_aux.append(cmds.joint(position=foot2_pos, name="{}footAux8_joint".format(pref), parent=joints_aux[6]))
    joints_aux.append(cmds.joint(position=foot1_pos, name="{}footAux9_joint".format(pref), parent=joints_aux[7]))
    joints_aux.append(cmds.joint(position=foot2_pos, name="{}footAux10_joint".format(pref), parent=joints_aux[6]))
    joints_aux.append(cmds.joint(position=toe_pos, name="{}footAux11_joint".format(pref), parent=joints_aux[9]))

    joints = []
    joints.append(cmds.joint(position=foot1_pos, name="{}foot1_joint".format(pref), parent=tmp_group))
    joints.append(cmds.joint(position=foot2_pos, name="{}foot2_joint".format(pref), parent=joints[0]))
    joints.append(cmds.joint(position=toe_pos, name="{}foot3_joint".format(pref), parent=joints[1]))

    cmds.delete(tmp_group)

    ik1_handle = cmds.ikHandle(startJoint=joints[0], endEffector=joints[1], solver="ikSCsolver")[0]
    ik2_handle = cmds.ikHandle(startJoint=joints[1], endEffector=joints[2], solver="ikSCsolver")[0]

    cmds.parent(ik1_handle, joints_group)
    cmds.parent(ik2_handle, joints_group)
    cmds.setAttr(ik1_handle + ".v", False)
    cmds.setAttr(ik2_handle + ".v", False)

    cmds.parentConstraint(joints_aux[8], ik1_handle, maintainOffset=True)
    cmds.parentConstraint(joints_aux[10], ik2_handle, maintainOffset=True)
    cmds.setAttr(joints_aux[0] + ".v", False)

    controls_group = cmds.group(empty=True, name="{}{}".format(pref, controls_label), parent="controls")
    foot_group = cmds.group(empty=True, name="{}{}_group".format(pref, foot_label), parent=controls_group)
    foot = cmds.group(empty=True, name="{}{}".format(pref, foot_label), parent=foot_group)

    cmds.addAttr(foot, longName="heelToToes", attributeType="double", minValue=0, maxValue=1, defaultValue=0,
                 keyable=True)
    cmds.addAttr(foot, longName="toesSide", attributeType="double", defaultValue=0, keyable=True)
    cmds.addAttr(foot, longName="toesTwist", attributeType="double", defaultValue=0, keyable=True)

    lock_attrs("{}{}".format(pref, foot_label), [1, 1, 1], [0, 0, 0], [1, 1, 1], 1)
    lock_attrs("{}{}_group".format(pref, foot_label), [1, 1, 1], [1, 1, 1], [1, 1, 1], 1)
    lock_attrs("{}{}".format(pref, controls_label), [1, 1, 1], [1, 1, 1], [1, 1, 1], 1)

    for jnt in joints:
        cmds.sets(jnt, add="bindJointsSet")
        lock_attrs("{}{}".format(pref, joints_label), [1, 1, 1], [1, 1, 1], [1, 1, 1], 1)

    toes = cmds.group(empty=True, name="{}{}_group".format(pref, toes_label), parent=foot_group)
    cmds.parentConstraint(joints[2], toes, maintainOffset=True)

    cmds.setAttr(joints[2] + ".v", False)
    create_control("circle", [toes, toes], [0.2, 17, 0], "toesIn")

    return foot

def create_body(num_joints):
    # Labels
    controls_label = "body_controls"
    joints_label = "body_joints"
    pelvis_label = "pelvis"
    spine_label = "spine"
    hip_label = "hip"
    chest_label = "chest"
    body_label = "body"

    # Get positions
    pelvis_pos = cmds.getAttr("pelvis_tuner.worldPosition")[0]
    spine_pos = cmds.getAttr("spine_tuner.worldPosition")[0]
    chest_pos = cmds.getAttr("chest_tuner.worldPosition")[0]
    clavicle_pos = cmds.getAttr("clavicle_tuner.worldPosition")[0]

    cmds.select(cl=True)

    # Create joints
    group_joints = cmds.group(em=True, name=joints_label, p="skeleton")
    joints = []

    joints.append(cmds.joint(p=pelvis_pos, n="{}_1_joint".format(body_label), parent=group_joints))
    joints.append(cmds.joint(p=spine_pos, n="{}_2_joint".format(body_label), parent=joints[0]))
    joints.append(cmds.joint(p=chest_pos, n="{}_3_joint".format(body_label), parent=joints[1]))
    joints.append(cmds.joint(p=clavicle_pos, n="{}_4_joint".format(body_label), parent=joints[2]))

    clavicle_joint = cmds.joint(p=clavicle_pos, radius=2, n="clavicle_joint", parent=joints_label)
    hip_joint = cmds.joint(p=pelvis_pos, radius=2, n="hip_joint", parent=joints_label)

    # Joint settings
    for joint in joints:
        cmds.joint(joint, e=True, zso=True, oj="xyz", sao="yup")

    cmds.setAttr("{}.v".format(joints[0]), False)
    cmds.lockNode(joints[0], lock=True)

    # Controls group
    group_controls = cmds.group(em=True, name=controls_label, p="controls")

    # Pelvis
    pelvis_group = cmds.group(em=True, name="{}_group".format(pelvis_label), p=group_controls)
    pelvis = cmds.group(em=True, name=pelvis_label, p=pelvis_group)
    cmds.setAttr("{}.rotateOrder".format(pelvis), 3)

    cmds.delete(cmds.pointConstraint(joints[0], pelvis_group))
    cmds.delete(cmds.orientConstraint(hip_joint, pelvis_group))

    cmds.pointConstraint(pelvis, joints[0])
    cmds.orientConstraint(pelvis, joints[0])

    # Spine
    spine = cmds.group(em=True, name=spine_label, p=pelvis)
    cmds.setAttr("{}.rotateOrder".format(spine), 3)

    cmds.delete(cmds.pointConstraint(joints[1], spine))
    cmds.makeIdentity(spine, apply=True, t=True, r=True, s=True, n=0)
    cmds.pointConstraint(joints[1], spine)

    cmds.orientConstraint(spine, joints[1])

    group1 = cmds.group(em=True, name="{}_Rotate1".format(chest_label), p=spine)
    group2 = cmds.group(em=True, name="{}_Rotate2".format(chest_label), p=spine)
    group3 = cmds.group(em=True, name="{}_Rotate3".format(chest_label), p=spine)

    cmds.connectAttr("{}.r".format(spine), "{}.r".format(group2))
    cmds.addAttr(spine, ln="{}RotateFactor".format(chest_label), at="double", min=0, max=1, dv=1, k=True)
    oc = cmds.orientConstraint(group1, group2, group3)
    cmds.setAttr("{}.interpType".format(oc[0]), 2)

    cmds.connectAttr("{}.{}RotateFactor".format(spine, chest_label), "{}.{}W0".format(oc[0], group1))
    cmds.connectAttr("{}.{}RotateFactor".format(spine, chest_label), "{}.{}W1".format(oc[0], group2))

    # Hip
    hip = cmds.group(em=True, name=hip_label, p=pelvis)
    cmds.delete(cmds.pointConstraint(joints[0], hip))
    cmds.makeIdentity(hip, apply=True, t=True, r=True, s=True, n=0)

    # Chest
    chest_group = cmds.group(em=True, name="{}_group".format(chest_label), p=pelvis)
    chest = cmds.group(em=True, name=chest_label, p=chest_group)
    cmds.setAttr("{}.rotateOrder".format(chest), 3)

    cmds.delete(cmds.pointConstraint(joints[2], chest_group))
    cmds.makeIdentity(chest_group, apply=True, t=True, r=True, s=True, n=0)

    cmds.pointConstraint(joints[2], chest_group)
    cmds.orientConstraint(group3, chest_group)

    # Spline IK handle
    base_name = "{}_stretch".format(body_label)
    pelvis_spine_vec = [spine_pos[i] - pelvis_pos[i] for i in range(3)]
    spine_chest_vec = [chest_pos[i] - spine_pos[i] for i in range(3)]
    chest_clavicle_vec = [clavicle_pos[i] - chest_pos[i] for i in range(3)]

    pelvis_spine_mag = cmds.mag(pelvis_spine_vec)
    spine_chest_mag = cmds.mag(spine_chest_vec)
    chest_clavicle_mag = cmds.mag(chest_clavicle_vec)

    pelvis_joints = []
    spine_joints = []
    chest_joints = []
    index = 1

    cmds.select(cl=True)
    for i in range(num_joints[0]):
        pelvis_joints.append(cmds.joint(r=True, p=(pelvis_spine_mag / num_joints[0], 0, 0),
                                        n="{}_{}_joint".format(base_name, index)))
        cmds.delete(cmds.parentConstraint("{}_1_joint".format(body_label), pelvis_joints[0]))
        index += 1

    cmds.select(cl=True)
    for i in range(num_joints[1]):
        spine_joints.append(cmds.joint(r=True, p=(spine_chest_mag / num_joints[1], 0, 0),
                                       n="{}_{}_joint".format(base_name, index)))
        cmds.delete(cmds.parentConstraint("{}_2_joint".format(body_label), spine_joints[0]))
        index += 1

    cmds.select(cl=True)
    for i in range(num_joints[2] + 1):
        chest_joints.append(cmds.joint(r=True, p=(chest_clavicle_mag / num_joints[2], 0, 0),
                                       n="{}_{}_joint".format(base_name, index)))
        cmds.delete(cmds.parentConstraint("{}_3_joint".format(body_label), chest_joints[0]))
        index += 1

    cmds.parent(pelvis_joints[0], joints_label)
    cmds.parent(spine_joints[0], pelvis_joints[num_joints[0] - 1])
    cmds.parent(chest_joints[0], spine_joints[num_joints[1] - 1])

    cmds.parentConstraint(hip, hip_joint, mo=True)
    cmds.parentConstraint(chest, clavicle_joint, mo=True)

    # IK handle
    ik_handle = cmds.ikHandle(solver="ikSplineSolver", n="{}_IKHandle".format(base_name), ccv=True, pcv=True,
                              sj=pelvis_joints[0], ee=chest_joints[num_joints[2]])
    cmds.parent(ik_handle[0], joints_label)
    ik_curve = cmds.rename(ik_handle[2], "{}_curve".format(base_name))

    cmds.setAttr("{}.v".format(ik_handle[0]), False)
    cmds.setAttr("{}.v".format(ik_curve), False)
    cmds.lockNode(ik_curve, lock=True)

    # Spline IK twist setup
    start_twist = cmds.group(em=True, n="{}_startTwist".format(base_name), p=joints_label)
    end_twist = cmds.group(em=True, n="{}_endTwist".format(base_name), p=joints_label)

    cmds.parentConstraint(spine, start_twist)
    cmds.parentConstraint(chest, end_twist)

    cmds.lockNode(start_twist, lock=True)
    cmds.lockNode(end_twist, lock=True)

    cmds.setAttr("{}.dTwistControlEnable".format(ik_handle[0]), 1)
    cmds.setAttr("{}.dWorldUpAxis".format(ik_handle[0]), 3)
    cmds.setAttr("{}.dWorldUpType".format(ik_handle[0]), 4)
    cmds.setAttr("{}.dWorldUpVector".format(ik_handle[0]), 0, 0, 1)
    cmds.setAttr("{}.dWorldUpVectorEnd".format(ik_handle[0]), 0, 0, 1)

    cmds.connectAttr("{}.worldMatrix".format(start_twist), "{}.dWorldUpMatrix".format(ik_handle[0]))
    cmds.connectAttr("{}.worldMatrix".format(end_twist), "{}.dWorldUpMatrixEnd".format(ik_handle[0]))

    # Lattice deformation
    lattice = cmds.lattice(en=True, divisons=(2, 2, 2), n="{}_lattice".format(base_name), objectCentered=True)[0]
    cluster1 = cmds.cluster(lattice + ".pt[0:2][0]", n="{}_cluster1".format(base_name))[1]
    cluster2 = cmds.cluster(lattice + ".pt[0:2][2]", n="{}_cluster2".format(base_name))[1]

    cmds.setAttr("{}.visibility".format(lattice), False)

    cmds.parent(lattice, joints_label)
    cmds.parent(cluster1, joints_label)
    cmds.parent(cluster2, joints_label)

    cmds.lockNode(lattice, lock=True)
    cmds.lockNode(cluster1, lock=True)
    cmds.lockNode(cluster2, lock=True)

    # Custom attributes
    cmds.addAttr(pelvis, ln="ikBlend", at="double", min=0, max=1, dv=0, k=True)
    cmds.addAttr(pelvis, ln="stretch", at="double", min=0, max=1, dv=0, k=True)
    cmds.addAttr(pelvis, ln="stretchFactor", at="double", min=0, max=1, dv=1, k=True)

    cmds.addAttr(spine, ln="stretch", at="double", min=0, max=1, dv=0, k=True)
    cmds.addAttr(spine, ln="stretchFactor", at="double", min=0, max=1, dv=1, k=True)

    cmds.addAttr(chest, ln="stretch", at="double", min=0, max=1, dv=0, k=True)
    cmds.addAttr(chest, ln="stretchFactor", at="double", min=0, max=1, dv=1, k=True)

    cmds.addAttr(hip, ln="stretch", at="double", min=0, max=1, dv=0, k=True)
    cmds.addAttr(hip, ln="stretchFactor", at="double", min=0, max=1, dv=1, k=True)

    # Lock attributes
    for node in [pelvis, hip, spine, chest, clavicle_joint, hip_joint]:
        cmds.setAttr("{}.tx".format(node), lock=True)
        cmds.setAttr("{}.ty".format(node), lock=True)
        cmds.setAttr("{}.tz".format(node), lock=True)

        cmds.setAttr("{}.rx".format(node), lock=True)
        cmds.setAttr("{}.ry".format(node), lock=True)
        cmds.setAttr("{}.rz".format(node), lock=True)

        cmds.setAttr("{}.sx".format(node), lock=True)
        cmds.setAttr("{}.sy".format(node), lock=True)
        cmds.setAttr("{}.sz".format(node), lock=True)

        cmds.setAttr("{}.visibility".format(node), lock=True)

    # Bind joints set
    bind_joints_set = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, n="bindJointsSet")
    cmds.sets(bind_joints_set, e=True, add="{}_1_joint".format(body_label))
    cmds.sets(bind_joints_set, e=True, add="{}_2_joint".format(body_label))
    cmds.sets(bind_joints_set, e=True, add="{}_3_joint".format(body_label))
    cmds.sets(bind_joints_set, e=True, add="{}_4_joint".format(body_label))

    cmds.sets(bind_joints_set, e=True, lock=True)
    return joints[0], pelvis, spine, chest, clavicle_joint, hip_joint


def create_head(neck_stretch_rig_params, head_stretch_rig_params):
    # Labels
    head_label = "head"
    head_stretch_label = "headStretch"
    neck_label = "neck"
    controls_label = "head_controls"
    additional_joints = ["clavicle_joint"]

    # Get positions
    neck_pos = cmds.getAttr("neck_tuner.worldPosition")[0]
    head_pos = cmds.getAttr("head_tuner.worldPosition")[0]
    head_end_pos = cmds.getAttr("head_end_tuner.worldPosition")[0]

    cmds.select(cl=True)

    joints = []

    # Check existence of additional joint
    if not cmds.objExists(additional_joints[0]):
        cmds.warning("createHead: cannot create head. Cannot find '{}'".format(additional_joints[0]))
        return

    # Create joints
    joints.append(cmds.joint(p=neck_pos, n="neck_joint", additional_joints[0]))
    joints.append(cmds.joint(p=head_pos, n="head_joint", joints[0]))
    joints.append(cmds.joint(p=head_end_pos, n="head_end_joint", joints[1]))

    # Joint settings
    for i in range(3):
        cmds.joint(joints[i], e=True, zso=True, oj="xyz", sao="yup")

    # Controls group
    cmds.group(em=True, name=controls_label, p="controls")

    # Neck
    neck_group = cmds.group(em=True, name=neck_label+"_group", p=controls_label)
    cmds.group(em=True, name=neck_label, p=neck_group)
    cmds.setAttr(neck_label+".rotateOrder", 3)

    cmds.pointConstraint(joints[0], neck_group)
    cmds.orientConstraint(additional_joints[0], neck_group)
    cmds.orientConstraint(neck_label, joints[0])

    # Head
    head_dyn_group = cmds.group(em=True, name=head_label+"_dynamicParent_group", p=controls_label)
    head_group = cmds.group(em=True, name=head_label+"_group", p=head_dyn_group)
    cmds.group(em=True, name=head_label+"_dynamicParentPoser", p=head_group)
    cmds.group(em=True, name=head_label, p=head_group)
    cmds.setAttr(head_label+".rotateOrder", 3)

    cmds.connectAttr(head_label+".rotateOrder", head_label+"_dynamicParentPoser.rotateOrder")

    pc_head_group = cmds.pointConstraint(joints[1], head_group)
    cmds.disconnectAttr(pc_head_group[0]+".constraintTranslateX", head_group+".tx")
    cmds.disconnectAttr(pc_head_group[0]+".constraintTranslateY", head_group+".ty")
    cmds.disconnectAttr(pc_head_group[0]+".constraintTranslateZ", head_group+".tz")

    plus = cmds.createNode("plusMinusAverage", n=head_group+"_ty_plusMinusAverage")
    cmds.setAttr(plus+".operation", 2)
    cmds.connectAttr(pc_head_group[0]+".constraintTranslate", plus+".input3D[0]")
    cmds.connectAttr(head_label+".t", plus+".input3D[1]")
    cmds.connectAttr(plus+".output3D", head_group+".t")

    cmds.delete(cmds.orientConstraint(additional_joints[0], head_group))

    cmds.group(em=True, name=joints[0]+"_NoScaleMatrix", p=additional_joints[0])
    cmds.setAttr(joints[0]+"_NoScaleMatrix.inheritsTransform", False)

    cmds.parentConstraint(joints[0], joints[0]+"_NoScaleMatrix")
    cmds.lockNode(joints[0]+"_NoScaleMatrix", l=True)

    oc = cmds.orientConstraint(head_label, joints[1])
    cmds.connectAttr(joints[0]+"_NoScaleMatrix.inverseMatrix", oc[0]+".constraintParentInverseMatrix")

    # Stretch Rig for Neck
    if len(neck_stretch_rig_params) == 2:
        constraints = [joints[0]]
        if len(head_stretch_rig_params) != 2:
            for i in range(1, neck_stretch_rig_params[1]-1):
                constraints.append("")
            constraints.append(joints[1])
        create_stretch_rig([neck_stretch_rig_params[0], neck_stretch_rig_params[1]], neck_label+"_stretchRig",
                           [joints[0], joints[1]], [joints[0], joints[1]], constraints, additional_joints[0])
    else:
        cmds.sets("bindJointsSet", e=True, add=joints[0])

    # Stretch Rig for Head
    if len(head_stretch_rig_params) == 2:
        constraint = [""]
        if len(neck_stretch_rig_params) == 2:
            constraint = [neck_label+"_stretchRig_control"+str(neck_stretch_rig_params[1])]
        else:
            constraint = [joints[1]]
        create_stretch_rig([head_stretch_rig_params[0], head_stretch_rig_params[1]], head_label+"_stretchRig",
                           [joints[1], joints[2]], [joints[1], joints[2]], constraint, additional_joints[0])
    else:
        cmds.sets("bindJointsSet", e=True, add=joints[1])

    # Head Stretch on Neck
    head_stretch_group = cmds.group(em=True, name=head_stretch_label+"_group", p=head_label)
    cmds.group(em=True, name=head_stretch_label, p=head_stretch_group)
    pc = cmds.pointConstraint(joints[2], head_stretch_group)
    cmds.disconnectAttr(pc[0]+".constraintTranslateX", head_stretch_group+".tx")
    cmds.disconnectAttr(pc[0]+".constraintTranslateY", head_stretch_group+".ty")
    cmds.disconnectAttr(pc[0]+".constraintTranslateZ", head_stretch_group+".tz")

    plus = cmds.createNode("plusMinusAverage", n=head_stretch_group+"_ty_plusMinusAverage")
    cmds.setAttr(plus+".operation", 2)
    cmds.connectAttr(pc[0]+".constraintTranslate", plus+".input3D[0]")
    cmds.connectAttr(head_stretch_label+".t", plus+".input3D[1]")
    cmds.connectAttr(plus+".output3D", head_stretch_group+".t")

    cmds.addAttr(head_stretch_label, ln="scaleFactor", at="double", min=0.1, max=2, dv=1, k=True)

    mult = cmds.createNode("multiplyDivide", n=head_stretch_label+"_stretch_multiplyDivide")
    cmds.setAttr(mult+".operation", 2)
    cmds.setAttr(mult+".input1Y", 1)
    cmds.connectAttr(head_stretch_label+".scaleFactor", mult+".input1X")
    cmds.connectAttr(head_stretch_label+".scaleFactor", mult+".input2Y")

    b = cmds.createNode("blendTwoAttr", n=joints[2]+"_saveVolume_blendTwoAttr")
    cmds.setAttr(b+".i[0]", 1)
    cmds.connectAttr(mult+".outputY", b+".i[1]")
    cmds.connectAttr(head_stretch_label+".saveVolume", b+".attributesBlender")

    cmds.connectAttr(mult+".outputX", joints[1]+".sx")
    cmds.connectAttr(b+".output", joints[1]+".sy")
    cmds.connectAttr(b+".output", joints[1]+".sz")

    # Head Stretch on Neck
    cmds.addAttr(head_label, ln="scaleFactor", at="double", min=0.1, max=2, dv=1, k=True)

    mult = cmds.createNode("multiplyDivide", n=head_label+"_stretch_multiplyDivide")
    cmds.setAttr(mult+".operation", 2)
    cmds.setAttr(mult+".input1Y", 1)
    cmds.connectAttr(head_label+".scaleFactor", mult+".input1X")
    cmds.connectAttr(head_label+".scaleFactor", mult+".input2Y")

    b = cmds.createNode("blendTwoAttr", n=joints[0]+"_saveVolume_blendTwoAttr")
    cmds.setAttr(b+".i[0]", 1)
    cmds.connectAttr(mult+".outputY", b+".i[1]")
    cmds.connectAttr(head_label+".saveVolume", b+".attributesBlender")

    cmds.connectAttr(mult+".outputX", joints[0]+".sx")
    cmds.connectAttr(b+".output", joints[0]+".sy")
    cmds.connectAttr(b+".output", joints[0]+".sz")

    # Dynamic Parent
    dyn_parents = [neck_label+"="+neck_label]
    if cmds.objExists("hip_joint"):
        dyn_parents.append("pelvis=hip_joint")
    if len(dyn_parents) > 0:
        make_dynamic_parent(head_label, head_dyn_group, dyn_parents)

    # Create Controls
    create_control("circle", [neck_label, neck_label], [0.7, 8, 1], "body")
    create_control("circle", [head_label, head_label], [1.5, 8, 1], "body")
    create_control("circle", [head_stretch_label, head_stretch_label], [1.0, 8, 1], "body")

    # Lock Attributes
    lock_attrs(controls_label, [1, 1, 1], [1, 1, 1], [1, 1, 1], True)
    lock_attrs(neck_group, [1, 1, 1], [1, 1, 1], [1, 1, 1], True)
    lock_attrs(neck_label, [1, 1, 1], [0, 0, 0], [1, 1, 1], True)
    lock_attrs(head_dyn_group, [1, 1, 1], [1, 1, 1], [1, 1, 1], True)
    lock_attrs(head_group, [1, 1, 1], [1, 1, 1], [1, 1, 1], True)
    lock_attrs(head_label+"_dynamicParentPoser", [0, 0, 0], [0, 0, 0], [1, 1, 1], True)
    lock_attrs(head_label, [1, 1, 1], [0, 0, 0], [1, 1, 1], True)
    lock_attrs(head_stretch_label+"_group", [1, 1, 1], [1, 1, 1], [1, 1, 1], True)
    lock_attrs(head_stretch_label, [1, 1, 1], [1, 1, 1], [1, 1, 1], True)


def create_shoulder(pref, stretch_rig):
    shoulder_tuner_label = "shoulder_tuner"
    arm_tuner_label = "arm_tuner"
    joints_label = "shoulder_joints"
    controls_label = "shoulder_controls"
    shoulder_label = "shoulder"
    additional_joints = ["clavicle_joint"]

    shoulder_pos = cmds.getAttr(pref + shoulder_tuner_label + ".worldPosition")[0]
    arm_pos = cmds.getAttr(pref + arm_tuner_label + ".worldPosition")[0]

    shoulder_vec = [arm_pos[0] - shoulder_pos[0], arm_pos[1] - shoulder_pos[1], arm_pos[2] - shoulder_pos[2]]
    mag_shoulder = cmds.math.sqrt(sum(map(lambda x: x * x, shoulder_vec)))

    joints_group = cmds.group(em=True, n=pref + joints_label, p="skeleton")
    cmds.select(cl=True)

    build_joints = []
    coeff = 1
    orient = [0, 0, 0]

    if pref == "r_":
        coeff = -1
        orient = [180, 0, 0]

    build_joints.append(cmds.joint(p=[0, 0, 0], n=pref + shoulder_label + "1_joint"))
    build_joints.append(cmds.joint(p=[coeff * mag_shoulder, 0, 0], n=pref + shoulder_label + "2_joint", parent=build_joints[0]))
    cmds.setAttr(build_joints[0] + ".jointOrient", orient[0], orient[1], orient[2])

    ik_handle = cmds.ikHandle(sj=build_joints[0], ee=build_joints[1], solver="ikSCsolver")[0]
    cmds.delete(cmds.pointConstraint(pref + shoulder_tuner_label, build_joints[0]))
    cmds.xform(ik_handle, ws=True, t=arm_pos)
    cmds.delete(cmds.orientConstraint(pref + shoulder_tuner_label, ik_handle))

    joints = []
    joints.append(cmds.joint(p=[0, 0, 0], n=pref + shoulder_label + "1_joint", parent=joints_group))
    joints.append(cmds.joint(p=[coeff * mag_shoulder / 2, 0, 0], n=pref + shoulder_label + "2_joint", parent=joints[0]))
    joints.append(cmds.joint(p=[coeff * mag_shoulder, 0, 0], n=pref + shoulder_label + "3_joint", parent=joints[1]))
    cmds.setAttr(joints[0] + ".jointOrient", orient[0], orient[1], orient[2])

    cmds.delete(cmds.parentConstraint(build_joints[0], joints_group))
    cmds.delete(build_joints[0])

    controls_group = cmds.group(em=True, n=pref + controls_label, p="controls")
    shoulder_group = cmds.group(em=True, n=pref + shoulder_label + "_group", p=controls_group)
    shoulder = cmds.group(em=True, n=pref + shoulder_label, p=shoulder_group)
    cmds.delete(cmds.parentConstraint(joints_group, shoulder_group))

    cmds.pointConstraint(joints[0], shoulder_group)
    cmds.orientConstraint(shoulder, joints[0])

    cmds.addAttr(shoulder, ln="rotateFactor", at="double", min=0, max=1, dv=0.3, k=True)

    group1 = cmds.group(em=True, n=joints[1] + "Rotate1", p=joints[0])
    group2 = cmds.group(em=True, n=joints[1] + "Rotate2", p=joints[0])
    group3 = cmds.group(em=True, n=joints[1] + "Rotate3", p=joints[0])

    cmds.connectAttr(joints[0] + ".rotate", group2 + ".rotate")
    oc = cmds.orientConstraint(group1, group2, group3, mo=True)
    cmds.setAttr(oc[0] + ".interpType", 2)

    cmds.connectAttr(group3 + ".rotate", joints[1] + ".rotate")
    cmds.connectAttr(shoulder + ".rotateFactor", oc[0] + "." + group1 + "W0")
    cmds.connectAttr(shoulder + ".rotateFactor", oc[0] + "." + group2 + "W1")

    if cmds.objExists(additional_joints[0]):
        cmds.xform(additional_joints[0], pivots=True, ws=True, rp=joints_group)
        pc = cmds.parentConstraint(additional_joints[0], joints_group, mo=True)
        cmds.disconnectAttr(additional_joints[0] + ".scale", pc[0] + ".target[0].targetScale")
        cmds.orientConstraint(additional_joints[0], shoulder_group, mo=True)

    if stretch_rig:
        cmds.setAttr(joints[0] + ".v", False)
        create_stretch_rig([2, 2], pref + shoulder_label + "1_stretchRig", [joints[0], joints[1]], [joints[0], joints[1]], [joints[0]], joints_group)
        create_stretch_rig([2, 2], pref + shoulder_label + "2_stretchRig", [joints[1], joints[2]], [joints[1], joints[2]], [pref + shoulder_label + "1_stretchRig_control2"], joints_group)
    else:
        cmds.sets("bindJointsSet", e=True, add=[joints[0], joints[1]])

    color = 7.0 if pref == "r_" else 6.0
    create_control("circle", [shoulder, joints[1]], [1.0, color, 0], "body")

    lock_attrs(joints_group, [1, 1, 1], [1, 1, 1], [1, 1, 1], True)
    lock_attrs(controls_group, [1, 1, 1], [1, 1, 1], [1, 1, 1], True)
    lock_attrs(shoulder_group, [1, 1, 1], [1, 1, 1], [1, 1, 1], True)
    lock_attrs(shoulder, [1, 1, 1], [0, 0, 0], [1, 1, 1], True)
    lock_attrs(group1, [1, 1, 1], [1, 1, 1], [1, 1, 1], True)
    lock_attrs(group2, [1, 1, 1], [1, 1, 1], [1, 1, 1], True)
    lock_attrs(group3, [1, 1, 1], [1, 1, 1], [1, 1, 1], True)


def create_eyes():
    joints_label = "eyes_joints"
    controls_label = "eyes_controls"
    look_label = "look"
    eye_label = "eye"
    additional_joints = ["head_joint", "pelvis", "hip_joint"]

    l_eye_pos = cmds.getAttr("l_eye_tuner.worldPosition")[0]
    r_eye_pos = cmds.getAttr("r_eye_tuner.worldPosition")[0]
    look_pos = cmds.getAttr("look_tuner.worldPosition")[0]
    coeff = cmds.getAttr("character_tuners.controlsSize")

    eyes_vec = [r_eye_pos[0] - l_eye_pos[0], r_eye_pos[1] - l_eye_pos[1], r_eye_pos[2] - l_eye_pos[2]]
    eyes_mag = cmds.math.sqrt(sum(map(lambda x: x * x, eyes_vec)))

    joints_group = cmds.group(em=True, n=joints_label, p="skeleton")
    cmds.select(cl=True)
    joints = []
    joints.append(cmds.joint(p=l_eye_pos, n="l_eye_joint", parent=joints_group))
    joints.append(cmds.joint(p=r_eye_pos, n="r_eye_joint", parent=joints_group))

    cmds.group(em=True, n=controls_label, p="controls")
    dyn_group = cmds.group(em=True, n=look_label + "_dynamicParent_group", p=controls_label)
    look_group = cmds.group(em=True, n=look_label + "_group", p=dyn_group)
    cmds.group(em=True, n=look_label + "_dynamicParentPoser", p=look_group)
    cmds.delete(cmds.orientConstraint(additional_joints[1], look_group))

    l_eye = cmds.group(em=True, n="l_" + eye_label, p=look_label)
    r_eye = cmds.group(em=True, n="r_" + eye_label, p=look_label)
    cmds.setAttr(l_eye + ".tx", eyes_mag / 2.0)
    cmds.setAttr(r_eye + ".tx", -eyes_mag / 2.0)

    cmds.makeIdentity(l_eye, apply=True, t=1, r=1, s=1, n=0)
    cmds.makeIdentity(r_eye, apply=True, t=1, r=1, s=1, n=0)

    cmds.xform(look_group, ws=True, t=look_pos)

    cmds.aimConstraint(joints[0], l_eye, aimVector=[0, 0, 1], upVector=[0, 1, 0], worldUpType="none")
    cmds.aimConstraint(joints[1], r_eye, aimVector=[0, 0, 1], upVector=[0, 1, 0], worldUpType="none")

    if cmds.objExists(additional_joints[0]):
        cmds.xform(additional_joints[0], pivots=True, ws=True, rp=joints_group)
        cmds.parent(joints_group, additional_joints[0])
        cmds.orientConstraint(additional_joints[0], look_group, mo=True)

    dyn_parents = []
    if cmds.objExists(additional_joints[0]):
        dyn_parents.append("head=" + additional_joints[0])
    if cmds.objExists(additional_joints[2]):
        dyn_parents.append("pelvis=" + additional_joints[2])
    if len(dyn_parents) > 0:
        make_dynamic_parent(look_label, dyn_group, dyn_parents)

    draw_help_line([l_eye, joints[0]], "l_eye", l_eye + ".v")
    draw_help_line([r_eye, joints[1]], "r_eye", r_eye + ".v")
    draw_help_line([l_eye, r_eye], "eyes", look_label + ".v")

    create_control("rect", [look_label, look_label], [1.0, 8, (eyes_mag + 0.5 * coeff) * 1 / coeff, 0.5, 2], "eyes")
    create_control("circle", [l_eye, l_eye], [0.2, 7, 2], "eyes")
    create_control("circle", [r_eye, r_eye], [0.2, 6, 2], "eyes")

    lock_attrs(dyn_group, [1, 1, 1], [1, 1, 1], [1, 1, 1], True)
    lock_attrs(look_group, [1, 1, 1], [1, 1, 1], [1, 1, 1], True)
    lock_attrs(look_label + "_dynamicParentPoser", [0, 0, 0], [0, 0, 0], [1, 1, 1], True)
    lock_attrs(look_label, [0, 0, 0], [1, 1, 1], [1, 1, 1], True)
    lock_attrs(l_eye, [0, 0, 1], [1, 1, 1], [1, 1, 1], True)
    lock_attrs(r_eye, [0, 0, 1], [1, 1, 1], [1, 1, 1], True)

def selector_create_text(name, user_text, pos, scale):
    text = cmds.textCurves(ch=0, f="Arial|h-13|w400|c204", t=user_text)
    cmds.scale(scale, scale, scale, text[0])

    text_group = cmds.group(em=True, n=name)
    shapes = cmds.listRelatives(ad=True, type="nurbsCurve", ni=True, s=True, fullPath=True, children=True)
    shapes_transforms = [cmds.listRelatives(parent=True)[0] for shape in shapes]

    cmds.shapeParent(text_group, shapes_transforms, add=True, shape=True)
    cmds.delete(text[0])
    cmds.xform(cp=True, ws=True, t=text_group)

    sp = cmds.spaceLocator()
    cmds.setAttr(sp[0] + ".t", pos[0], pos[1], pos[2])
    cmds.delete(cmds.pointConstraint(sp[0], text_group))
    cmds.delete(sp[0])

    cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0, text_group)

    cmds.lockNode(text_group, lock=True)
    return text_group


def selector_create_control(shape, label, name, command, pos, params, parent):
    color = int(params[0])
    text_width = params[1]
    geom = ""

    if shape == "circle":
        radius = params[2]
        circle = cmds.circle(c=pos, nr=(0, 0, 1), sw=360, r=radius, d=3, ut=0, tol=0.1, s=8, ch=0, n=name)
        geom = circle[0]

        if label:
            text = selector_create_text(name, label, pos, text_width)
            cmds.shapeParent(geom, text, add=True, shape=True)

    elif shape == "rect":
        width = params[2] * params[0]
        height = params[3] * params[0]

        if params[4] == 0:
            geom = cmds.curve(d=1,
                              p=[(0, -width / 2, -height / 2), (0, -width / 2, height / 2), (0, -width / 2, height / 2),
                                 (0, width / 2, height / 2), (0, width / 2, -height / 2), (0, -width / 2, -height / 2)])
        elif params[4] == 1:
            geom = cmds.curve(d=1,
                              p=[(-width / 2, 0, -height / 2), (-width / 2, 0, height / 2), (-width / 2, 0, height / 2),
                                 (width / 2, 0, height / 2), (width / 2, 0, -height / 2), (-width / 2, 0, -height / 2)])
        elif params[4] == 2:
            geom = cmds.curve(d=1,
                              p=[(-width / 2, -height / 2, 0), (-width / 2, height / 2, 0), (-width / 2, height / 2, 0),
                                 (width / 2, height / 2, 0), (width / 2, -height / 2, 0), (-width / 2, -height / 2, 0)])

        cmds.setAttr(geom + ".t", pos[0], pos[1], pos[2])
        geom = cmds.rename(geom, name)

        if label:
            text = selector_create_text(name, label, pos, text_width)
            cmds.shapeParent(geom, text, add=True, shape=True)

    else:
        geom = selector_create_text(name, label, pos, text_width)

    cmds.parent(geom, parent)
    cmds.color(geom, ud=color)

    cmds.addAttr(ln="script", dt="string", longName=True, shortName=False)
    cmds.setAttr(geom + ".script", command, type="string")

    cmds.xform(cp=True, ws=True, t=geom)

    cmds.lockNode(geom, lock=False)
    return geom


def selector_add_stretch_rig_controls(base_name, params, group):
    selector_postfix = "_selector"
    stretch_rig_controls = []
    stretch_rig_indexes = []

    color = int(params[0])
    control_size = params[1]
    start_pos = params[2]
    end_pos = params[3]
    axis = int(params[4])  # 0 - x, 1 - y, 2 - z

    i = 1
    while True:
        if cmds.objExists(base_name + str(i)):
            if not cmds.getAttr(base_name + str(i) + "_group.v"):
                i += 1
                continue
            else:
                stretch_rig_indexes.append(i)
        else:
            break

    step = (start_pos - end_pos) / (len(stretch_rig_indexes) + 1)
    pos = start_pos

    for i in stretch_rig_indexes:
        pos -= step

        if axis == 0:
            position = [pos, 0, 0]
        elif axis == 1:
            position = [0.0, pos, 0]
        else:
            position = [0.0, 0, pos]

        stretch_rig_controls.append(selector_create_control("", "*", base_name + str(i) + selector_postfix,
                                                            "select NAMESPACE" + base_name + str(i), position,
                                                            [color, control_size], group))

    return stretch_rig_controls


def selector_create_arm_leg(pref, type):
    selector_postfix = "_selector"

    arm_control_label = ""
    arm_label = ""
    arm_ik_label = ""
    elbow_ik_label = ""
    arm_fk_label = ""
    elbow_fk_label = ""
    hand_fk_label = ""
    position = []
    rotation = []
    arm_size = 0

    if type == "arm":
        arm_control_label = "arm_control"
        arm_label = "arm"
        arm_ik_label = "armIK"
        elbow_ik_label = "elbowIK"
        arm_fk_label = "armFK"
        elbow_fk_label = "elbowFK"
        hand_fk_label = "handFK"

        if pref == "l_":
            position = [1.7, 5.5, 0]
            rotation = [0, 0, 0]
        elif pref == "r_":
            position = [-1.7, 5.5, 0]
            rotation = [0, 0, 0]

        arm_size = 4

    elif type == "leg":
        arm_control_label = "leg_control"
        arm_label = "leg"
        arm_ik_label = "legIK"
        elbow_ik_label = "kneeIK"
        arm_fk_label = "legFK"
        elbow_fk_label = "kneeFK"
        hand_fk_label = "footFK"

        if pref == "l_":
            position = [1, 0, 0]
        elif pref == "r_":
            position = [-1, 0, 0]

        arm_size = 5

    else:
        raise ValueError("createArmLeg: type must be 'arm' or 'leg'")

    control_size = 1
    button_size = 0.15

    color = 0
    if pref == "l_":
        color = 7
    else:
        color = 6

    group = cmds.group(em=True, n=pref + arm_label + "_group" + selector_postfix)

    c = cmds.curve(d=1, p=[(0, arm_size, 0), (0, arm_size / 2, 0), (0, 0, 0)],
                   n=pref + arm_label + "_curve" + selector_postfix)
    cmds.setAttr(c + ".template", True)
    cmds.parent(c, group)

    fk_controls_group = cmds.group(em=True, n=pref + arm_label + "FK_controls" + selector_postfix, p=group)
    fk_controls = [
        selector_create_control("", "o", pref + arm_fk_label + selector_postfix,
                                "select NAMESPACE" + pref + arm_fk_label,
                                [0.0, arm_size, 0], [color, control_size], group),
        selector_create_control("", "o", pref + elbow_fk_label + selector_postfix,
                                "select NAMESPACE" + pref + elbow_fk_label,
                                [0.0, arm_size / 2, 0], [color, control_size], group),
        selector_create_control("", "o", pref + hand_fk_label + selector_postfix,
                                "select NAMESPACE" + pref + hand_fk_label,
                                [0.0, 0.0, 0], [color, control_size], group)
    ]
    cmds.parent(fk_controls, fk_controls_group)
    cmds.lockNode(fk_controls_group, lock=False)

    ik_controls_group = cmds.group(em=True, n=pref + arm_label + "IK_controls" + selector_postfix, p=group)
    ik_controls = [
        selector_create_control("", "o", pref + elbow_ik_label + selector_postfix,
                                "select NAMESPACE" + pref + elbow_ik_label,
                                [0.0, arm_size / 2, 0], [color, control_size], group),
        selector_create_control("", "o", pref + arm_ik_label + selector_postfix,
                                "select NAMESPACE" + pref + arm_ik_label,
                                [0.0, 0.0, 0], [color, control_size], group)
    ]
    cmds.parent(ik_controls, ik_controls_group)
    if cmds.objExists(pref + arm_label + "FK_controls"):
        cmds.connectAttr(pref + arm_label + "FK_controls.v", ik_controls_group + ".v")

    cmds.lockNode(ik_controls_group, lock=True)

    stretch_rig_controls = []
    stretch_rig_controls.extend(selector_add_stretch_rig_controls(pref + arm_label + "1_stretchRig_control",
                                                                  [color, control_size / 1.5, arm_size, arm_size / 2,
                                                                   1],
                                                                  group))
    stretch_rig_controls.extend(selector_add_stretch_rig_controls(pref + arm_label + "2_stretchRig_control",
                                                                  [color, control_size / 1.5, arm_size / 2, 0, 1],
                                                                  group))

    offset = 0.9 if pref == "r_" else -0.9

    buttons = [
        selector_create_control("circle", "ik", pref + arm_label + "_kinematicSwitch" + selector_postfix,
                                "kinematicSwitch(\"{}\",\"{}\");select -cl;".format(pref, arm_label),
                                [offset, arm_size / 2 + 1.2, 0], [8.0, button_size, 0.4], group),
        selector_create_control("circle", "p", pref + arm_label + "_changeParent" + selector_postfix,
                                "selector_changeParentSelector({\"NAMESPACE{}\",\"NAMESPACE{}\"});select -cl;"
                                .format(pref + arm_ik_label, pref + elbow_ik_label),
                                [offset, arm_size / 2, 0], [1.0, button_size, 0.4], ik_controls_group),
        selector_create_control("circle", "c", pref + arm_control_label + selector_postfix,
                                "select NAMESPACE{}".format(pref + arm_control_label),
                                [offset, arm_size / 2 - 1.2, 0], [4.0, button_size, 0.4], group)
    ]

    cmds.setAttr(group + ".t", position[0], position[1], position[2])
    cmds.setAttr(group + ".r", rotation[0], rotation[1], rotation[2])
    cmds.lockNode(group, lock=False)

    controls = []
    controls.extend(fk_controls)
    controls.extend(ik_controls)
    controls.extend(buttons)
    controls.extend(stretch_rig_controls)

    return controls

def selector_create_finger(pref, type, position, rotation):
    selector_postfix = "_selector"

    finger_control_label = type + "_control"
    finger_label = type
    finger_ik_label = type + "IK"
    finger_ik_orientation_label = type + "IKOrientation"
    finger_ik_rotator_label = type + "IKRotator"
    finger_transform_label = type + "Transform"
    finger_fk1_label = type + "FK1"
    finger_fk2_label = type + "FK2"
    finger_fk3_label = type + "FK3"

    finger_size = 2.5
    control_size = 0.5
    button_size = 0.09

    color = 0
    if pref == "l_":
        color = 7
    else:
        color = 6

    group = cmds.group(em=True, n="{}_{}_group{}".format(pref, finger_label, selector_postfix), p="selector")

    c = cmds.curve(d=1, p=[(0, finger_size, 0), (0, 2*finger_size/3, 0), (0, finger_size/3, 0), (0, 0, 0)],
                   n="{}_{}_curve{}".format(pref, finger_label, selector_postfix))
    cmds.setAttr(c + ".template", True)
    cmds.parent(c, group)

    # FK controls
    fk_controls_group = cmds.group(em=True, n="{}_FK_controls{}".format(pref, selector_postfix), p=group)
    fk_controls = []

    fk_controls.append(selector_create_control("rect", "",
                                               "{}{}{}".format(pref, finger_transform_label, selector_postfix),
                                               "select {}{}".format(pref, finger_transform_label),
                                               [0.0, finger_size, 0],
                                               [color, control_size, 0.1, 0.1, 2], group))

    fk_controls.append(selector_create_control("", "o",
                                               "{}{}{}".format(pref, finger_fk1_label, selector_postfix),
                                               "select {}{}".format(pref, finger_fk1_label),
                                               [0.0, finger_size, 0], [color, control_size], group))

    fk_controls.append(selector_create_control("", "o",
                                               "{}{}{}".format(pref, finger_fk2_label, selector_postfix),
                                               "select {}{}".format(pref, finger_fk2_label),
                                               [0.0, 2*finger_size/3, 0], [color, control_size], group))

    fk_controls.append(selector_create_control("", "o",
                                               "{}{}{}".format(pref, finger_fk3_label, selector_postfix),
                                               "select {}{}".format(pref, finger_fk3_label),
                                               [0.0, finger_size/3, 0], [color, control_size], group))

    cmds.parent(fk_controls, fk_controls_group)
    cmds.lockNode(fk_controls_group, lock=True)

    # IK controls
    ik_controls_group = cmds.group(em=True, n="{}_IK_controls{}".format(pref, selector_postfix), p=group)
    ik_controls = []

    ik_controls.append(selector_create_control("", "o",
                                               "{}{}{}".format(pref, finger_ik_orientation_label, selector_postfix),
                                               "select {}{}".format(pref, finger_ik_orientation_label),
                                               [0.0, 2*finger_size/3, 0], [color, control_size], group))

    ik_controls.append(selector_create_control("", "o",
                                               "{}{}{}".format(pref, finger_ik_label, selector_postfix),
                                               "select {}{}".format(pref, finger_ik_label),
                                               [0.0, 0.0, 0], [color, control_size], group))

    ik_controls.append(selector_create_control("circle", "",
                                               "{}{}{}".format(pref, finger_ik_rotator_label, selector_postfix),
                                               "select {}{}".format(pref, finger_ik_rotator_label),
                                               [0.0, 0.0, 0], [color, control_size*1.2, 0.3], group))

    cmds.parent(ik_controls, ik_controls_group)

    if cmds.objExists("{}FK_controls".format(pref, finger_label)):
        cmds.connectAttr("{}FK_controls.v".format(pref, finger_label), "{}.v".format(fk_controls_group))

    cmds.lockNode(ik_controls_group, lock=True)

    # Stretch Rig controls
    stretch_rig_controls = []

    stretch_rig_controls.extend(selector_add_stretch_rig_controls("{}1_stretchRig_control".format(pref, finger_label),
                                                                  [color, control_size, finger_size, 2*finger_size/1.5, 1],
                                                                  group))

    stretch_rig_controls.extend(selector_add_stretch_rig_controls("{}2_stretchRig_control".format(pref, finger_label),
                                                                  [color, control_size, 2*finger_size/3,
                                                                   finger_size/1.5, 1],
                                                                  group))

    stretch_rig_controls.extend(selector_add_stretch_rig_controls("{}3_stretchRig_control".format(pref, finger_label),
                                                                  [color, control_size, finger_size/1.5, 0, 1],
                                                                  group))

    # Buttons
    offset = 0.5 if pref == "l_" else -0.5

    buttons = []

    buttons.append(selector_create_control("circle", "ik",
                                           "{}{}_kinematicSwitch{}".format(pref, finger_label, selector_postfix),
                                           "kinematicSwitch(\"{}\",\"{}\");select -cl;".format(pref, finger_label),
                                           [offset, finger_size/2 + 0.6, 0], [8.0, button_size, 0.22], group))

    buttons.append(selector_create_control("circle", "p",
                                           "{}{}_changeParent{}".format(pref, finger_label, selector_postfix),
                                           "selector_changeParentSelector({\"NAMESPACE{}\",\"NAMESPACE{}\"});select -cl;"
                                           .format(pref + finger_ik_label, pref + finger_ik_orientation_label),
                                           [offset, finger_size/2, 0], [1.0, button_size, 0.22], ik_controls_group))

    buttons.append(selector_create_control("circle", "c",
                                           "{}{}".format(pref, finger_control_label + selector_postfix),
                                           "select NAMESPACE{}".format(pref + finger_control_label),
                                           [offset, finger_size/2 - 0.6, 0], [4.0, button_size, 0.22], group))

    cmds.setAttr("{}.t".format(group), position[0], position[1], position[2])
    cmds.setAttr("{}.r".format(group), rotation[0], rotation[1], rotation[2])
    cmds.lockNode(group, lock=False)

    controls = []
    controls.extend(fk_controls)
    controls.extend(ik_controls)
    controls.extend(buttons)
    controls.extend(stretch_rig_controls)

    return controls

def selector_createHead(position):
    selectorPostfix = "_selector"
    HeadLabel = "head"
    HeadStretchLabel = "headStretch"
    NeckLabel = "neck"
    controls = []
    headSize = 2
    controlSize = 1

    group = cmds.group(em=True, n="{}_group{}".format(HeadLabel, selectorPostfix), p="selector")

    c = cmds.curve(d=1, n="{}_curve{}".format(HeadLabel, selectorPostfix), p=[(0, 0, 0), (0, headSize, 0), (0, headSize * 2, 0)])
    cmds.setAttr(c + ".template", True)
    cmds.parent(c, group)

    controls.append(selector_create_control("", "o", "{}{}".format(NeckLabel, selectorPostfix), "select NAMESPACE" + NeckLabel, [0.0, 0, 0], [8.0, controlSize], group))
    controls.append(selector_create_control("", "o", "{}{}".format(HeadLabel, selectorPostfix), "select NAMESPACE" + HeadLabel, [0.0, headSize, 0], [8.0, controlSize], group))
    controls.append(selector_create_control("", "o", "{}{}".format(HeadStretchLabel, selectorPostfix), "select NAMESPACE" + HeadStretchLabel, [0.0, headSize * 2, 0], [8.0, controlSize], group))

    controls.append(selector_create_control("circle", "p", "{}_changeParent{}".format(HeadLabel, selectorPostfix), "selector_changeParentSelector({\"NAMESPACE" + HeadLabel + "\"});select -cl;", [0.8, headSize, 0], [1.0, controlSize / 1.5, 0.4], group))

    controls.extend(selector_add_stretch_rig_controls("{}_stretchRig_control".format(NeckLabel), [8.0, controlSize / 1.5, 0, headSize, 1], group))
    controls.extend(selector_add_stretch_rig_controls("{}_stretchRig_control".format(HeadLabel), [8.0, controlSize / 1.5, headSize, headSize * 2, 1], group))

    cmds.setAttr(group + ".t", position[0], position[1], position[2])
    cmds.lockNode(group, l=[0, 0, 1], a=True)

    return controls


def loadPreset(file):
    path = cmds.internalVar(userPresetsDir=True) + "AutoriggingSystemPresets/" + file

    if not cmds.filetest(r=path) or file == "":
        return

    cmds.evalDeferred("source \"" + path + "\"")


def savePreset(*args):
    preset = cmds.optionMenu("presets_optionMenu", q=True, v=True)
    file = cmds.promptDialog(
        title="Enter preset's name",
        message="Enter preset's name",
        text=preset,
        button=["OK", "Cancel"],
        defaultButton="OK",
        cancelButton="Cancel",
        dismissString="Cancel"
    )

    if file == "default":
        cmds.confirmDialog(title="Warning", message="Cannot rewrite default preset", button=["OK"])
        return

    create_preset(file, 2)


def deletePreset(*args):
    preset = cmds.optionMenu("presets_optionMenu", q=True, v=True)

    if preset == "default":
        cmds.confirmDialog(title="Warning", message="Cannot delete default preset", button=["OK"])
        return

    path = cmds.internalVar(userPresetsDir=True) + "AutoriggingSystemPresets/" + preset

    if cmds.confirmDialog(title="Confirm", message="Do you really want to delete this preset?", button=["Yes", "No"],
                          defaultButton="No", cancelButton="No", dismissString="No") == "Yes":
        cmds.sysFile(path, delete=True)
        getAvailablePresets()


def creationInterface():
    window = "creationInterfaceWnd"
    width = 400
    height = 685

    if cmds.windowPref(window, exists=True):
        cmds.windowPref(window, remove=True)

    if cmds.window(window, exists=True):
        cmds.deleteUI(window, window=True)

    cmds.window(window, title="Autorigging System", width=width, height=height, sizeable=False)
    cmds.columnLayout(adj=True, rs=5)

    frmLayout = cmds.formLayout()

    presets_optionMenu = cmds.optionMenu(label="Presets",
                                         cc=lambda x: loadPreset(cmds.optionMenu("presets_optionMenu", q=True, v=True)))
    presets_save_button = cmds.button(label="Save", c=savePreset)
    presets_load_button = cmds.button(label="Load",
                                      c=lambda x: loadPreset(cmds.optionMenu("presets_optionMenu", q=True, v=True)))
    presets_delete_button = cmds.button(label="Delete", c=deletePreset)

    cmds.formLayout(frmLayout, edit=True,
                    attachForm=[(presets_optionMenu, 'left', 5),
                                (presets_save_button, 'left', 5),
                                (presets_load_button, 'left', 5),
                                (presets_delete_button, 'left', 5)]
                    )

    cmds.setParent("..")

    # FrameLayouts and other UI elements omitted for brevity

    cmds.showWindow(window)
    create_preset("default", 0)
    getAvailablePresets()


def checkTuners(type):
    tuners = []

    if type == "body":
        tuners = ["pelvis_tuner", "spine_tuner", "chest_tuner", "clavicle_tuner", "neck_tuner", "head_end_tuner",
                  "look_tuner", "r_eye_tuner", "l_eye_tuner", "head_tuner"]
    elif type == "arms":
        tuners = ["l_hand_tuner", "l_elbow_tuner", "l_arm_tuner", "l_shoulder_tuner",
                  "r_hand_tuner", "r_elbow_tuner", "r_arm_tuner", "r_shoulder_tuner"]
    elif type == "hands":
        tuners = ["l_indexFinger1_tuner", "l_indexFinger2_tuner", "l_indexFinger3_tuner", "l_indexFinger4_tuner",
                  "l_middleFinger1_tuner", "l_middleFinger2_tuner", "l_middleFinger3_tuner", "l_middleFinger4_tuner",
                  "l_ringFinger1_tuner", "l_ringFinger2_tuner", "l_ringFinger3_tuner", "l_ringFinger4_tuner",
                  "l_pinkyFinger1_tuner", "l_pinkyFinger2_tuner", "l_pinkyFinger3_tuner", "l_pinkyFinger4_tuner",
                  "l_hand2_tuner", "l_thumbFinger4_tuner", "l_thumbFinger3_tuner", "l_thumbFinger2_tuner",
                  "l_thumbFinger1_tuner", "l_hand_tuner",
                  "r_indexFinger1_tuner", "r_indexFinger2_tuner", "r_indexFinger3_tuner", "r_indexFinger4_tuner",
                  "r_middleFinger1_tuner", "r_middleFinger2_tuner", "r_middleFinger3_tuner", "r_middleFinger4_tuner",
                  "r_ringFinger1_tuner", "r_ringFinger2_tuner", "r_ringFinger3_tuner", "r_ringFinger4_tuner",
                  "r_pinkyFinger1_tuner", "r_pinkyFinger2_tuner", "r_pinkyFinger3_tuner", "r_pinkyFinger4_tuner",
                  "r_hand2_tuner", "r_thumbFinger4_tuner", "r_thumbFinger3_tuner", "r_thumbFinger2_tuner",
                  "r_thumbFinger1_tuner", "r_hand_tuner"]
    elif type == "feet":
        tuners = ["l_foot1_tuner", "l_foot2_tuner", "l_toe_tuner", "l_heel_tuner",
                  "r_foot1_tuner", "r_foot2_tuner", "r_toe_tuner", "r_heel_tuner"]

    for t in tuners:
        if not cmds.objExists(t):
            cmds.error("checkTuners: cannot find '{}' tuner. Creation is skipped".format(t))


def makeCharacter():
    if not cmds.checkBox("doNotCreateRig_checkBox", q=True, v=True):
        if not cmds.objExists("character_tuners"):
            cmds.error("makeCharacter: cannot find 'characters_tuners' to generate rig")

        rotY = cmds.getAttr("character_tuners.ry")
        if rotY % 90 != 0:
            cmds.error("makeCharacter: character_tuners.ry must be 0, 90, 180, -180, -90")

        checkTuners("body")
        checkTuners("arms")
        checkTuners("legs")
        checkTuners("hands")
        checkTuners("feet")

        create_main_hierarchy()

        body = cmds.intFieldGrp("body_intFieldGrp", q=True, v=True)
        create_body(body)

        if cmds.checkBox("neck_stretchRig_checkBox", q=True, v=True):
            neckStretch = cmds.intFieldGrp("neck_stretchRig_intFieldGrp", q=True, v=True)
        else:
            neckStretch = []

        if cmds.checkBox("head_stretchRig_checkBox", q=True, v=True):
            headStretch = cmds.intFieldGrp("head_stretchRig_intFieldGrp", q=True, v=True)
        else:
            headStretch = []

        create_head(neckStretch, headStretch)

        if cmds.checkBox("eyes_checkBox", q=True, v=True):
            create_eyes()

        if cmds.checkBox("arms_left_checkBox", q=True, v=True):
            if cmds.checkBox("hands_left_checkBox", q=True, v=True):
                fingersStretchRig = cmds.intFieldGrp("fingers_stretchRig_intFieldGrp", q=True, v=True) if cmds.checkBox(
                    "fingers_stretchRig_checkBox", q=True, v=True) else []
                stretchable = cmds.checkBox("finger_stretch_checkBox", q=True, v=True)
                thumb = cmds.checkBox("finger_thumb_checkBox", q=True, v=True)
                index = cmds.checkBox("finger_index_checkBox", q=True, v=True)
                middle = cmds.checkBox("finger_middle_checkBox", q=True, v=True)
                ring = cmds.checkBox("finger_ring_checkBox", q=True, v=True)
                pinky = cmds.checkBox("finger_pinky_checkBox", q=True, v=True)
                create_hand("l_", [thumb, index, middle, ring, pinky], fingersStretchRig, stretchable)

            create_shoulder("l_", cmds.checkBox("shoulders_stretchRig_checkBox", q=True, v=True))

            stretchable = cmds.checkBox("arms_stretch_checkBox", q=True, v=True)
            armsStretchRig = cmds.intFieldGrp("arms_stretchRig_intFieldGrp", q=True, v=True) if cmds.checkBox(
                "arms_stretchRig_checkBox", q=True, v=True) else []
            create_arm_leg("l_", "arm", stretchable, armsStretchRig)

        if cmds.checkBox("arms_right_checkBox", q=True, v=True):
            if cmds.checkBox("hands_right_checkBox", q=True, v=True):
                fingersStretchRig = cmds.intFieldGrp("fingers_stretchRig_intFieldGrp", q=True, v=True) if cmds.checkBox(
                    "fingers_stretchRig_checkBox", q=True, v=True) else []
                stretchable = cmds.checkBox("finger_stretch_checkBox", q=True, v=True)
                thumb = cmds.checkBox("finger_thumb_checkBox", q=True, v=True)
                index = cmds.checkBox("finger_index_checkBox", q=True, v=True)
                middle = cmds.checkBox("finger_middle_checkBox", q=True, v=True)
                ring = cmds.checkBox("finger_ring_checkBox", q=True, v=True)
                pinky = cmds.checkBox("finger_pinky_checkBox", q=True, v=True)
                create_hand("r_", [thumb, index, middle, ring, pinky], fingersStretchRig, stretchable)

            create_shoulder("r_", cmds.checkBox("shoulders_stretchRig_checkBox", q=True, v=True))

            stretchable = cmds.checkBox("arms_stretch_checkBox", q=True, v=True)
            armsStretchRig = cmds.intFieldGrp("arms_stretchRig_intFieldGrp", q=True, v=True) if cmds.checkBox(
                "arms_stretchRig_checkBox", q=True, v=True) else []
            create_arm_leg("r_", "arm", stretchable, armsStretchRig)

        if cmds.checkBox("legs_left_checkBox", q=True, v=True):
            create_leg("l_", cmds.checkBox("legs_stretchRig_checkBox", q=True, v=True))

        if cmds.checkBox("legs_right_checkBox", q=True, v=True):
            create_leg("r_", cmds.checkBox("legs_stretchRig_checkBox", q=True, v=True))

        if cmds.checkBox("tail_checkBox", q=True, v=True):
            create_tail()

        cmds.delete("character_tuners")


def getAvailablePresets(*args):
    path = cmds.internalVar(userPresetsDir=True) + "AutoriggingSystemPresets/"

    if not cmds.filetest(r=path):
        cmds.sysFile(path, makeDir=True)

    presets_optionMenu = cmds.optionMenu("presets_optionMenu", q=True, ill=True)

    if presets_optionMenu:
        cmds.deleteUI(presets_optionMenu)

    allFiles = cmds.getFileList(folder=path, filespec="*.mel")

    if allFiles:
        allFiles.sort()

        for file in allFiles:
            cmds.menuItem(label=file.split(".")[0], parent="presets_optionMenu")

    if cmds.optionMenu("presets_optionMenu", q=True, ni=True) == 0:
        cmds.menuItem(label="Default", parent="presets_optionMenu")


def importUI():

    global version

    if cmds.window("Autorigging_System", exists=True):
        cmds.deleteUI("Autorigging_System")

    mainWindow = cmds.window("Autorigging_System", t="Autorigging System")

    cmds.columnLayout(adj=True)
    cmds.separator(h=15)
    cmds.text(l="Select a Rig to Import")
    cmds.separator(h=15)

    cmds.setParent("..")

    cmds.rowColumnLayout(nc=4, cw=[(1, 200), (2, 60), (3, 60), (4, 60)])
    cmds.button(l="Autorig")
    cmds.button(l="Quit", c="cmds.quit()")
    cmds.setParent("..")

    cmds.showWindow(mainWindow)


cmds.evalDeferred(importUI)
