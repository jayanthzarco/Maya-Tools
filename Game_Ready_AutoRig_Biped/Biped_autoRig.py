import maya.cmds as cmd
from PySide2 import QtWidgets


class Node_Names:
    def __init__(self):
        self.placement_joints = {
            'root': 'Root',
            'spine_01': 'Spine_01',
            'spine_02': 'Spine_02',
            'spine_03': 'Spine_03',
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


class InfoMessageBox:
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
        self.loc_jnt.mirror_jnts()

    def generate_rig(self, *args):
        print("Generate Rig action triggered")
        GenerateRig()


class LocationJoint(Node_Names):
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
        root_ctrl = cmds.circle(name=self.placement_joints['root_ctrl'], center=(0, 0, 0), radius=4, normal=(0, 1, 0),
                                ch=False)
        cmds.select(clear=True)

        # root jnt
        root_joint = cmds.joint(name=self.placement_joints['root'], position=(0, 5, 0))
        cmds.joint(name=self.placement_joints['spine_01'], position=(0, 6, 0))
        cmds.joint(name=self.placement_joints['spine_02'], position=(0, 7, 0))
        cmds.joint(name=self.placement_joints['spine_03'], position=(0, 8, 0))

        # Reorient spine joints
        cmds.joint(root_joint, edit=True, orientJoint='xyz', secondaryAxisOrient='yup', ch=False, zso=True)
        cmds.parent(root_joint, root_ctrl)

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
        cmds.mirrorJoint("LT_Thigh", mirrorYZ=True, mirrorBehavior=True, searchReplace=('LT_', 'RT_'))
        cmds.mirrorJoint("LT_Clavicle", mirrorYZ=True, mirrorBehavior=True, searchReplace=('LT_', 'RT_'))
        self.msg_ui.show("Skeleton built check the orientation of joints")


class GenerateRig:
    def __init__(self):
        self.names = Node_Names()
        self.placement_joints = self.names.placement_joints
        print(self.placement_joints)
        self.build_rig()

    def build_rig(self):
        cmds.group(self.placement_joints['root_ctrl'], name="asset")


if __name__ == "__main__":
    rig_window = Window()
    rig_window.create_window()
