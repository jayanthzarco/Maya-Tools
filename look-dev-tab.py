import maya.cmds as cmds
import maya.mel as mel


def delete_lookdev_graph_editor_tabs():
    """
    Delete all tabs in the Look Dev Graph Editor in Maya.
    This script accesses the graph editor panel tabs and removes them.
    """
    try:
        # First check if the lookDevEditor exists
        if not cmds.workspaceControl("lookDevEditor", exists=True):
            print("Look Dev Graph Editor is not currently open.")
            return

        # Get the graph editor panel name
        graph_editor_panel = mel.eval('$tmp = $gLookDevGraphEditorPanel')

        if not graph_editor_panel or not cmds.panel(graph_editor_panel, exists=True):
            print("Could not access the Look Dev Graph Editor panel.")
            return

        # Get all tabs in the graph editor
        tabs = cmds.tabLayout(graph_editor_panel + "Tab", query=True, childArray=True)

        if not tabs:
            print("No tabs found in the Look Dev Graph Editor.")
            return

        # Store the number of tabs for reporting
        num_tabs = len(tabs)

        # Delete each tab
        for tab in tabs:
            try:
                # Close he tab - different approaches depending on Maya version
                if cmds.control(tab, exists=True):
                    # Try to use the closeTab command if available
                    try:
                        mel.eval(f'lookDevGraphEditorCloseTab("{tab}")')
                    except:
                        # Fallback method: delete the control
                        cmds.deleteUI(tab)
            except Exception as e:
                print(f"Error deleting tab {tab}: {str(e)}")

        print(f"Successfully deleted {num_tabs} tabs from the Look Dev Graph Editor.")

    except Exception as e:
        print(f"Error: {str(e)}")


# Execute the function
delete_lookdev_graph_editor_tabs()