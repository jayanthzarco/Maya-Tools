from PySide2 import QtWidgets, QtCore
from maya import cmds
import maya.OpenMayaUI as omui
import shiboken2


def get_maya_window():
    ptr = omui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(int(ptr), QtWidgets.QWidget)


class AnimTransferUI(QtWidgets.QDialog):
    def __init__(self, parent=get_maya_window()):
        super(AnimTransferUI, self).__init__(parent)
        self.setWindowTitle("Animation Transfer Tool")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.build_ui()

    def build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        # Load buttons and hierarchy checkboxes
        load_layout = QtWidgets.QHBoxLayout()
        self.source_hierarchy = QtWidgets.QCheckBox("Hierarchy")
        self.target_hierarchy = QtWidgets.QCheckBox("Hierarchy")
        self.load_source_btn = QtWidgets.QPushButton("Load Source")
        self.load_target_btn = QtWidgets.QPushButton("Load Target")
        self.load_source_btn.clicked.connect(self.load_source)
        self.load_target_btn.clicked.connect(self.load_target)

        load_layout.addWidget(self.load_source_btn)
        load_layout.addWidget(self.source_hierarchy)
        load_layout.addStretch()
        load_layout.addWidget(self.load_target_btn)
        load_layout.addWidget(self.target_hierarchy)
        main_layout.addLayout(load_layout)

        # Source and Target lists with their respective clear buttons
        list_layout = QtWidgets.QHBoxLayout()

        # Source list and buttons in a vertical layout
        source_column = QtWidgets.QVBoxLayout()
        self.source_list = QtWidgets.QListWidget()
        self.source_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        source_column.addWidget(self.source_list)

        # Buttons under source list
        source_btns = QtWidgets.QHBoxLayout()
        source_clear_selected = QtWidgets.QPushButton("Clear Selected")
        source_clear_all = QtWidgets.QPushButton("Clear All")
        source_clear_selected.clicked.connect(self.clear_selected_source)
        source_clear_all.clicked.connect(self.clear_all_source)
        source_btns.addWidget(source_clear_selected)
        source_btns.addWidget(source_clear_all)
        source_column.addLayout(source_btns)

        # Target list and buttons in a vertical layout
        target_column = QtWidgets.QVBoxLayout()
        self.target_list = QtWidgets.QListWidget()
        self.target_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        target_column.addWidget(self.target_list)

        # Buttons under target list
        target_btns = QtWidgets.QHBoxLayout()
        target_clear_selected = QtWidgets.QPushButton("Clear Selected")
        target_clear_all = QtWidgets.QPushButton("Clear All")
        target_clear_selected.clicked.connect(self.clear_selected_target)
        target_clear_all.clicked.connect(self.clear_all_target)
        target_btns.addWidget(target_clear_selected)
        target_btns.addWidget(target_clear_all)
        target_column.addLayout(target_btns)

        # Add the columns to the list layout
        list_layout.addLayout(source_column)
        list_layout.addWidget(QtWidgets.QLabel("→"))
        list_layout.addLayout(target_column)

        main_layout.addLayout(list_layout)

        # Progress bar
        self.progress_bar = QtWidgets.QProgressBar()
        main_layout.addWidget(self.progress_bar)

        # Transfer buttons
        btn_layout = QtWidgets.QHBoxLayout()
        self.transfer_selected_btn = QtWidgets.QPushButton("Transfer Selected")
        self.transfer_all_btn = QtWidgets.QPushButton("Transfer All")
        self.transfer_selected_btn.clicked.connect(self.transfer_selected)
        self.transfer_all_btn.clicked.connect(self.transfer_all)
        btn_layout.addWidget(self.transfer_selected_btn)
        btn_layout.addWidget(self.transfer_all_btn)
        main_layout.addLayout(btn_layout)

    def load_source(self):
        self.source_list.clear()
        if self.source_hierarchy.isChecked():
            input_items = self.get_selection()
        else:
            input_items = cmds.ls(sl=True)
        self.source_list.addItems(input_items)

    def load_target(self):
        self.target_list.clear()
        if self.target_hierarchy.isChecked():
            input_items = self.get_selection()
        else:
            input_items = cmds.ls(sl=True)
        self.target_list.addItems(input_items)

    @staticmethod
    def get_selection():
        selection = []
        selected = cmds.ls(sl=True)
        if not selected:
            print("Select something, dude...")
            return []
        for each in selected:
            cmds.select(cl=True)
            cmds.select(each, hierarchy=True)
            all_objects = cmds.ls(sl=True)
            selection.extend(all_objects)
            cmds.select(cl=True)
        return selection

    def clear_selected_source(self):
        for item in self.source_list.selectedItems():
            self.source_list.takeItem(self.source_list.row(item))

    def clear_all_source(self):
        self.source_list.clear()

    def clear_selected_target(self):
        for item in self.target_list.selectedItems():
            self.target_list.takeItem(self.target_list.row(item))

    def clear_all_target(self):
        self.target_list.clear()

    def get_selected_pairs(self):
        source_items = self.source_list.selectedItems()
        target_items = self.target_list.selectedItems()
        return [(source_items[i].text(), target_items[i].text()) for i in
                range(min(len(source_items), len(target_items)))]

    def get_all_pairs(self):
        count = min(self.source_list.count(), self.target_list.count())
        return [(self.source_list.item(i).text(), self.target_list.item(i).text()) for i in range(count)]

    def transfer_selected(self):
        pairs = self.get_selected_pairs()
        self.transfer_animation(pairs)

    def transfer_all(self):
        pairs = self.get_all_pairs()
        self.transfer_animation(pairs)

    def transfer_animation(self, pairs):
        total = len(pairs)
        if total == 0:
            cmds.warning("No matching pairs to transfer.")
            return
        for i, (src, tgt) in enumerate(pairs):
            self.progress_bar.setValue(int((i / total) * 100))
            try:
                self.copy_anim_keys(src, tgt)
            except Exception as e:
                cmds.warning(f"Failed copying {src} → {tgt}: {e}")
        self.progress_bar.setValue(100)

    def copy_anim_keys(self, source, target):
        attrs = cmds.listAnimatable(source)
        if not attrs:
            return
        for attr in attrs:
            attr_name = attr.split(".")[-1]
            if cmds.objExists(f"{target}.{attr_name}"):
                cmds.copyKey(source, at=attr_name)
                cmds.pasteKey(target, at=attr_name, option="replace")


def launch_anim_transfer_ui():
    global anim_tool_ui
    try:
        anim_tool_ui.close()
    except:
        pass
    anim_tool_ui = AnimTransferUI()
    anim_tool_ui.show()


launch_anim_transfer_ui()