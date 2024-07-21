# creating custom side bar for all tools in maya
# Wip :last updated 21-07-2024

import maya.cmds as cmds

class ZarcoMenuBar:
    def __init__(self):
        if cmds.menu('_zarco_menu', exists=True):
            cmds.deleteUI('_zarco_menu', menu=True)
        self.menu = None
        self.zarco_menubar()

    def zarco_menubar(self):
        self.menu = cmds.menu('_zarco_menu_', label='zarco_menu', parent='MayaWindow', tearOff=True)
        # adding menu items
        cmds.menuItem(label='Auto_Rig', parent=self.menu, command=lambda *args:self._auto_rig())
        cmds.menuItem(label='JZ_Renamer', parent=self.menu, command=lambda *args: self._jz_renamer())
        cmds.menuItem(label='Scene_Optimizer', parent=self.menu, command=lambda *args: self._scene_optimizer())
        cmds.menuItem(label='Quick_Renderer', parent=self.menu, command=lambda *args: self._quick_renderer())
        cmds.menuItem(label='Duplicate_Node_Renamer', parent=self.menu, command=lambda *args: self._duplicate_node_renamer())

    @staticmethod
    def _auto_rig():
        print("calling Auto Rig")

    @staticmethod
    def _jz_renamer():
        print("calling JZ_Renamer")

    @staticmethod
    def _scene_optimizer():
        print("calling Scene Optimizer")

    @staticmethod
    def _quick_renderer():
        print("calling Quick Renderer")

    @staticmethod
    def _duplicate_node_renamer():
        print("calling Duplicate Node Renamer")


if __name__ == '__main__':
    _run = ZarcoMenuBar()
