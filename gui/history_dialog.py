# gui/history_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QListWidget, QListWidgetItem, QWidget,
                              QSplitter, QTextBrowser, QDialogButtonBox)
from PySide6.QtCore import Qt
import json
import os

class ChangeHistoryDialog(QDialog):
    def __init__(self, repo_path, parent=None):
        super().__init__(parent)
        self.repo_path = repo_path
        self.history = []
        self.selected_changes = None

        self.setWindowTitle("Change History")
        self.setMinimumSize(800, 500)

        self.load_history()
        self.setup_ui()

    def load_history(self):
        """Load change history from file"""
        history_path = os.path.join(self.repo_path, '.git', 'change_history.json')

        if os.path.exists(history_path):
            try:
                with open(history_path, 'r') as f:
                    self.history = json.load(f)
            except Exception as e:
                print(f"Error loading history: {str(e)}")
                self.history = []
        else:
            self.history = []

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Create splitter for two-pane view
        splitter = QSplitter(Qt.Horizontal)

        # Left pane: History list
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)

        history_label = QLabel("Change History:")
        history_layout.addWidget(history_label)

        self.history_list = QListWidget()
        for entry in self.history:
            timestamp = entry['timestamp']
            total = entry['summary']['total']
            item_text = f"{timestamp} - {total} changes"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, entry)
            self.history_list.addItem(item)

        self.history_list.currentItemChanged.connect(self.on_history_item_selected)
        history_layout.addWidget(self.history_list)

        # Right pane: Details view
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)

        details_label = QLabel("Change Details:")
        details_layout.addWidget(details_label)

        self.details_view = QTextBrowser()
        details_layout.addWidget(self.details_view)

        # Add widgets to splitter
        splitter.addWidget(history_widget)
        splitter.addWidget(details_widget)
        splitter.setSizes([300, 500])  # Initial sizes

        layout.addWidget(splitter)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)

        view_button = QPushButton("View Selected Changes")
        view_button.clicked.connect(self.view_selected_changes)
        button_box.addButton(view_button, QDialogButtonBox.ActionRole)

        layout.addWidget(button_box)

    def on_history_item_selected(self, current, previous):
        """Handle selection of history item"""
        if not current:
            self.details_view.clear()
            self.selected_changes = None
            return

        # Get entry data
        entry = current.data(Qt.UserRole)
        self.selected_changes = entry['changes']

        # Display details
        details = f"<h3>Changes from {entry['timestamp']}</h3>"
        details += f"<p>Total changes: {entry['summary']['total']}</p>"

        details += f"<h4>Added Files ({entry['summary']['added']}):</h4>"
        if entry['changes']['added']:
            details += "<ul>"
            for file in entry['changes']['added']:
                details += f"<li>{file}</li>"
            details += "</ul>"
        else:
            details += "<p>No files added</p>"

        details += f"<h4>Modified Files ({entry['summary']['modified']}):</h4>"
        if entry['changes']['modified']:
            details += "<ul>"
            for file in entry['changes']['modified']:
                details += f"<li>{file}</li>"
            details += "</ul>"
        else:
            details += "<p>No files modified</p>"

        details += f"<h4>Deleted Files ({entry['summary']['deleted']}):</h4>"
        if entry['changes']['deleted']:
            details += "<ul>"
            for file in entry['changes']['deleted']:
                details += f"<li>{file}</li>"
            details += "</ul>"
        else:
            details += "<p>No files deleted</p>"

        self.details_view.setHtml(details)

    def view_selected_changes(self):
        """View selected changes in change details dialog"""
        if not self.selected_changes:
            return

        from gui.change_dialog import ChangeDetailsDialog
        dialog = ChangeDetailsDialog(self.selected_changes, self)
        dialog.exec()
