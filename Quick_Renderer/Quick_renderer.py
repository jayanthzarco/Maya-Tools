from PySide2 import QtWidgets, QtCore
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
import os


class RenderWindow(QtWidgets.QWidget):
    def __init__(self):
        super(RenderWindow, self).__init__()

        # Set up the window
        self.setWindowTitle("Camera Renderer")
        self.setGeometry(100, 100, 400, 200)

        # Layout
        layout = QtWidgets.QVBoxLayout()

        # Camera dropdown
        self.camera_combo = QtWidgets.QComboBox()
        self.populate_cameras()
        layout.addWidget(QtWidgets.QLabel("Select Camera:"))
        layout.addWidget(self.camera_combo)

        # Render options
        self.single_frame_radio = QtWidgets.QRadioButton("Single Frame")
        self.time_range_radio = QtWidgets.QRadioButton("Time Range")
        self.single_frame_radio.setChecked(True)

        render_options_layout = QtWidgets.QHBoxLayout()
        render_options_layout.addWidget(self.single_frame_radio)
        render_options_layout.addWidget(self.time_range_radio)

        layout.addWidget(QtWidgets.QLabel("Render Options:"))
        layout.addLayout(render_options_layout)

        # Output path
        self.output_path_edit = QtWidgets.QLineEdit()
        self.output_path_edit.setPlaceholderText("Select output path")
        self.browse_button = QtWidgets.QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_output_path)

        path_layout = QtWidgets.QHBoxLayout()
        path_layout.addWidget(self.output_path_edit)
        path_layout.addWidget(self.browse_button)

        layout.addLayout(path_layout)

        # Render button
        self.render_button = QtWidgets.QPushButton("Render")
        self.render_button.clicked.connect(self.render_camera)
        layout.addWidget(self.render_button)

        self.setLayout(layout)

    def populate_cameras(self):
        """Populates the camera dropdown with all cameras in the scene."""
        cameras = cmds.ls(type='camera')
        self.camera_combo.addItems(cameras)

    def browse_output_path(self):
        """Opens a file dialog to select the output path."""
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_path_edit.setText(directory)

    def render_camera(self):
        """Renders the selected camera based on the chosen render option."""
        selected_camera = self.camera_combo.currentText()
        output_directory = self.output_path_edit.text()

        if not output_directory:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select an output directory.")
            return

        if self.single_frame_radio.isChecked():
            # Render single frame
            current_frame = cmds.currentTime(query=True)
            self.render_single_frame(selected_camera, output_directory, current_frame)
        else:
            # Render time range
            start_frame = cmds.playbackOptions(query=True, minTime=True)
            end_frame = cmds.playbackOptions(query=True, maxTime=True)
            self.render_time_range(selected_camera, output_directory, start_frame, end_frame)

    def render_single_frame(self, camera, output_directory, frame):
        """Renders a single frame."""
        camera_transform = cmds.listRelatives(camera, parent=True)[0]
        cmds.lookThru(camera_transform)
        cmds.setAttr("defaultRenderGlobals.startFrame", frame)
        cmds.setAttr("defaultRenderGlobals.endFrame", frame)
        cmds.setAttr("defaultRenderGlobals.imageFilePrefix",
                     os.path.join(output_directory, "<Scene>_<RenderLayer>_<Camera>_<RenderPass>"))
        cmds.render(camera_transform)
        cmds.batchRender()

    def render_time_range(self, camera, output_directory, start_frame, end_frame):
        """Renders a time range."""
        camera_transform = cmds.listRelatives(camera, parent=True)[0]
        cmds.lookThru(camera_transform)
        cmds.setAttr("defaultRenderGlobals.startFrame", start_frame)
        cmds.setAttr("defaultRenderGlobals.endFrame", end_frame)
        cmds.setAttr("defaultRenderGlobals.animation", 1)
        cmds.setAttr("defaultRenderGlobals.imageFilePrefix",
                     os.path.join(output_directory, "<Scene>_<RenderLayer>_<Camera>_<RenderPass>"))
        cmds.batchRender()


# Function to get Maya's main window
def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


# Create and display the window
try:
    render_window.close()  # Close existing window if open
except:
    pass

if __name__ == '__main__':
    parent = get_maya_main_window()
    render_window = RenderWindow()
    render_window.setParent(parent, QtCore.Qt.Window)
    render_window.show()
