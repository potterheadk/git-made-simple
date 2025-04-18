# gui/branch_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QListWidget, QListWidgetItem, QInputDialog,
                              QMessageBox, QDialogButtonBox, QGroupBox, QRadioButton)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from gui.animated_dialog import AnimatedDialog

class BranchDialog(AnimatedDialog):
    def __init__(self, git_manager, parent=None):
        super().__init__(parent)
        self.git_manager = git_manager
        self.selected_branch = None

        self.setWindowTitle("Branch Management")
        self.setMinimumSize(500, 400)

        self.setup_ui()
        self.load_branches()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header with explanation
        header_label = QLabel("Select a branch to work with or create a new branch.")
        header_label.setWordWrap(True)
        layout.addWidget(header_label)

        # Current branch label
        try:
            current_branch = self.git_manager.get_current_branch()
            self.current_branch_label = QLabel(f"Current branch: <b>{current_branch}</b>")
        except:
            self.current_branch_label = QLabel("Current branch: <i>Unknown</i>")
        layout.addWidget(self.current_branch_label)

        # Branch list
        branches_group = QGroupBox("Available Branches")
        branches_layout = QVBoxLayout(branches_group)

        self.branch_list = QListWidget()
        self.branch_list.itemDoubleClicked.connect(self.checkout_selected_branch)
        branches_layout.addWidget(self.branch_list)

        # Add fetch button
        fetch_button = QPushButton("Fetch from Remote")
        fetch_button.clicked.connect(self.fetch_remote)
        branches_layout.addWidget(fetch_button)

        layout.addWidget(branches_group, 1)  # 1 = stretch factor

        # Buttons for branch operations
        buttons_layout = QHBoxLayout()

        self.create_button = QPushButton("Create New Branch")
        self.create_button.clicked.connect(self.create_branch)

        self.checkout_button = QPushButton("Checkout Branch")
        self.checkout_button.clicked.connect(self.checkout_selected_branch)

        buttons_layout.addWidget(self.create_button)
        buttons_layout.addWidget(self.checkout_button)

        layout.addLayout(buttons_layout)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    # Add the fetch_remote method:
    def fetch_remote(self):
        """Fetch updates from remote repositories"""
        try:
            if not self.git_manager.repo or not self.git_manager.repo.remotes:
                QMessageBox.warning(
                    self,
                    "No Remotes",
                    "No remote repositories configured.",
                    QMessageBox.Ok
                )
                return

            for remote in self.git_manager.repo.remotes:
                try:
                    QMessageBox.information(
                        self,
                        "Fetching",
                        f"Fetching from remote: {remote.name}",
                        QMessageBox.Ok
                    )
                    remote.fetch()
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        "Fetch Error",
                        f"Error fetching from {remote.name}: {str(e)}",
                        QMessageBox.Ok
                    )

            # Reload branches after fetch
            self.load_branches()

            QMessageBox.information(
                self,
                "Fetch Complete",
                "Fetch operation completed.",
                QMessageBox.Ok
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to fetch from remote: {str(e)}",
                QMessageBox.Ok
            )

    def load_branches(self):
        """Load branches from the repository"""
        try:
            self.branch_list.clear()
            branches = self.git_manager.get_all_branches()

            # Get current branch for highlighting
            current_branch = self.git_manager.get_current_branch()

            # Add local branches
            if branches['local']:
                self.branch_list.addItem("--- Local Branches ---")
                for branch in branches['local']:
                    item = QListWidgetItem(branch)
                    # Highlight current branch
                    if branch == current_branch:
                        item.setBackground(QColor(200, 255, 200))  # Light green
                        item.setText(f"{branch} (current)")
                    self.branch_list.addItem(item)

            # Add remote branches
            if branches['remote']:
                self.branch_list.addItem("--- Remote Branches ---")
                for branch in branches['remote']:
                    if branch not in branches['local']:  # Don't show duplicates
                        item = QListWidgetItem(f"{branch} (remote)")
                        item.setData(Qt.UserRole, branch)
                        self.branch_list.addItem(item)
            else:
                # Debug information if no remote branches found
                self.branch_list.addItem("No remote branches found")

        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to load branches: {str(e)}",
                QMessageBox.Ok
            )

    def create_branch(self):
        """Create a new branch"""
        name, ok = QInputDialog.getText(
            self,
            "Create Branch",
            "Enter new branch name:"
        )

        if ok and name:
            try:
                result = self.git_manager.create_branch(name)
                QMessageBox.information(
                    self,
                    "Branch Created",
                    result,
                    QMessageBox.Ok
                )
                self.load_branches()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to create branch: {str(e)}",
                    QMessageBox.Ok
                )

    def checkout_selected_branch(self):
        """Checkout the selected branch"""
        current_item = self.branch_list.currentItem()
        if not current_item or current_item.text().startswith("---"):
            return

        # Get branch name (handle remote branches format)
        branch_name = current_item.data(Qt.UserRole) if current_item.data(Qt.UserRole) else current_item.text()
        branch_name = branch_name.split(" (")[0]  # Remove (current) or (remote) suffix

        try:
            result = self.git_manager.checkout_branch(branch_name, create=False)

            QMessageBox.information(
                self,
                "Checkout Result",
                result,
                QMessageBox.Ok
            )

            # Update UI
            self.load_branches()
            self.current_branch_label.setText(f"Current branch: <b>{self.git_manager.get_current_branch()}</b>")

            # Store selected branch
            self.selected_branch = branch_name
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to checkout branch: {str(e)}",
                QMessageBox.Ok
            )

    def get_selected_branch(self):
        """Return the selected branch name"""
        return self.selected_branch
