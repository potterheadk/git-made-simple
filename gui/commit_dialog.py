# gui/commit_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QTextEdit, QLineEdit, QDialogButtonBox,
                              QCheckBox)
from PySide6.QtCore import Qt
from datetime import datetime

from gui.animated_dialog import AnimatedDialog

class CommitDialog(AnimatedDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Commit Changes")
        self.setMinimumSize(500, 300)
        self.commit_message = ""
        self.add_timestamp = True

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header_label = QLabel("Enter a commit message for your changes:")
        header_label.setWordWrap(True)
        layout.addWidget(header_label)

        # Commit message input
        self.message_edit = QTextEdit()
        self.message_edit.setPlaceholderText("Describe your changes here...")
        layout.addWidget(self.message_edit)

        # Timestamp option
        timestamp_layout = QHBoxLayout()
        self.timestamp_checkbox = QCheckBox("Add timestamp to commit message")
        self.timestamp_checkbox.setChecked(True)
        timestamp_layout.addWidget(self.timestamp_checkbox)
        timestamp_layout.addStretch()
        layout.addLayout(timestamp_layout)

        # Example of how the message will look
        self.example_label = QLabel()
        self.update_example()
        self.message_edit.textChanged.connect(self.update_example)
        self.timestamp_checkbox.stateChanged.connect(self.update_example)
        layout.addWidget(self.example_label)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_commit)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def update_example(self):
        """Update the example commit message"""
        message = self.message_edit.toPlainText()
        if not message:
            message = "Describe your changes here..."

        if self.timestamp_checkbox.isChecked():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            example = f"{message} - {timestamp}"
        else:
            example = message

        self.example_label.setText(f"Example: {example}")

    def accept_commit(self):
        """Accept the commit message"""
        message = self.message_edit.toPlainText()
        if not message.strip():
            message = "Backup commit"

        if self.timestamp_checkbox.isChecked():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.commit_message = f"{message} - {timestamp}"
        else:
            self.commit_message = message

        self.add_timestamp = self.timestamp_checkbox.isChecked()
        self.accept()

    def get_commit_message(self):
        """Return the commit message"""
        return self.commit_message
