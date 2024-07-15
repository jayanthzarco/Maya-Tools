import maya.cmds as cmds


class NurbsRibbon:
    def __init__(self, numFollicles=6, numDrivers=3, name="nurbsRibbon"):
        if numDrivers <= 1:
            cmds.error("Number of drivers must be greater than 1.")
            return

        self.numFollicles = numFollicles
        self.numDrivers = numDrivers
        self.name = name

        # Create NURBS Plane
        self.ribbon = cmds.nurbsPlane(w=6, ax=(0, 1, 0), ch=0, u=6, v=1, lr=.1666666667, n=name + "_Ribbon")
        self.ribbonShape = cmds.listRelatives(self.ribbon, shapes=True)[0]
        cmds.makeIdentity(self.ribbon, s=1, apply=True)
        cmds.delete(self.ribbon, constructionHistory=True)

        # Create follicles
        self.ribbonFollicles = []
        for i in range(numFollicles):
            follicle = cmds.createNode("follicle")
            follicleTransform = cmds.listRelatives(follicle, parent=True)[0]
            follicleTransform = cmds.rename(follicleTransform, "{}_follicle#".format(name))
            follicleShape = cmds.listRelatives(follicleTransform, shapes=True)[0]
            self.ribbonFollicles.append([follicleTransform, follicleShape])
            cmds.connectAttr(self.ribbonShape + ".local", follicleShape + ".inputSurface")
            cmds.connectAttr(self.ribbonShape + ".worldMatrix[0]", follicleShape + ".inputWorldMatrix")
            cmds.connectAttr(follicleShape + ".outRotate", follicleTransform + ".rotate")
            cmds.connectAttr(follicleShape + ".outTranslate", follicleTransform + ".translate")
            U = (1 / float(2 * numFollicles)) + (2 * (1 / float(2 * numFollicles)) * float(i))
            cmds.setAttr(follicleShape + ".parameterU", U)
            cmds.setAttr(follicleShape + ".parameterV", .5)

        # Create bind joints
        self.bindJnts = []
        for i in range(numFollicles):
            cmds.select(clear=True)
            U = (1 / float(2 * numFollicles)) + (2 * (1 / float(2 * numFollicles)) * float(i))
            xLoc = -3 + 6 * U
            bindJoint = cmds.joint(p=[xLoc, 0, 0], n="{}_follicleJnt{}_BIND".format(name, i + 1))
            cmds.parent(bindJoint, self.ribbonFollicles[i][0])
            self.bindJnts.append(bindJoint)

        # Create drive joints
        self.driveJnts = []
        for i in range(numDrivers):
            cmds.select(clear=True)
            driveJoint = cmds.joint(p=(0, 0, 0), radius=1.5, n="{}_DriveJnt#".format(name))
            self.driveJnts.append(driveJoint)

        # Orient joints and create SDK groups
        self.driverOrientGrps = []
        self.driverSDK1Grps = []
        self.driverSDK2Grps = []
        step = 6.0 / (numDrivers - 1)
        for i, jnt in enumerate(self.driveJnts):
            xLoc = -3 + i * step
            sdk2 = cmds.group(jnt, n=jnt + "_SDK2")
            sdk1 = cmds.group(sdk2, n=jnt + "_SDK1")
            orient = cmds.group(sdk1, n=jnt + "_ORIENT")
            self.driverSDK1Grps.append(sdk1)
            self.driverSDK2Grps.append(sdk2)
            cmds.xform(orient, t=(xLoc, 0, 0))
            self.driverOrientGrps.append(orient)

        cmds.select(clear=True)
        cmds.select(self.driveJnts + [self.ribbon[0]])
        ribbonCluster = cmds.skinCluster(dropoffRate=1.55, n="{}_ribbonCluster#".format(name))[0]

        # Adjust skin weights
        cmds.skinPercent(ribbonCluster, self.ribbon[0] + ".cv[8][0:3]", transformValue=(self.driveJnts[-1], 1))
        cmds.skinPercent(ribbonCluster, self.ribbon[0] + ".cv[0][0:3]", transformValue=(self.driveJnts[0], 1))

        # Organize hierarchy
        self.driveGrp = cmds.group(self.driverOrientGrps, n="{}_ribbonJnts_DRIVE".format(name))
        cmds.select(clear=True)
        follicleTransforms = [f[0] for f in self.ribbonFollicles]
        self.follicleGrp = cmds.group(follicleTransforms, n="{}_ribbon_FOLLICLES".format(name))
        self.allGrp = cmds.group(self.driveGrp, self.follicleGrp, self.ribbon[0], n="{}_ALL".format(name))

        # Setup scale constraints
        for follicle in self.ribbonFollicles:
            cmds.scaleConstraint(self.driveJnts, follicle[0], mo=True)

        # Create bind joint set
        cmds.select(self.bindJnts)
        cmds.sets(n="{}_BIND_SET".format(name))

        # Set ribbon attributes for rendering
        cmds.setAttr(self.ribbonShape + ".primaryVisibility", 0)
        cmds.setAttr(self.ribbonShape + ".castsShadows", 0)
        cmds.setAttr(self.ribbonShape + ".receiveShadows", 0)
        cmds.setAttr(self.ribbonShape + ".visibleInReflections", 0)
        cmds.setAttr(self.ribbonShape + ".visibleInRefractions", 0)


class NurbsRibbonUI:
    def __init__(self):
        self.window = "nurbsRibbonUI"
        self.title = "Nurbs Ribbon Setup"
        self.size = (300, 200)
        self.ribbon_name = "nurbsRibbon"
        self.num_follicles = 6
        self.num_drivers = 3

    def create_ui(self):
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window)

        self.window = cmds.window(self.window, title=self.title, widthHeight=self.size)
        cmds.columnLayout(adjustableColumn=True)

        cmds.text(label="Ribbon Name:")
        self.ribbon_name_field = cmds.textField(text=self.ribbon_name)

        cmds.text(label="Number of Follicles:")
        self.num_follicles_field = cmds.intField(value=self.num_follicles)

        cmds.text(label="Number of Drivers:")
        self.num_drivers_field = cmds.intField(value=self.num_drivers)

        cmds.button(label="Create Ribbon", command=self.create_ribbon)

        cmds.showWindow(self.window)

    def create_ribbon(self, *args):
        self.ribbon_name = cmds.textField(self.ribbon_name_field, query=True, text=True)
        self.num_follicles = cmds.intField(self.num_follicles_field, query=True, value=True)
        self.num_drivers = cmds.intField(self.num_drivers_field, query=True, value=True)

        NurbsRibbon(numFollicles=self.num_follicles, numDrivers=self.num_drivers, name=self.ribbon_name)


if __name__ == '__main__':
    ribbon_ui = NurbsRibbonUI()
    ribbon_ui.create_ui()
