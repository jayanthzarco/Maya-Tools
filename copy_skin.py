import maya.cmds as cmds


class SkinWeightCopyTool:
    """
    A tool class for copying skin weights between meshes and managing skinCluster nodes in Maya.
    With an enhanced UI featuring pick buttons and text fields.
    """

    def __init__(self):
        self.window_name = 'ResCopySkinweight_tools'
        self.skin_suffix = '_SKN'
        self.source_mesh = ''
        self.target_meshes = []

    def create_ui(self):
        """Create the enhanced user interface for the tool"""
        # Delete UI if it already exists
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)

        # Create window with a more appealing layout
        cmds.window(self.window_name, title='Skin Weight Copy Tool', sizeable=True, width=400)

        # Main layout
        main_layout = cmds.columnLayout(adjustableColumn=True, columnAlign='center', rowSpacing=10, columnWidth=400)

        # Add some spacing at the top
        cmds.separator(height=10, style='none')

        # Title
        cmds.text(label='Skin Weight Copy Tool', font='boldLabelFont', height=30)
        cmds.separator(height=10, style='double')

        # Source mesh section
        cmds.frameLayout(label='Source Mesh', collapsable=False, borderStyle='etchedIn',
                         backgroundColor=[0.2, 0.2, 0.25], marginWidth=5, marginHeight=5)

        source_row = cmds.rowLayout(numberOfColumns=3, columnWidth3=(50, 270, 60), adjustableColumn=2,
                                    columnAlign=(1, 'right'),
                                    columnAttach=[(1, 'right', 5), (2, 'both', 5), (3, 'right', 5)])
        cmds.text(label='Source:')
        self.source_field = cmds.textField(placeholderText='Select source mesh with skin weights', editable=False)
        cmds.button(label='Pick', backgroundColor=[0.8, 0.8, 0.3], command=self.pick_source)
        cmds.setParent('..')  # Go back to frameLayout
        cmds.setParent('..')  # Go back to main layout

        cmds.separator(height=5)

        # Target meshes section
        cmds.frameLayout(label='Target Meshes', collapsable=False, borderStyle='etchedIn',
                         backgroundColor=[0.2, 0.2, 0.25], marginWidth=5, marginHeight=5)

        target_row = cmds.rowLayout(numberOfColumns=3, columnWidth3=(50, 270, 60), adjustableColumn=2,
                                    columnAlign=(1, 'right'),
                                    columnAttach=[(1, 'right', 5), (2, 'both', 5), (3, 'right', 5)])
        cmds.text(label='Targets:')
        self.targets_field = cmds.textField(placeholderText='Select target meshes', editable=False)
        cmds.button(label='Pick', backgroundColor=[0.8, 0.8, 0.3], command=self.pick_targets)
        cmds.setParent('..')  # Go back to frameLayout

        # Add buttons for target mesh management
        target_buttons = cmds.rowLayout(numberOfColumns=2, columnWidth2=(190, 190),
                                        columnAlign=(1, 'center'),
                                        columnAttach=[(1, 'both', 5), (2, 'both', 5)])
        cmds.button(label='Clear Targets', backgroundColor=[0.8, 0.4, 0.4], command=self.clear_targets)
        cmds.button(label='Add Selected to Targets', backgroundColor=[0.4, 0.8, 0.4], command=self.add_to_targets)
        cmds.setParent('..')  # Go back to frameLayout
        cmds.setParent('..')  # Go back to main layout

        cmds.separator(height=10)

        # Copy button
        cmds.button(label='Copy Skin Weights', height=40, backgroundColor=[0.2, 0.6, 0.8],
                    command=self.copy_skinweights)

        cmds.separator(height=10, style='double')

        # Rename skinCluster section
        cmds.frameLayout(label='Rename Skin Clusters', collapsable=False, borderStyle='etchedIn',
                         backgroundColor=[0.2, 0.2, 0.25], marginWidth=5, marginHeight=5)

        suffix_row = cmds.rowLayout(numberOfColumns=2, columnWidth2=(120, 260), adjustableColumn=2,
                                    columnAlign=(1, 'right'), columnAttach=[(1, 'right', 5), (2, 'both', 5)])
        cmds.text(label='Skin Cluster Suffix:')
        self.suffix_field = cmds.textField(text=self.skin_suffix)
        cmds.setParent('..')  # Go back to frameLayout

        cmds.button(label='Rename Skin Clusters', backgroundColor=[0.6, 0.6, 0.8],
                    command=self.rename_skincluster)
        cmds.setParent('..')  # Go back to main layout

        # Help text
        cmds.separator(height=10)
        cmds.text(
            label='How to use: First pick a source mesh with skin weights,\nthen pick target meshes and click "Copy Skin Weights"',
            align='center')

        # Add some spacing at the bottom
        cmds.separator(height=10, style='none')

        cmds.showWindow(self.window_name)

    def pick_source(self, *args):
        """Pick the source mesh from current selection"""
        selection = cmds.ls(selection=True, type='transform')
        if not selection:
            cmds.warning("Nothing selected. Please select a source mesh.")
            return

        # Take the first selected object as source
        self.source_mesh = selection[0]
        cmds.textField(self.source_field, edit=True, text=self.source_mesh)

    def pick_targets(self, *args):
        """Pick target meshes from current selection"""
        selection = cmds.ls(selection=True, type='transform')
        if not selection:
            cmds.warning("Nothing selected. Please select target meshes.")
            return

        self.target_meshes = selection
        cmds.textField(self.targets_field, edit=True, text=", ".join(self.target_meshes))

    def add_to_targets(self, *args):
        """Add currently selected objects to the target list"""
        selection = cmds.ls(selection=True, type='transform')
        if not selection:
            cmds.warning("Nothing selected. Please select objects to add as targets.")
            return

        # Add new selections to existing targets, avoiding duplicates
        for obj in selection:
            if obj not in self.target_meshes:
                self.target_meshes.append(obj)

        cmds.textField(self.targets_field, edit=True, text=", ".join(self.target_meshes))

    def clear_targets(self, *args):
        """Clear the target meshes list"""
        self.target_meshes = []
        cmds.textField(self.targets_field, edit=True, text="")

    def copy_skinweights(self, *args):
        """Copy skin weights from source to target meshes"""
        if not self.source_mesh:
            cmds.warning("No source mesh specified. Please pick a source mesh first.")
            return

        if not self.target_meshes:
            cmds.warning("No target meshes specified. Please pick target meshes first.")
            return

        for target in self.target_meshes:
            if target == self.source_mesh:
                continue  # Skip if target is the same as source

            success = self._copy_to_target(self.source_mesh, target)
            if success:
                cmds.inViewMessage(
                    amg=f"Copied skin weights: <hl>{self.source_mesh}</hl> → <hl>{target}</hl>",
                    pos='midCenter',
                    fade=True
                )

        cmds.select(self.target_meshes, replace=True)

    def _copy_to_target(self, driver, target):
        """Copy skin weights from driver to target"""
        # Get driver's skinCluster
        driver_history = cmds.listHistory(driver, lv=3)
        driver_skincluster = cmds.ls(driver_history, type='skinCluster')

        if not driver_skincluster:
            cmds.warning(f"No skinCluster found on {driver}")
            return False

        # Remove existing skinCluster from target if it exists
        target_history = cmds.listHistory(target, lv=3)
        old_skincluster = cmds.ls(target_history, type='skinCluster')
        if old_skincluster:
            cmds.delete(old_skincluster)

        # Get joints from driver's skinCluster
        joints = cmds.skinCluster(driver_skincluster, query=True, weightedInfluence=True)

        # Create new skinCluster for target
        new_skincluster = cmds.skinCluster(
            joints,
            target,
            toSelectedBones=True,
            maximumInfluences=5,
            dropoffRate=4,
            removeUnusedInfluence=0
        )

        # Copy skin weights
        cmds.copySkinWeights(
            sourceSkin=driver_skincluster[0],
            destinationSkin=new_skincluster[0],
            noMirror=True,
            surfaceAssociation='closestPoint'
        )

        return True

    def rename_skincluster(self, *args):
        """Rename skinCluster nodes to match their mesh names with specified suffix"""
        suffix = cmds.textField(self.suffix_field, query=True, text=True)
        self.skin_suffix = suffix  # Update stored suffix

        # Get all transforms in the scene or use selected objects
        selected_objects = cmds.ls(selection=True, type='transform')
        objects_to_process = selected_objects if selected_objects else cmds.ls(type='transform')
        renamed_count = 0

        for obj in objects_to_process:
            history = cmds.listHistory(obj, pdo=True, interestLevel=1)
            if not history:
                continue

            for node in history:
                if cmds.nodeType(node) == "skinCluster":
                    # Handle namespace if present
                    namespace_parts = obj.split(":")
                    if len(namespace_parts) > 1:
                        base_name = namespace_parts[1]
                    else:
                        base_name = namespace_parts[0]

                    # Rename the skinCluster node
                    new_name = base_name + suffix
                    cmds.rename(node, new_name)
                    renamed_count += 1

        if renamed_count > 0:
            cmds.inViewMessage(
                amg=f"Renamed {renamed_count} skinCluster nodes with suffix: <hl>{suffix}</hl>",
                pos='midCenter',
                fade=True
            )
        else:
            cmds.warning("No skinCluster nodes found to rename.")


# Create and show the tool when script is executed
if __name__ == "__main__":
    tool = SkinWeightCopyTool()
    tool.create_ui()