"""
    Create joint chain on curve
    Script by : Nikhil Ramchandani (3D rigger) - Original MEL script
    Python conversion by Claude
    Connect with me on LinkedIn : https://www.linkedin.com/in/nikramchandani/
"""
import maya.cmds as cmds


def joint_on_curve(num_joints):
    """
    Create joints along a selected curve

    Args:
        num_joints (int): Number of joints to create

    Returns:
        list: Names of created joints
    """
    # Get the selected curve
    selected_curve = cmds.ls(selection=True)

    # Ensure a curve is selected
    if not selected_curve:
        cmds.warning("Please select a curve first")
        return []

    # Calculate the number of control vertices for the curve
    num_cv = cmds.getAttr(selected_curve[0] + ".degree") + cmds.getAttr(selected_curve[0] + ".spans")
    smooth_cv = num_cv * num_joints

    # Rebuild the curve to get evenly distributed points
    dup_curve = cmds.rebuildCurve(
        selected_curve[0],
        constructionHistory=True,
        replaceOriginal=False,
        rebuildType=0,
        endKnots=1,
        keepRange=0,
        keepControlPoints=False,
        keepEndPoints=True,
        keepTangents=False,
        spans=smooth_cv,
        degree=1,
        tolerance=0.01
    )

    # Get the shape node of the duplicated curve
    dup_curve_shape_node = cmds.listRelatives(dup_curve[0], shapes=True)

    # Clear selection
    cmds.select(clear=True)

    joint_names = []

    # Loop through the number of joints specified by the user
    for i in range(num_joints + 1):
        joint_cv = (smooth_cv / num_joints) * i

        # Get the world space position of the CV
        joint_pos = cmds.xform(
            dup_curve_shape_node[0] + ".controlPoints[" + str(int(joint_cv)) + "]",
            query=True,
            translation=True
        )

        # Create a joint at the world space position of the CV
        joint_name = cmds.joint(
            name="joint" + str(i),
            position=joint_pos
        )

        joint_names.append(joint_name)

    # Delete the duplicated curve
    cmds.delete(dup_curve)

    # Orient the joint chain
    cmds.joint(
        joint_names[0],
        edit=True,
        children=True,
        orientJoint="yzx",
        secondaryAxisOrient="yup"
    )

    # Select the root joint
    cmds.select(joint_names[0])

    return joint_names


def joint_on_curve_ui():
    """
    Create a simple UI for the joint on curve tool
    """
    # Check if the window already exists
    if cmds.window("jointOnCurveWindow", exists=True):
        cmds.deleteUI("jointOnCurveWindow")

    # Create the window
    window = cmds.window(
        "jointOnCurveWindow",
        title="Joints on Curve",
        widthHeight=(250, 50), s=False
    )

    # Create a horizontal layout
    cmds.rowLayout(numberOfColumns=2, columnWidth3=(100, 80, 100), adjustableColumn=2, columnAlign=(1, 'right'))

    # Add a label and field for the number of joints
    joint_field = cmds.intField(minValue=1, value=5, width=140)

    # Add the create button
    cmds.button(
        label="Create Joints", width=50,
        command=lambda x: joint_on_curve(cmds.intField(joint_field, query=True, value=True))
    )

    # Show the window
    cmds.showWindow(window)


# Run the UI function when the script is executed
if __name__ == "__main__":
    joint_on_curve_ui()