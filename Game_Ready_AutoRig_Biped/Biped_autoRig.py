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

        self.skin_jnts = {key: value + "_Skn_jnt" for key, value in self.placement_joints.items()}
        self.asset_names = {
            'asset': 'Asset',
            'geo_grp': 'Geometry_Group',
            'rig_grp': 'Rig_Group',
            'extras': 'Extras',
            'skn_jnts_grp': 'Skn_Jnts_Group',
            'ctrls_group': 'Ctrl_Group',
            'placement_jnts_grp': 'Placements_Jnts_Group'
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
            self.msg_ui.show(", ".join(error_obj)+" already exists in the scene")
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
        self.build_rig()

    def build_rig(self):
        # creating globe ctrls and checking asset
        pass



if __name__ == "__main__":
    rig_window = Window()
    rig_window.create_window()
