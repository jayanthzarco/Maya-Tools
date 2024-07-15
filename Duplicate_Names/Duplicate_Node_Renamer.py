# this tool loads the all the nodes with same name and helps to rename them

import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore
import maya.OpenMayaUI as omui
import shiboken2


class DuplicateNodeRenamerUI(QtWidgets.QWidget):
    def __init__(self):
        super(DuplicateNodeRenamerUI, self).__init__()
        self.setWindowTitle("Duplicate Node Renamer")
        self.setMinimumWidth(350)
        self.setMinimumHeight(250)

        self.layout = QtWidgets.QVBoxLayout()

        self.node_list_widget = QtWidgets.QListWidget()
        self.layout.addWidget(self.node_list_widget)

        self.checkbox_layout = QtWidgets.QVBoxLayout()

        self.refresh_button = QtWidgets.QPushButton("Refresh List")
        self.refresh_button.clicked.connect(self.refresh_list)
        self.layout.addWidget(self.refresh_button)

        self.rename_selected_button = QtWidgets.QPushButton("Rename Selected")
        self.rename_selected_button.clicked.connect(self.rename_selected)
        self.layout.addWidget(self.rename_selected_button)

        self.rename_all_button = QtWidgets.QPushButton("Rename All")
        self.rename_all_button.clicked.connect(self.rename_all)
        self.layout.addWidget(self.rename_all_button)

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(self.layout)
        main_layout.addLayout(self.checkbox_layout)
        self.setLayout(main_layout)

        self.refresh_list()

    def refresh_list(self):
        self.node_list_widget.clear()
        self.checkbox_layout = QtWidgets.QVBoxLayout()

        # Get all nodes in the scene
        all_nodes = cmds.ls(dag=True, long=True)
        node_counts = {}

        # Count occurrences of each node name
        for node in all_nodes:
            node_name = node.split('|')[-1]
            if node_name in node_counts:
                node_counts[node_name].append(node)
            else:
                node_counts[node_name] = [node]

        # Add duplicate node names to the UI list and create checkboxes
        for name, nodes in node_counts.items():
            if len(nodes) > 1:
                item = QtWidgets.QListWidgetItem(name)
                self.node_list_widget.addItem(item)

                checkbox_layout = QtWidgets.QHBoxLayout()
                checkbox = QtWidgets.QCheckBox()
                checkbox_layout.addWidget(checkbox)
                checkbox_layout.addWidget(QtWidgets.QLabel(name))
                self.checkbox_layout.addLayout(checkbox_layout)

    def rename_selected(self):
        selected_items = self.node_list_widget.selectedItems()

        for index in range(self.checkbox_layout.count()):
            checkbox_layout = self.checkbox_layout.itemAt(index)
            checkbox = checkbox_layout.itemAt(0).widget()
            if checkbox.isChecked():
                name = self.node_list_widget.item(index).text()
                nodes_to_rename = cmds.ls(name, long=True)
                for i, node in enumerate(nodes_to_rename):
                    new_name = "{}_{}".format(node.split('|')[-1], i + 1)
                    cmds.rename(node, new_name)
                    print("Renamed {} to {}".format(node, new_name))

        self.refresh_list()

    def rename_all(self):
        for index in range(self.node_list_widget.count()):
            item = self.node_list_widget.item(index)
            name = item.text()
            nodes_to_rename = cmds.ls(name, long=True)
            for i, node in enumerate(nodes_to_rename):
                new_name = "{}_{}".format(node.split('|')[-1], i + 1)
                cmds.rename(node, new_name)
                print("Renamed {} to {}".format(node, new_name))

        self.refresh_list()

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


if __name__ == "__main__":
    try:
        duplicate_node_renamer_ui.close()
        duplicate_node_renamer_ui.deleteLater()
    except:
        pass

    duplicate_node_renamer_ui = DuplicateNodeRenamerUI()
    duplicate_node_renamer_ui.show()
    duplicate_node_renamer_ui.setParent(maya_main_window())

"""
Created By Jayanth
"""
