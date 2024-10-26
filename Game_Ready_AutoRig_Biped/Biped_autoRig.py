import maya.cmds as cmd
from PySide2 import QtWidgets


class NodeNames:
    def __init__(self):
        self.placement_joints = {
            'root': 'Root',
            'spine_01': 'Spine_01',
            'spine_02': 'Spine_02',
            'spine_03': 'Spine_03',
            'spine_04': 'Spine_04',
            'LT_Clavicle': 'LT_Clavicle',
            'LT_Shoulder': 'LT_Shoulder',
            'LT_Elbow': 'LT_Elbow',
            'LT_Wrist': 'LT_Wrist',
            'LT_Thigh': 'LT_Thigh',
            'LT_Knee': 'LT_Knee',
            'LT_Ankle': 'LT_Ankle',
            'LT_Ball': 'LT_Ball',
            'LT_Toe': 'LT_Toe',
            'RT_Clavicle': 'RT_Clavicle',
            'RT_Shoulder': 'RT_Shoulder',
            'RT_Elbow': 'RT_Elbow',
            'RT_Wrist': 'RT_Wrist',
            'RT_Thigh': 'RT_Thigh',
            'RT_Knee': 'RT_Knee',
            'RT_Ankle': 'RT_Ankle',
            'RT_Ball': 'RT_Ball',
            'RT_Toe': 'RT_Toe',
            'Neck': 'Neck',
            'Head': 'Head',
            'root_ctrl': 'Root_Ctrl'
        }

        self.skin_jnts = {key: value + "_Skn_Jnt" for key, value in self.placement_joints.items()}
        self.asset_names = {
            'asset': 'Asset',
            'geo_grp': 'Geometry_Group',
            'rig_grp': 'Rig_Group',
            'extras': 'Extras',
            'skn_jnts_grp': 'Skn_Jnts_Group',
            'ctrls_group': 'Ctrl_Group',
            'placement_jnts_grp': 'Placements_Jnts_Group',
            'placement_ctrl': 'Placement_Ctrl',
            'main_ctrl': 'Main_Ctrl'
        }

        self.ctrls = {
            'cog_ctrl': 'COG_Ctrl',
            'hip_ctrl': 'Hip_Ctrl',
            'spine_IK_01': 'Spine_IK_01_Ctrl',
            'spine_IK_02': 'Spine_IK_02_Ctrl',
            'spine_IK_03': 'Spine_IK_03_Ctrl',

            'spine_FK_01': 'Spine_FK_01_Ctrl',
            'spine_FK_02': 'Spine_FK_02_Ctrl',
            'spine_FK_03': 'Spine_FK_03_Ctrl',

            'neck': 'Neck_Ctrl',
            'LT_Arm_IK': "LT_Arm_IK_Ctrl",
            'LT_Arm_Pole': "LT_Arm_Pole_Ctrl",
            'RT_Arm_IK': "RT_Arm_IK_Ctrl",
            'RT_Arm_Pole': "LT_Arm_Pole_Ctrl",

            "LT_Leg_IK": "LT_Leg_IK_Ctrl",
            "RT_Leg_IK": "RT_Leg_IK_Ctrl",
            "LT_Leg_Pole": "LT_Leg_Pole_Ctrl",
            "RT_Leg_Pole": "RT_Leg_Pole_Ctrl",

            'LT_Clavicle': "LT_Clavicle_Ctrl",
            'RT_Clavicle': "RT_Clavicle_Ctrl"

        }


class InfoMessageBox:
    def __init__(self):
        self.message = None

    def show(self, message):
        # Create a message box
        self.message = message
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle("Creation Info")
        msg_box.setText(self.message)
        msg_box.setIcon(QtWidgets.QMessageBox.Information)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)

        # Execute the message box
        msg_box.exec_()


class Window:
    def __init__(self):
        super().__init__()
        self.window = None
        self.loc_jnt = LocationJoint()

    def create_window(self):
        self.window = cmd.window(title='Biped Game Rig', width=400, height=130, sizeable=False)
        cmd.rowColumnLayout(nc=1)

        cmd.separator(height=10)
        cmd.button(l='Create Dummy', c=self.create_dummy_joints, width=400)
        cmd.separator(height=10)
        cmd.button(l='Build Skeleton', c=self.build_skeleton, width=400)
        cmd.separator(height=10)
        cmd.button(l='Generate Rig', c=self.generate_rig, width=400)

        cmd.separator(height=12)
        cmd.text(label="| Created by Jayanth", align='right', fn="boldLabelFont")
        cmd.showWindow()

    def create_dummy_joints(self, *args):
        self.loc_jnt.create_dummy_jnts()

    def build_skeleton(self, *args):
        print("Build Skeleton action triggered")
        check = self.loc_jnt.error_check()
        if check:
            return
        self.loc_jnt.create_placement_joints()
        self.loc_jnt.build_asset()
        self.loc_jnt.mirror_jnts()

    def generate_rig(self, *args):
        print("Generate Rig action triggered")
        GenerateRig()


class LocationJoint(NodeNames):
    def __init__(self):
        super().__init__()
        self.msg_ui = InfoMessageBox()

    def create_dummy_jnts(self):
        # scene check
        error_obj = []
        for item in self.placement_joints.values():
            if cmds.objExists(item):
                error_obj.append(item)
        print(error_obj)
        if error_obj:
            self.msg_ui.show(", ".join(error_obj) + " already exists in the scene remove it before creating Joints")
            return
        root_ctrl = cmds.circle(name=self.placement_joints['root_ctrl'], center=(0, 0, 0), radius=4, normal=(0, 1, 0),
                                ch=False)
        cmds.select(clear=True)

        # root jnt
        root_joint = cmds.joint(name=self.placement_joints['root'], position=(0, 4.5, 0))
        cmds.select(cl=True)
        spine_joint = cmds.joint(name=self.placement_joints['spine_01'], position=(0, 5, 0))
        cmds.joint(name=self.placement_joints['spine_02'], position=(0, 6, 0))
        cmds.joint(name=self.placement_joints['spine_03'], position=(0, 7, 0))
        cmds.joint(name=self.placement_joints['spine_04'], position=(0, 8, 0))

        # Reorient spine joints
        cmds.joint(root_joint, edit=True, orientJoint='xyz', secondaryAxisOrient='yup', ch=False, zso=True)
        cmds.parent(root_joint, root_ctrl)
        cmds.parent(spine_joint, root_ctrl)

        # head and neck
        cmds.select(clear=True)
        neck_joint = cmds.joint(name=self.placement_joints['Neck'], position=(0, 10, 0))
        cmds.joint(name=self.placement_joints['Head'], position=(0, 12, 0))
        cmds.parent(neck_joint, root_ctrl)

        # Reorient neck and head joints
        cmds.select(clear=True)
        cmds.joint(self.placement_joints['Neck'], edit=True, orientJoint='xyz', secondaryAxisOrient='yup', ch=False,
                   zso=True)

        # Left Arm
        cmds.select(clear=True)
        clv_joint = cmds.joint(name=self.placement_joints['LT_Clavicle'], position=(1, 9, 0))
        cmds.joint(name=self.placement_joints['LT_Shoulder'], position=(2, 9, 0))
        cmds.joint(name=self.placement_joints['LT_Elbow'], position=(3, 9, -0.1))
        cmds.joint(name=self.placement_joints['LT_Wrist'], position=(4, 9, 0))

        cmds.parent(clv_joint, root_ctrl)

        # Reorient arm joints
        cmds.select(clear=True)
        cmds.joint(self.placement_joints['LT_Clavicle'], edit=True, orientJoint='xyz', secondaryAxisOrient='yup',
                   ch=False,
                   zso=True)

        # Left Leg
        cmds.select(clear=True)
        thigh_joint = cmds.joint(name=self.placement_joints['LT_Thigh'], position=(1, 4, 0))
        cmds.joint(name=self.placement_joints['LT_Knee'], position=(1, 2.27, 0.15))
        cmds.joint(name=self.placement_joints['LT_Ankle'], position=(1, 0.5, 0))
        cmds.joint(name=self.placement_joints['LT_Ball'], position=(1, 0, 0.8))
        cmds.joint(name=self.placement_joints['LT_Toe'], position=(1, -0.15, 1.8))
        cmds.parent(thigh_joint, root_ctrl)

        # Reorient leg joints
        cmds.select(clear=True)
        cmds.joint(self.placement_joints['LT_Thigh'], edit=True, orientJoint='xyz', secondaryAxisOrient='yup', ch=False,
                   zso=True)
        self.msg_ui.show("Placement joints are created")

    def mirror_jnts(self):
        cmds.mirrorJoint(self.skin_jnts["LT_Thigh"], mirrorYZ=True, mirrorBehavior=True, searchReplace=('LT_', 'RT_'))
        cmds.mirrorJoint(self.skin_jnts["LT_Clavicle"], mirrorYZ=True, mirrorBehavior=True,
                         searchReplace=('LT_', 'RT_'))
        self.msg_ui.show("Skeleton built check the orientation of joints")

    def create_placement_joints(self):
        # creating arms and legs skin joints
        cmds.select(cl=True)
        clv_jnt = cmds.joint(name=self.skin_jnts['LT_Clavicle'])
        shl_jnt = cmds.joint(name=self.skin_jnts['LT_Shoulder'])
        elbow_jnt = cmds.joint(name=self.skin_jnts['LT_Elbow'])
        wrist_jnt = cmds.joint(name=self.skin_jnts['LT_Wrist'])
        cmds.matchTransform(clv_jnt, self.placement_joints['LT_Clavicle'])
        cmds.matchTransform(shl_jnt, self.placement_joints['LT_Shoulder'])
        cmds.matchTransform(elbow_jnt, self.placement_joints['LT_Elbow'])
        cmds.matchTransform(wrist_jnt, self.placement_joints['LT_Wrist'])

        clv_jnt_grp = cmds.group(clv_jnt, name=clv_jnt + "_Group")

        # creating leg
        cmds.select(cl=True)
        thigh_jnt = cmds.joint(name=self.skin_jnts['LT_Thigh'])
        keen_jnt = cmds.joint(name=self.skin_jnts['LT_Knee'])
        ankle_jnt = cmds.joint(name=self.skin_jnts['LT_Ankle'])
        ball_jnt = cmds.joint(name=self.skin_jnts['LT_Ball'])
        toe_jnt = cmds.joint(name=self.skin_jnts['LT_Toe'])
        cmds.matchTransform(thigh_jnt, self.placement_joints['LT_Thigh'])
        cmds.matchTransform(keen_jnt, self.placement_joints['LT_Knee'])
        cmds.matchTransform(ankle_jnt, self.placement_joints['LT_Ankle'])
        cmds.matchTransform(ball_jnt, self.placement_joints['LT_Ball'])
        cmds.matchTransform(toe_jnt, self.placement_joints['LT_Toe'])

        thigh_jnt_grp = cmds.group(thigh_jnt, name=thigh_jnt + '_Group')

        # creating spine and head
        cmds.select(cl=True)
        root_jnt = cmds.joint(name=self.skin_jnts['root'])
        cmds.select(cl=True)
        spine_01 = cmds.joint(name=self.skin_jnts['spine_01'])
        spine_02 = cmds.joint(name=self.skin_jnts['spine_02'])
        spine_03 = cmds.joint(name=self.skin_jnts['spine_03'])
        spine_04 = cmds.joint(name=self.skin_jnts['spine_04'])

        cmds.matchTransform(root_jnt, self.placement_joints['root'])
        cmds.matchTransform(spine_01, self.placement_joints['spine_01'])
        cmds.matchTransform(spine_02, self.placement_joints['spine_02'])
        cmds.matchTransform(spine_03, self.placement_joints['spine_03'])
        cmds.matchTransform(spine_04, self.placement_joints['spine_04'])

        spine_jnt_group = cmds.group(spine_01, name='Spine_Skn_Jnt_Group')

        cmds.select(cl=True)
        neck_jnt = cmds.joint(name=self.skin_jnts['Neck'])
        head_jnt = cmds.joint(name=self.skin_jnts['Head'])
        cmds.matchTransform(neck_jnt, self.placement_joints['Neck'])
        cmds.matchTransform(head_jnt, self.placement_joints['Head'])

        head_jnt_group = cmds.group(neck_jnt, name='Head_Skn_Jnts_Group')
        cmds.group(root_jnt, head_jnt_group, spine_jnt_group, clv_jnt_grp,
                   thigh_jnt_grp, name=self.asset_names['skn_jnts_grp'])

    def error_check(self):
        error_obj = []
        for item in self.asset_names.values():
            if cmds.objExists(item):
                error_obj.append(item)
        if error_obj:
            self.msg_ui.show(", ".join(error_obj) + " already exists in the scene")
            return True

    def build_asset(self):
        cmds.select(cl=True)
        asset = cmds.group(name=self.asset_names['asset'], em=True)
        geo = cmds.group(name=self.asset_names['geo_grp'], em=True)
        rig = cmds.group(name=self.asset_names['rig_grp'], em=True)
        extras = cmds.group(name=self.asset_names['extras'], em=True)
        ctrls_group = cmds.group(name=self.asset_names['ctrls_group'], em=True)
        placement_jnts_grp = cmds.group(name=self.asset_names['placement_jnts_grp'], em=True)
        cmds.parent(ctrls_group, rig)
        cmds.parent(geo, asset)
        cmds.parent(rig, asset)
        cmds.parent(extras, asset)
        cmds.parent(self.asset_names['skn_jnts_grp'], rig)
        cmds.parent(self.placement_joints['root_ctrl'], placement_jnts_grp)
        cmds.parent(self.asset_names['placement_jnts_grp'], extras)

        cmds.setAttr(extras + ".visibility", 0)
        cmds.setAttr(extras + ".visibility", lock=True, keyable=False, channelBox=False)


class GenerateRig(NodeNames):
    def __init__(self):
        super().__init__()
        self.ctrls_shapes = ControlShapes()
        self.custom_rig = Rig_Customs()
        self.build_rig()

    def build_rig(self):
        # creating globe ctrls and checking asset
        main_ctrl = self.ctrls_shapes.circle(name=self.asset_names['main_ctrl'], radius=3, color=6)

        plc_ctrl = self.ctrls_shapes.cog(name=self.asset_names['placement_ctrl'], color=13)
        plc_grp = cmds.group(plc_ctrl, name=plc_ctrl + "_Group")
        cmds.parent(main_ctrl, self.asset_names['ctrls_group'])
        cmds.parent(plc_grp, main_ctrl)

        # COG and spine
        cog_ctrl = self.ctrls_shapes.cog(name="COG_Ctrl", color=13)
        cog_group = cmds.group(cog_ctrl, name=cog_ctrl + "_Group")
        cmds.parent(cog_group, plc_ctrl)
        cmds.matchTransform(cog_group, self.skin_jnts['spine_01'])

        # hip ctrl
        hip_ctrl = self.ctrls_shapes.circle(name="Hip_Ctrl", radius=2.2, color=6)
        hip_group = cmds.group(hip_ctrl, name=hip_ctrl + "_Group")
        hip_offset = cmds.group(hip_group, name=hip_ctrl + "_Offset_Group")
        cmds.matchTransform(hip_offset, self.skin_jnts['root'])
        cmds.parent(hip_offset, cog_ctrl)

        # spine ik handel
        spine_ik_handle, effector, spine_curve = cmds.ikHandle(
            sj=self.skin_jnts['spine_01'],
            ee=self.skin_jnts['spine_04'],
            solver="ikSplineSolver",
            createCurve=True,
            simplifyCurve=False
        )
        cmds.rebuildCurve(spine_curve, degree=1, keepRange=1)
        spine_def = cmds.group(spine_ik_handle, spine_curve, name="spine_ik_handel_group")
        cmds.parent(spine_def, self.asset_names['extras'])

        # create a bind joints for ik
        spine_bind_jnts = self.custom_rig.joint_along_the_curve(no_of_joints=3, curve=spine_curve)
        spine_bind_grp = cmds.group(spine_bind_jnts[0], name="spine_bind_joints_group")
        cmds.parent(spine_bind_grp, self.asset_names['extras'])
        cmds.skinCluster(spine_bind_jnts, spine_curve, tsb=True)

        # create spine ik ctrls
        spine_01_ik = self.ctrls_shapes.cube(color=13, name="Spine_01_IK_Ctrl")
        spine_02_ik = self.ctrls_shapes.cube(color=13, name="Spine_02_IK_Ctrl")
        spine_03_ik = self.ctrls_shapes.cube(color=13, name="Spine_03_IK_Ctrl")

        spine_01_ik_offset = cmds.group(spine_01_ik, name=spine_01_ik + "_Offset_Group")
        spine_02_ik_offset = cmds.group(spine_02_ik, name=spine_02_ik + "_Offset_Group")
        spine_03_ik_offset = cmds.group(spine_03_ik, name=spine_03_ik + "_Offset_Group")

        cmds.matchTransform(spine_01_ik_offset, spine_bind_jnts[0])
        cmds.matchTransform(spine_02_ik_offset, spine_bind_jnts[1])
        cmds.matchTransform(spine_03_ik_offset, spine_bind_jnts[2])

        cmds.parentConstraint(spine_01_ik, spine_bind_jnts[0], mo=True)
        cmds.parentConstraint(spine_02_ik, spine_bind_jnts[1], mo=True)
        cmds.parentConstraint(spine_03_ik, spine_bind_jnts[2], mo=True)

        cmds.parent(spine_01_ik_offset, hip_ctrl)

        # creating fk ctrls for spine
        spine_01_fk = self.ctrls_shapes.circle(name="Spine_01_FK_Ctrl", radius=1.5, color=18)
        spine_02_fk = self.ctrls_shapes.circle(name="Spine_02_FK_Ctrl", radius=1.5, color=18)
        spine_03_fk = self.ctrls_shapes.circle(name="Spine_03_FK_Ctrl", radius=1.5, color=18)
        spine_01_fk_offset = cmds.group(spine_01_fk, name=spine_01_fk + "_Offset_Group")
        spine_02_fk_offset = cmds.group(spine_02_fk, name=spine_02_fk + "_Offset_Group")
        spine_03_fk_offset = cmds.group(spine_03_fk, name=spine_03_fk + "_Offset_Group")

        cmds.matchTransform(spine_01_fk_offset, spine_01_ik_offset)
        cmds.matchTransform(spine_02_fk_offset, spine_02_ik_offset)
        cmds.matchTransform(spine_03_fk_offset, spine_03_ik_offset)

        cmds.parent(spine_01_fk_offset, cog_ctrl)
        cmds.parent(spine_02_fk_offset, spine_01_fk)
        cmds.parent(spine_03_fk_offset, spine_02_fk)

        cmds.parent(spine_02_ik_offset, spine_02_fk)
        cmds.parent(spine_03_ik_offset, spine_03_fk)
        cmds.scaleConstraint(cog_ctrl, self.asset_names["skn_jnts_grp"], mo=True)

        # twist for spine
        spine_pma = cmds.createNode("plusMinusAverage", name="Spine_Twist_PMA")
        cmds.connectAttr('Spine_01_FK_Ctrl.rotateY', spine_pma+'.input1D[0]')
        cmds.connectAttr('Spine_02_FK_Ctrl.rotateY', spine_pma+'.input1D[1]')
        cmds.connectAttr('Spine_03_FK_Ctrl.rotateY', spine_pma+'.input1D[2]')
        cmds.connectAttr(spine_pma+'.output1D', spine_ik_handle+".twist")

        # creating neck ctrl
        neck_ctrl = self.ctrls_shapes.circle(name="Neck_Ctrl", radius=1, color=18)
        neck_offset_grp = cmds.group(neck_ctrl, name=neck_ctrl + "_Offset_Group")
        cmds.matchTransform(neck_offset_grp, self.skin_jnts["Neck"])
        cmds.parent(neck_offset_grp, cog_ctrl)

        cmds.parentConstraint(neck_ctrl, self.skin_jnts['Neck'], mo=True)
        cmds.scaleConstraint(neck_ctrl, self.skin_jnts['Neck'], mo=True)
        cmds.parentConstraint(self.skin_jnts['spine_04'], neck_offset_grp, mo=True)

        # create clv ctrl
        lt_clv_ctrl = self.ctrls_shapes.circle(name=self.ctrls['LT_Clavicle'], color=18)
        rt_clv_ctrl = self.ctrls_shapes.circle(name=self.ctrls['RT_Clavicle'], color=18)

        lt_clv_offset = cmds.group(lt_clv_ctrl, name=lt_clv_ctrl+"_Offset_group")
        rt_clv_offset = cmds.group(rt_clv_ctrl, name=rt_clv_ctrl+"_Offset_group")
        cmds.matchTransform(lt_clv_offset, self.skin_jnts['LT_Clavicle'])
        cmds.matchTransform(rt_clv_offset, self.skin_jnts['RT_Clavicle'])
        cmds.parent(lt_clv_offset, cog_ctrl)
        cmds.parent(rt_clv_offset, cog_ctrl)

        cmds.parentConstraint(lt_clv_ctrl, self.skin_jnts['LT_Clavicle'], mo=True)
        cmds.parentConstraint(rt_clv_ctrl, self.skin_jnts['RT_Clavicle'], mo=True)
        cmds.parentConstraint(self.skin_jnts['spine_04'], lt_clv_offset, mo=True)
        cmds.parentConstraint(self.skin_jnts['spine_04'], rt_clv_offset, mo=True)

        # limb rig
        self.custom_rig.limb_rig(side='LT', shape="Arm")
        self.custom_rig.limb_rig(side='RT', shape="Arm")
        self.custom_rig.limb_rig(side='LT', shape="leg")
        self.custom_rig.limb_rig(side='RT', shape="Leg")


class ControlShapes:
    @staticmethod
    def circle(name='circle', radius=1.0, color=1):
        circle = cmds.circle(name=name, radius=radius, center=(0, 0, 0), normal=(0, 1, 0), ch=0)[0]
        shape_node = cmds.listRelatives(circle, shapes=True)[0]
        cmds.setAttr(shape_node + ".overrideEnabled", 1)
        cmds.setAttr(shape_node + ".overrideColor", color)
        return circle

    @staticmethod
    def plus(name="plus", color=18):
        points = [
            (-1, 0.25, -0.00218529),
            (-0.251826, 0.249337, -0.00218529),
            (-0.25, 1, -0.00218529),
            (0.25, 1, -0.00218529),
            (0.250501, 0.249337, -0.00218529),
            (1, 0.25, -0.00218529),
            (1, -0.25, -0.00218529),
            (0.250501, -0.249499, -0.00218529),
            (0.25, -1, -0.00218529),
            (-0.25, -1, -0.00218529),
            (-0.251826, -0.249499, -0.00218529),
            (-1, -0.25, -0.00218529),
            (-1, 0.25, -0.00218529)
        ]

        curve = cmds.curve(name=name, degree=1, point=points)

        shape_node = cmds.listRelatives(curve, shapes=True)[0]
        cmds.setAttr(shape_node + ".overrideEnabled", 1)
        cmds.setAttr(shape_node + ".overrideColor", color)
        return curve

    @staticmethod
    def cube(color=1, name='curve'):
        points = [
            (-1, 0.05, -1),
            (-1, 0.05, 1),
            (1, 0.05, 1),
            (1, 0.05, -1),
            (-1, 0.05, -1),
            (-1, -0.05, -1),
            (1, -0.05, -1),
            (1, -0.05, 1),
            (-1, -0.05, 1),
            (-1, -0.05, -1),
            (-1, 0.05, -1),
            (-1, 0.05, 1),
            (-1, -0.05, 1),
            (1, -0.05, 1),
            (1, 0.05, 1),
            (1, 0.05, -1),
            (1, -0.05, -1),
            (-1, -0.05, -1),
            (-1, 0.05, -1)
        ]

        # Create the curve with degree 1
        curve_ = cmds.curve(name=name, degree=1, point=points)
        shape_node = cmds.listRelatives(curve_, shapes=True)[0]
        cmds.setAttr(shape_node + ".overrideEnabled", 1)
        cmds.setAttr(shape_node + ".overrideColor", color)
        return curve_

    @staticmethod
    def cog(name='COG_Ctrl', color=14):
        curve = cmds.curve(name=name,
                           d=1,
                           p=[(-2.121687, 0, 0),
                              (-1.491384, 0, -0.679417),
                              (-1.491384, 0, -0.357191),
                              (-1.09932, 0, -0.357191),
                              (-0.935137, 0, -0.679417),
                              (-0.679417, 0, -0.935137),
                              (-0.357191, 0, -1.09932),
                              (-0.357191, 0, -1.35728),
                              (-0.671052, 0, -1.35728),
                              (0, 0, -2),
                              (0.679417, 0, -1.35728),
                              (0.357191, 0, -1.35728),
                              (0.357191, 0, -1.09932),
                              (0.679417, 0, -0.935138),
                              (0.935138, 0, -0.679417),
                              (1.09932, 0, -0.357191),
                              (1.454919, 0, -0.357191),
                              (1.454919, 0, -0.679417),
                              (2.1117, 0, 0.001089),
                              (1.454919, 0, 0.671052),
                              (1.454919, 0, 0.357191),
                              (1.09932, 0, 0.357191),
                              (0.935137, 0, 0.679417),
                              (0.679417, 0, 0.935137),
                              (0.357191, 0, 1.09932),
                              (0.349338, 0, 1.323075),
                              (0.679417, 0, 1.323075),
                              (0, 0, 2),
                              (-0.671052, 0, 1.323075),
                              (-0.357733, 0, 1.323075),
                              (-0.357191, 0, 1.09932),
                              (-0.679417, 0, 0.935137),
                              (-0.935137, 0, 0.679417),
                              (-1.09932, 0, 0.357191),
                              (-1.491385, 0, 0.352793),
                              (-1.491385, 0, 0.671052),
                              (-2.121687, 0, 0)
                              ],
                           k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                              21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
                           )
        shape_node = cmds.listRelatives(curve, shapes=True)[0]
        cmds.setAttr(shape_node + ".overrideEnabled", 1)
        cmds.setAttr(shape_node + ".overrideColor", color)
        return curve

    @staticmethod
    def square(name="Square", color=14):
        curve = cmds.curve(name=name, d=1, p=[(-1, 0, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1), (-1, 0, -1)],
                           k=[0, 1, 2, 3, 4])
        shape_node = cmds.listRelatives(curve, shapes=True)[0]
        cmds.setAttr(shape_node + ".overrideEnabled", 1)
        cmds.setAttr(shape_node + ".overrideColor", color)
        return curve

    @staticmethod
    def loc(name="loc", color=12):
        curve = cmds.curve(name=name, d=1, p=[(0, 0, 0), (0, 0, -1), (0, 0, 0), (1, 0, 0), (0, 0, 0), (0, 0, 1),
                                              (0, 0, 0), (-1, 0, 0), (0, 0, 0), (0, 1, 0), (0, 0, 0), (0, -1, 0)],
                           k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        shape_node = cmds.listRelatives(curve, shapes=True)[0]
        cmds.setAttr(shape_node + ".overrideEnabled", 1)
        cmds.setAttr(shape_node + ".overrideColor", color)
        return curve


class Rig_Customs(NodeNames):
    def __init__(self):
        super().__init__()
        self.ctrl_shapes = ControlShapes()

    @staticmethod
    def joint_along_the_curve(no_of_joints, curve):
        selcurve = curve
        No_Of_Jnt = no_of_joints
        bindJnt = []
        newJnt = []
        prevesJnt = ''
        rootJnt = ''
        for jnt in range(0, No_Of_Jnt):
            cmds.select(cl=True)
            newjnt = cmds.joint()
            bindJnt.append(newjnt)
            motionpath = cmds.pathAnimation(newjnt, c=selcurve, fm=True)
            cmds.cutKey(motionpath + '.u', t=())
            cmds.setAttr(motionpath + '.u', jnt * (1.0 / (No_Of_Jnt - 1)))
            cmds.delete(newjnt + '.tx', icn=True)
            cmds.delete(newjnt + '.ty', icn=True)
            cmds.delete(newjnt + '.tz', icn=True)
            cmds.delete(motionpath)
            if jnt == 0:
                prevesJnt = newjnt
                rootJnt = newjnt
                continue
            cmds.parent(newjnt, prevesJnt)
            prevesJnt = newjnt
        cmds.joint(rootJnt, e=True, oj='xyz', sao='yup', ch=True, zso=True)
        for i, x in enumerate(bindJnt):
            newname = selcurve + '_' + str(i + 1).zfill(2)
            newJnt.append(newname + '_Jnt')
        for a, b in zip(bindJnt, newJnt):
            cmds.rename(a, b)
        return newJnt

    def limb_rig(self, side="LT", shape="Arm"):
        if shape == "Arm":
            parent, ctrl = "Clavicle_Skn_Jnt", side+"_Clavicle_Ctrl"
        else:
            parent, ctrl = "Root_Skn_Jnt", "Hip_Ctrl"

        if shape == "Arm":
            base_jnt = "_Shoulder_Skn_Jnt"
            mid_jnt = "_Elbow_Skn_Jnt"
            end_jnt = "_Wrist_Skn_Jnt"
        else:
            base_jnt = "_Thigh_Skn_Jnt"
            mid_jnt = "_Knee_Skn_Jnt"
            end_jnt = "_Ankle_Skn_Jnt"

        # IK CHAIN
        cmds.select(cl=True)
        ik_01 = cmds.joint(name=side + base_jnt.replace("Skn", "IK"))
        ik_02 = cmds.joint(name=side + mid_jnt.replace("Skn", "IK"))
        ik_03 = cmds.joint(name=side + end_jnt.replace("Skn", "IK"))

        cmds.matchTransform(ik_01, side + base_jnt)
        cmds.matchTransform(ik_02, side + mid_jnt)
        cmds.matchTransform(ik_03, side + end_jnt)
        cmds.select(cl=True)
        cmds.makeIdentity(ik_01, apply=True, translate=True, rotate=True, scale=True, normal=False, preserveNormals=True)

        # creating_ctrls and matching positions
        ik_jnt_grp = cmds.group(ik_01, name=side + "_" + shape + "_IK_Jnts")
        ik_ctrl = self.ctrl_shapes.square(name=side + "_" + shape + "_IK_Ctrl", color=13)
        pole_ctrl = self.ctrl_shapes.loc(name=side + "_" + shape + "_Pole_Ctrl", color=13)
        ik_offset = cmds.group(ik_ctrl, name=ik_ctrl + "_Offset_Group")
        pole_offset = cmds.group(pole_ctrl, name=pole_ctrl + "_Offset_Group")
        cmds.matchTransform(ik_offset, ik_03)
        cmds.matchTransform(pole_offset, ik_02)

        ik_grp = cmds.group([ik_offset, pole_offset], name=side + "_" + shape + "_IK_Ctrls_Group")
        ik_handle = cmds.ikHandle(
            name=side+"_"+shape+"_IK_handel",
            startJoint=ik_01,
            endEffector=ik_03,
            solver="ikRPsolver"

        )
        cmds.parentConstraint(ik_ctrl, ik_handle[0], mo=True)
        cmds.poleVectorConstraint(pole_ctrl, ik_handle[0])
        def_grp = cmds.group(ik_jnt_grp, name=ik_jnt_grp.replace("IK", "DEF"))
        cmds.parent(ik_grp, "COG_Ctrl")
        cmds.parentConstraint(self.asset_names['placement_ctrl'], ik_jnt_grp, mo=True)
        cmds.scaleConstraint(self.asset_names['placement_ctrl'], ik_jnt_grp, mo=True)
        cmds.parentConstraint(ctrl, ik_01, mo=True)
        ik_def = cmds.group([ik_handle[0], ik_jnt_grp], name=side+'_'+shape+"_ik_def_group")
        cmds.parent(ik_def, def_grp)

        # FK Chain
        cmds.select(cl=True)
        fk_01 = cmds.joint(name=side + base_jnt.replace("Skn", "FK"))
        fk_02 = cmds.joint(name=side + mid_jnt.replace("Skn", "FK"))
        fk_03 = cmds.joint(name=side + end_jnt.replace("Skn", "FK"))

        cmds.matchTransform(fk_01, side + base_jnt)
        cmds.matchTransform(fk_02, side + mid_jnt)
        cmds.matchTransform(fk_03, side + end_jnt)
        cmds.select(cl=True)
        cmds.makeIdentity(fk_01, apply=True, translate=True, rotate=True, scale=True, normal=False, preserveNormals=True)
        # creating fk ctrls
        for each in [fk_01, fk_02, fk_03]:
            print(each)
            fk_ctrl = self.ctrl_shapes.circle(each.replace('Jnt', 'Ctrl'), radius=0.5, color=18)
            ctrl_group = cmds.group(fk_ctrl, name=fk_ctrl + "_Group")
            offset = cmds.group(ctrl_group, name=ctrl_group.replace("_Group", "_Offset_Group"))
            cmds.matchTransform(offset, each)
            cmds.parentConstraint(fk_ctrl, each, mo=True)

        cmds.parent(fk_03.replace("Jnt", 'Ctrl_Offset_Group'), fk_02.replace("Jnt", 'Ctrl'))
        cmds.parent(fk_02.replace("Jnt", 'Ctrl_Offset_Group'), fk_01.replace("Jnt", 'Ctrl'))

        cmds.parent(fk_01.replace('Jnt', 'Ctrl_Offset_Group'), ctrl)

        cmds.parent(fk_01, def_grp)
        cmds.parent(def_grp, self.asset_names['extras'])

        # IK FK Blending
        ikfk = self.ctrl_shapes.plus(name=side+"_"+shape+"_IKFK_Switch")
        ikfk_grp = cmds.group(ikfk, name=ikfk+"_Group")
        cmds.matchTransform(ikfk_grp, ik_03)
        attributes = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"]
        cmds.addAttr(
            ikfk,
            longName="IKFK",
            attributeType="double",
            minValue=0,
            maxValue=1,
            defaultValue=0)

        for attr in attributes:
            cmds.setAttr(f"{ikfk}.{attr}", lock=True, keyable=False, channelBox=False)


if __name__ == "__main__":
    rig_window = Window()
    rig_window.create_window()
