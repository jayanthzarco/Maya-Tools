import maya.cmds as cmds


class RenameFunctions:
    @staticmethod
    def renaming_objects(new_name):
        selected_names = cmds.ls(sl=True)
        if not selected_names:
            return cmds.warning("No objects selected. Please select objects to rename.")

        renamed_count = 0
        if "#" not in new_name and len(selected_names) == 1:
            new_obj = cmds.rename(selected_names[0], new_name)
            print(f"Renamed to: {new_name}")
            renamed_count = 1
            # Show viewport message
            cmds.inViewMessage(amg=f"Renamed: <hl>{selected_names[0]}</hl> → <hl>{new_obj}</hl>", pos='midCenter',
                               fade=True, fadeOutTime=1.5)
        elif "#" not in new_name and len(selected_names) > 1:
            return cmds.warning("# is not in the name. Please use # for sequential numbering.")
        else:
            split_name = new_name.split('#')
            padding = len(split_name) - 1
            hash_name = '#' * padding
            new_names = [new_name.replace(hash_name, str(i + 1).zfill(padding))
                         for i, old in enumerate(selected_names)]

            renamed_objects = []
            for old, new in zip(selected_names, new_names):
                renamed = cmds.rename(old, new)
                renamed_objects.append(renamed)
                print(f"{old} renamed to --> {renamed}")
                renamed_count += 1

            # Show viewport message for multiple objects
            if renamed_count > 0:
                if renamed_count == 1:
                    cmds.inViewMessage(amg=f"Renamed: <hl>{selected_names[0]}</hl> → <hl>{renamed_objects[0]}</hl>",
                                       pos='midCenter', fade=True, fadeOutTime=1.5)
                else:
                    cmds.inViewMessage(
                        amg=f"Renamed <hl>{renamed_count}</hl> objects with pattern: <hl>{new_name}</hl>",
                        pos='midCenter', fade=True, fadeOutTime=1.5)

        return renamed_count

    @staticmethod
    def search_and_replace(search, replace):
        selected_objects = cmds.ls(sl=True)
        if not selected_objects:
            return cmds.warning("No objects selected. Please select objects to rename.")

        replaced_names = []
        renamed_count = 0

        for old in selected_objects:
            if search in old:
                new = old.replace(search, replace)
                renamed = cmds.rename(old, new)
                replaced_names.append(renamed)
                print(f'{old} replaced with --> {renamed}')
                renamed_count += 1
            else:
                replaced_names.append(old)

        # Show viewport message
        if renamed_count > 0:
            if renamed_count == 1:
                cmds.inViewMessage(amg=f"Replaced: <hl>{search}</hl> → <hl>{replace}</hl> in 1 object",
                                   pos='midCenter', fade=True, fadeOutTime=1.5)
            else:
                cmds.inViewMessage(amg=f"Replaced: <hl>{search}</hl> → <hl>{replace}</hl> in {renamed_count} objects",
                                   pos='midCenter', fade=True, fadeOutTime=1.5)
        else:
            cmds.warning(f"'{search}' not found in any selected objects.")

        return renamed_count

    @staticmethod
    def add_prefix(prefix):
        selected_objects = cmds.ls(sl=True)
        if not selected_objects:
            return cmds.warning("No objects selected. Please select objects to rename.")

        renamed_count = 0
        renamed_objects = []

        for old in selected_objects:
            new = prefix + old
            renamed = cmds.rename(old, new)
            renamed_objects.append(renamed)
            print(f'{prefix} added to {old} --> {renamed}')
            renamed_count += 1

        # Show viewport message
        if renamed_count > 0:
            if renamed_count == 1:
                cmds.inViewMessage(amg=f"Added prefix <hl>{prefix}</hl> to 1 object",
                                   pos='midCenter', fade=True, fadeOutTime=1.5)
            else:
                cmds.inViewMessage(amg=f"Added prefix <hl>{prefix}</hl> to {renamed_count} objects",
                                   pos='midCenter', fade=True, fadeOutTime=1.5)

        return renamed_count

    @staticmethod
    def add_suffix(suffix):
        selected_objects = cmds.ls(sl=True)
        if not selected_objects:
            return cmds.warning("No objects selected. Please select objects to rename.")

        renamed_count = 0
        renamed_objects = []

        for old in selected_objects:
            new = old + suffix
            renamed = cmds.rename(old, new)
            renamed_objects.append(renamed)
            print(f'{suffix} added to {old} --> {renamed}')
            renamed_count += 1

        # Show viewport message
        if renamed_count > 0:
            if renamed_count == 1:
                cmds.inViewMessage(amg=f"Added suffix <hl>{suffix}</hl> to 1 object",
                                   pos='midCenter', fade=True, fadeOutTime=1.5)
            else:
                cmds.inViewMessage(amg=f"Added suffix <hl>{suffix}</hl> to {renamed_count} objects",
                                   pos='midCenter', fade=True, fadeOutTime=1.5)

        return renamed_count


class RenameUI(RenameFunctions):
    def __init__(self):
        self.name_TF = None
        self.search_TF = None
        self.replace_TF = None
        self.prefix_TF = None
        self.suffix_TF = None
        self.selection_label = None
        self.status_text = None
        self.window_name = 'JZ_RENAME_UI'

        # Close existing window if open
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)

        self.window_ui()

    def window_ui(self):
        # Create window
        cmds.window(self.window_name, title='JZ Rename Tool', sizeable=False, width=500, height=275)

        # Main layout
        main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=5)

        # Title section
        cmds.frameLayout(label="Multiple Object Renaming Tool", collapsable=False,
                         marginWidth=5, marginHeight=5, backgroundColor=[0.2, 0.2, 0.25],
                         labelVisible=True, borderStyle='etchedIn', font='boldLabelFont')

        # Selection indicator
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(100, 350), columnAlign=(1, 'right'))
        cmds.text(label="Selected: ", font="boldLabelFont")
        self.selection_label = cmds.text(label="0 objects", align="left")
        cmds.setParent('..')
        cmds.setParent('..')

        # Rename section
        cmds.frameLayout(label="Rename with Sequential Numbering", collapsable=False,
                         marginWidth=5, marginHeight=10, backgroundColor=[0.2, 0.2, 0.25],
                         borderStyle='etchedIn')

        cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
        cmds.text(label="Use # for numbering (e.g., Cube_### will become Cube_001, Cube_002...)", align="left")

        cmds.rowLayout(numberOfColumns=2, columnWidth2=(350, 150), adjustableColumn=1, columnAlign=(1, 'left'))
        self.name_TF = cmds.textField(text='Prefix_Name_###_Suffix', width=350, height=28, font='boldLabelFont')
        cmds.button(label='Rename', width=150, height=28, command=self.rename_call, backgroundColor=[0.2, 0.6, 0.8])
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.setParent('..')

        # Search and replace section
        cmds.frameLayout(label="Search and Replace", collapsable=False,
                         marginWidth=5, marginHeight=10, backgroundColor=[0.2, 0.2, 0.25],
                         borderStyle='etchedIn')

        cmds.rowLayout(numberOfColumns=4, columnWidth4=(150, 50, 150, 150), adjustableColumn=3,
                       columnAlign=(1, 'left'), columnAttach=[(1, 'left', 5), (4, 'right', 5)])
        self.search_TF = cmds.textField(text='Search_for', font='obliqueLabelFont', width=150, height=28)
        cmds.text(label='--->', width=50, align='center')
        self.replace_TF = cmds.textField(text='Replace_with', font='obliqueLabelFont', width=150, height=28)
        cmds.button(label='Replace', width=150, height=28, command=self.search_and_replace_call,
                    backgroundColor=[0.6, 0.6, 0.8])
        cmds.setParent('..')
        cmds.setParent('..')

        # Prefix/Suffix section
        cmds.frameLayout(label="Add Prefix or Suffix", collapsable=False,
                         marginWidth=5, marginHeight=10, backgroundColor=[0.2, 0.2, 0.25],
                         borderStyle='etchedIn')

        cmds.rowLayout(numberOfColumns=5, columnWidth5=(150, 75, 50, 150, 75),
                       columnAlign=(1, 'left'), columnAttach=[(1, 'left', 5), (5, 'right', 5)])
        self.prefix_TF = cmds.textField(text='Prefix_', width=150, height=28, font='obliqueLabelFont')
        cmds.button(label='Add', width=75, height=28, command=self.prefix_call, backgroundColor=[0.8, 0.4, 0.4])
        cmds.text(label='|', width=50, align='center')
        self.suffix_TF = cmds.textField(text='_Suffix', width=150, height=28, font='obliqueLabelFont')
        cmds.button(label='Add', width=75, height=28, command=self.suffix_call, backgroundColor=[0.4, 0.8, 0.4])
        cmds.setParent('..')
        cmds.setParent('..')

        # Status bar
        cmds.frameLayout(label="", labelVisible=False, collapsable=False,
                         marginWidth=5, marginHeight=5, borderStyle='etchedIn')
        self.status_text = cmds.text(label="Ready", align="center", width=500)
        cmds.setParent('..')

        # Footer
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(150, 200, 150), adjustableColumn=2,
                       columnAlign2=('left', 'center'))
        cmds.text(label="")
        cmds.text(label='Created by Jayanth Zarco', align='center', font='smallBoldLabelFont')
        cmds.button(label='Refresh Selection', width=120, height=24, command=self.refresh_selection,
                    backgroundColor=[0.35, 0.35, 0.35])
        cmds.setParent('..')

        # Display the window
        cmds.showWindow(self.window_name)

        # Update selection count at startup
        self.refresh_selection()

        # Add script job to update selection count when selection changes
        cmds.scriptJob(event=["SelectionChanged", self.refresh_selection], parent=self.window_name)

    def refresh_selection(self, *args):
        """Update the selection count label"""
        selection = cmds.ls(selection=True)
        count = len(selection)
        if count == 0:
            cmds.text(self.selection_label, edit=True, label="0 objects")
            cmds.text(self.status_text, edit=True, label="Ready - Select objects to rename")
        elif count == 1:
            cmds.text(self.selection_label, edit=True, label=f"1 object: {selection[0]}")
            cmds.text(self.status_text, edit=True, label=f"Selected: {selection[0]}")
        else:
            cmds.text(self.selection_label, edit=True, label=f"{count} objects selected")
            cmds.text(self.status_text, edit=True, label=f"Selected {count} objects - Ready for renaming")

    def rename_call(self, *args):
        chosen_name = cmds.textField(self.name_TF, query=True, text=True)
        count = self.renaming_objects(new_name=chosen_name)

        if count:
            cmds.text(self.status_text, edit=True, label=f"Renamed {count} objects with pattern: {chosen_name}")

        self.refresh_selection()

    def search_and_replace_call(self, *args):
        search_name = cmds.textField(self.search_TF, query=True, text=True)
        replace_name = cmds.textField(self.replace_TF, query=True, text=True)
        count = self.search_and_replace(search=search_name, replace=replace_name)

        if count:
            cmds.text(self.status_text, edit=True,
                      label=f"Replaced '{search_name}' with '{replace_name}' in {count} objects")
        else:
            cmds.text(self.status_text, edit=True, label=f"'{search_name}' not found in selection")

        self.refresh_selection()

    def prefix_call(self, *args):
        prefix_name = cmds.textField(self.prefix_TF, query=True, text=True)
        count = self.add_prefix(prefix=prefix_name)

        if count:
            cmds.text(self.status_text, edit=True, label=f"Added prefix '{prefix_name}' to {count} objects")

        self.refresh_selection()

    def suffix_call(self, *args):
        suffix_name = cmds.textField(self.suffix_TF, query=True, text=True)
        count = self.add_suffix(suffix=suffix_name)

        if count:
            cmds.text(self.status_text, edit=True, label=f"Added suffix '{suffix_name}' to {count} objects")

        self.refresh_selection()


if __name__ == '__main__':
    win = RenameUI()