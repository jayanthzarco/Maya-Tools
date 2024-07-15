# this script helps to name the multiple nodes at a same time
# code is created on 1-05-2021
# published 10-March-2024 by Jayanth
import maya.cmds as cmds

class RenameFunctions:
    @staticmethod
    def renaming_objects(new_name):
        selected_names = cmds.ls(sl=True)
        if "#" not in new_name and len(selected_names) == 1:
            cmds.rename(selected_names[0], new_name)
        elif "#" not in new_name and len(selected_names) >1 :
            return cmds.warning("# is not in the name please use the # ")
        else:
            split_name = new_name.split('#')
            padding = len(split_name) - 1
            hash_name = '#' * padding
            new_names = [new_name.replace(hash_name, str(i + 1).zfill(padding))
                         for i, old in enumerate(selected_names)]
            for old, new in zip(selected_names, new_names):
                cmds.rename(old, new)
                print(f"{old} renamed to --> {new}")
    @staticmethod
    def search_and_replace(search, replace):
        selected_objects = cmds.ls(sl=True)
        replaced_names = [name.replace(search, replace) for name in selected_objects]

        for old, new in zip(selected_objects, replaced_names):
            cmds.rename(old, new)
            print(f'{old} replaced with --> {new}')

    @staticmethod
    def add_prefix(prefix):
        selected_objects = cmds.ls(sl=True)
        new_names = [prefix + node for node in selected_objects]
        for p, n in zip(selected_objects, new_names):
            cmds.rename(p, n)
            print(f'{prefix} added to {p} --> {n}')

    @staticmethod
    def add_suffix(suffix):
        selected_objects = cmds.ls(sl=True)
        new_names = [node + suffix for node in selected_objects]
        for s, n in zip(selected_objects, new_names):
            cmds.rename(s, n)
            print(f'{suffix} added to {s} --> {n}')

class RenameUI(RenameFunctions):
    def __init__(self):
        self.name_TF = None
        self.search_TF = None
        self.replace_TF = None
        self.prefix_TF = None
        self.suffix_TF = None
        if cmds.window('RENAME_UI', exists=True):
            cmds.deleteUI('RENAME_UI')
        self.window_ui()

    def window_ui(self):

        cmds.window('RENAME_UI', title='JZ_Rename_Tool', sizeable=False,
                    width=500,height=105)

        cmds.columnLayout(adj=True)
        cmds.rowColumnLayout(numberOfColumns=2, adj=1)
        self.name_TF = cmds.textField(text='Prefix_Name_####_Suffix',
                                 width=350, h=25, font='boldLabelFont')
        cmds.button(l='Rename', width=150, h=25, c=self.rename_call)
        cmds.setParent('..')
        cmds.separator(height=10)
        cmds.rowColumnLayout(nc=4, adj=1)
        self.search_TF = cmds.textField(text='Search_for', font='boldLabelFont',
                                        width=150, height=25)
        cmds.text(label='--->', width=50)
        self.replace_TF = cmds.textField(text='Replace_with', font='boldLabelFont',
                                         width=150, height=25)
        cmds.button(label='Replace', width=150, c=self.search_and_replace_call)
        cmds.setParent('..')

        cmds.separator(height=10)

        cmds.rowColumnLayout(nc=5, adj=1)
        self.prefix_TF = cmds.textField(text='Prefix_', width=150, height=25,
                                        font='boldLabelFont')
        cmds.button(l='Add', width=75, c=self.prefix_call)

        cmds.text(label='|', width=50)
        self.suffix_TF = cmds.textField(text='_Suffix', width=150,
                                        font='boldLabelFont')
        cmds.button(label='Add', width=75, c=self.suffix_call)

        for each in range(3):
            cmds.separator(height=15)
        cmds.text(label='             |   Jayanth_Zarco', h=10,
                  font='boldLabelFont', noBackground=True)
        cmds.showWindow()

    def rename_call(self, *args):
        chosen_name = cmds.textField(self.name_TF, q=True, text=True)
        self.renaming_objects(new_name=chosen_name)

    def search_and_replace_call(self, *args):
        search_name = cmds.textField(self.search_TF, q=True, text=True)
        replace_name = cmds.textField(self.replace_TF, q=True, text=True)
        self.search_and_replace(search=search_name, replace=replace_name)

    def prefix_call(self, *args):
        prefix_name = cmds.textField(self.prefix_TF, q=True, text=True)
        self.add_prefix(prefix=prefix_name)

    def suffix_call(self, *args):
        suffix_name = cmds.textField(self.suffix_TF, q=True, text=True)
        self.add_suffix(suffix=suffix_name)


if __name__ == '__main__':
    win = RenameUI()

"""
created by Jayanth
"""