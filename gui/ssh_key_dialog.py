# gui/ssh_key_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QLineEdit, QDialogButtonBox, QFileDialog)
from PySide6.QtCore import Qt
import os

from gui.animated_dialog import AnimatedDialog

class SSHKeyDialog(AnimatedDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SSH Key Configuration")
        self.setMinimumSize(500, 200)
        self.ssh_key_path = ""

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header_label = QLabel("Configure SSH key for authentication:")
        header_label.setWordWrap(True)
        layout.addWidget(header_label)

        # Key path input
        key_layout = QHBoxLayout()

        key_layout.addWidget(QLabel("Private Key Path:"))

        self.key_path_edit = QLineEdit()
        self.key_path_edit.setPlaceholderText("Path to your SSH private key...")

        # Set default path if exists
        default_key_path = os.path.expanduser("~/.ssh/id_rsa")
        if os.path.exists(default_key_path):
            self.key_path_edit.setText(default_key_path)
            self.ssh_key_path = default_key_path

        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_key)

        key_layout.addWidget(self.key_path_edit, 1)  # 1 = stretch factor
        key_layout.addWidget(browse_button)

        layout.addLayout(key_layout)

        # Help text
        help_label = QLabel("Note: The SSH key will be used for authentication with the remote repository. "
                            "Make sure the public key is added to your Git hosting service (GitHub, GitLab, etc.).")
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: gray; font-size: 10pt;")
        layout.addWidget(help_label)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_key)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def browse_key(self):
        """Browse for SSH key file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select SSH Private Key",
            os.path.expanduser("~/.ssh"),
            "All Files (*)"
        )

        if file_path:
            self.key_path_edit.setText(file_path)

    def accept_key(self):
        """Accept the key path"""
        self.ssh_key_path = self.key_path_edit.text()
        if not self.ssh_key_path:
            return  # Don't accept empty path

        self.accept()

    def get_ssh_key_path(self):
        """Return the SSH key path"""
        return self.ssh_key_path
