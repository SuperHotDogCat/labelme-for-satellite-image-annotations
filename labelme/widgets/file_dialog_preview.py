import json

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
import tifffile


class ScrollAreaPreview(QtWidgets.QScrollArea):
    def __init__(self, *args, **kwargs):
        super(ScrollAreaPreview, self).__init__(*args, **kwargs)

        self.setWidgetResizable(True)

        content = QtWidgets.QWidget(self)
        self.setWidget(content)

        lay = QtWidgets.QVBoxLayout(content)

        self.label = QtWidgets.QLabel(content)
        self.label.setWordWrap(True)

        lay.addWidget(self.label)

    def setText(self, text):
        self.label.setText(text)

    def setPixmap(self, pixmap):
        self.label.setPixmap(pixmap)

    def clear(self):
        self.label.clear()


class FileDialogPreview(QtWidgets.QFileDialog):
    def __init__(self, *args, **kwargs):
        super(FileDialogPreview, self).__init__(*args, **kwargs)
        self.setOption(self.DontUseNativeDialog, True)

        self.labelPreview = ScrollAreaPreview(self)
        self.labelPreview.setFixedSize(300, 300)
        self.labelPreview.setHidden(True)

        box = QtWidgets.QVBoxLayout()
        box.addWidget(self.labelPreview)
        box.addStretch()

        self.setFixedSize(self.width() + 300, self.height())
        self.layout().addLayout(box, 1, 3, 1, 1)
        self.currentChanged.connect(self.onChange)

    def onChange(self, path):
        if path.lower().endswith(".json"):
            with open(path, "r") as f:
                data = json.load(f)
                self.labelPreview.setText(json.dumps(data, indent=4, sort_keys=False))
            self.labelPreview.label.setAlignment(
                QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop
            )
            self.labelPreview.setHidden(False)
        else:
            pixmap = QtGui.QPixmap(path)
            if pixmap.isNull():
                self.labelPreview.clear()
                self.labelPreview.setHidden(True)
            else:
                self.labelPreview.setPixmap(
                    pixmap.scaled(
                        self.labelPreview.width() - 30,
                        self.labelPreview.height() - 30,
                        QtCore.Qt.KeepAspectRatio,
                        QtCore.Qt.SmoothTransformation,
                    )
                )
                self.labelPreview.label.setAlignment(QtCore.Qt.AlignCenter)
                self.labelPreview.setHidden(False)


class ChannelSelectionDialog(QtWidgets.QDialog):
    def __init__(self, filename, parent=None):
        super(ChannelSelectionDialog, self).__init__(parent)
        with tifffile.TiffFile(filename) as tif:
            image_array = tif.asarray()
            if image_array.ndim == 3:
                self.num_channels = image_array.shape[2]
            if image_array.ndim == 4:
                self.num_channels = image_array.shape[3]
            if image_array.ndim == 2:
                self.num_channels = 1
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Select RGB Channels")

        layout = QtWidgets.QFormLayout()

        # Create combo boxes for R, G, B channel selection
        self.r_channel_combo = QtWidgets.QComboBox()
        self.g_channel_combo = QtWidgets.QComboBox()
        self.b_channel_combo = QtWidgets.QComboBox()

        # Populate combo boxes with channel options
        for i in range(self.num_channels):
            self.r_channel_combo.addItem(f"Channel {i}", i)
            self.g_channel_combo.addItem(f"Channel {i}", i)
            self.b_channel_combo.addItem(f"Channel {i}", i)

        # Add combo boxes to layout
        layout.addRow("Red Channel:", self.r_channel_combo)
        layout.addRow("Green Channel:", self.g_channel_combo)
        layout.addRow("Blue Channel:", self.b_channel_combo)

        # Add buttons
        self.ok_button = QtWidgets.QPushButton("OK")
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        layout.addRow(self.ok_button, self.cancel_button)

        self.setLayout(layout)

        # Connect buttons to their actions
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_selected_channels(self):
        r_channel = self.r_channel_combo.currentData()
        g_channel = self.g_channel_combo.currentData()
        b_channel = self.b_channel_combo.currentData()
        return r_channel, g_channel, b_channel
