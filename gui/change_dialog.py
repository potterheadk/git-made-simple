# gui/change_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QListWidget, QTabWidget, QWidget,
                              QDialogButtonBox, QTextBrowser)
from PySide6.QtCore import Qt

class ChangeDetailsDialog(QDialog):
    def __init__(self, changes, parent=None):
        super().__init__(parent)
        self.changes = changes
        self.setWindowTitle("File Changes")
        self.setMinimumSize(600, 500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Summary label
        total_changes = (len(self.changes['added']) +
                         len(self.changes['modified']) +
                         len(self.changes['deleted']))
        summary = QLabel(f"Total changes: {total_changes}")
        layout.addWidget(summary)

        # Create tabs for different change types
        tabs = QTabWidget()

        # Added files tab
        added_tab = QWidget()
        added_layout = QVBoxLayout(added_tab)

        # Add counter label
        added_layout.addWidget(QLabel(f"Added files: {len(self.changes['added'])}"))

        # Use QTextBrowser instead of QListWidget for better display
        added_list = QTextBrowser()
        added_text = "\n".join(self.changes['added']) if self.changes['added'] else "No files added"
        added_list.setText(added_text)
        added_layout.addWidget(added_list)

        tabs.addTab(added_tab, f"Added ({len(self.changes['added'])})")

        # Modified files tab
        modified_tab = QWidget()
        modified_layout = QVBoxLayout(modified_tab)

        # Add counter label
        modified_layout.addWidget(QLabel(f"Modified files: {len(self.changes['modified'])}"))

        modified_list = QTextBrowser()
        modified_text = "\n".join(self.changes['modified']) if self.changes['modified'] else "No files modified"
        modified_list.setText(modified_text)
        modified_layout.addWidget(modified_list)

        tabs.addTab(modified_tab, f"Modified ({len(self.changes['modified'])})")

        # Deleted files tab
        deleted_tab = QWidget()
        deleted_layout = QVBoxLayout(deleted_tab)

        # Add counter label
        deleted_layout.addWidget(QLabel(f"Deleted files: {len(self.changes['deleted'])}"))

        deleted_list = QTextBrowser()
        deleted_text = "\n".join(self.changes['deleted']) if self.changes['deleted'] else "No files deleted"
        deleted_list.setText(deleted_text)
        deleted_layout.addWidget(deleted_list)

        tabs.addTab(deleted_tab, f"Deleted ({len(self.changes['deleted'])})")

        layout.addWidget(tabs)

        # Add debug information
        debug_info = QTextBrowser()
        debug_info.setText(f"Debug Info:\n" +
                           f"Added files count: {len(self.changes['added'])}\n" +
                           f"Modified files count: {len(self.changes['modified'])}\n" +
                           f"Deleted files count: {len(self.changes['deleted'])}")
        layout.addWidget(debug_info)

        # Add OK button
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
