# gui/main_window.py
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt, Signal, Slot, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtWidgets import (QMainWindow, QWidget, QPushButton, QVBoxLayout,
                              QHBoxLayout, QLabel, QLineEdit, QFileDialog,
                              QTextEdit, QGroupBox, QFormLayout, QComboBox,
                              QMessageBox, QStatusBar, QDialog, QStyle)
import os
from datetime import datetime
# Module imports
from core.git_manager import GitManager
from core.file_sync import FileSync
from gui.change_dialog import ChangeDetailsDialog
from gui.history_dialog import ChangeHistoryDialog
from gui.conflict_dialog import ConflictResolutionDialog
from gui.gitignore_dialog import GitIgnoreDialog
from gui.branch_dialog import BranchDialog
from gui.commit_dialog import CommitDialog
from gui.ssh_key_dialog import SSHKeyDialog

# Create a base dialog class with animations
class AnimatedDialog(QDialog):
    """Base dialog class with smooth animations"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowModality(Qt.ApplicationModal)
        self.animation = None

    def showEvent(self, event):
        """Animate the dialog when it's shown"""
        if not self.animation:
            self.animation = QPropertyAnimation(self, b"geometry")
            self.animation.setDuration(250)
            self.animation.setEasingCurve(QEasingCurve.OutCubic)

            # Save the target geometry
            target_geometry = self.geometry()

            # Start from a smaller size
            start_geometry = QRect(
                target_geometry.center().x() - target_geometry.width() * 0.4,
                target_geometry.center().y() - target_geometry.height() * 0.4,
                target_geometry.width() * 0.8,
                target_geometry.height() * 0.8
            )

            # Set up the animation
            self.animation.setStartValue(start_geometry)
            self.animation.setEndValue(target_geometry)
            self.animation.start()

        super().showEvent(event)

class PrimaryButton(QPushButton):
    """Custom styled primary action button with subtle colors"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(32)
        self.setStyleSheet("""
            QPushButton {
                background-color: #8a9d7e;  /* Muted sage green */
                color: #f5f2ec;  /* Off-white text for contrast */
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #798d6e;  /* Darker on hover */
            }
            QPushButton:pressed {
                background-color: #697c5f;  /* Even darker when pressed */
            }
        """)

class DangerButton(QPushButton):
    """Custom styled button for potentially dangerous operations with subtle colors"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(30)
        self.setStyleSheet("""
            QPushButton {
                background-color: #b08d87;  /* Muted dusty rose */
                color: #f5f2ec;  /* Off-white text */
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #a07d78;  /* Darker on hover */
            }
            QPushButton:pressed {
                background-color: #8f6e69;  /* Even darker when pressed */
            }
        """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize window properties
        self.setWindowTitle("Git Backup Tool")
        self.setMinimumSize(800, 600)

        # Initialize core components
        self.git_manager = GitManager()
        self.file_sync = FileSync(self.git_manager)

        # SSH key path
        self.ssh_key_path = ""

        # Setup UI components FIRST
        self.setup_ui()

        # THEN apply styles (after UI components are created)
        self.apply_styles()

        # Initialize status bar
        self.statusBar().showMessage("Ready")

    def apply_styles(self):
        """Apply CSS styles with subtle, eye-friendly colors"""
        self.setStyleSheet("""
            /* Overall application style */
            QMainWindow, QDialog {
                background-color: #f0ece5;  /* Subtle cream background */
            }

            /* Button styling with warm, muted colors */
            QPushButton {
                background-color: #e0d8cd;  /* Soft taupe */
                color: #4f4a41;  /* Dark taupe text for contrast */
                border: 1px solid #c5bdb3;
                border-radius: 6px;
                padding: 6px 12px;
                min-width: 80px;
                font-weight: 500;
            }

            QPushButton:hover {
                background-color: #d5cec3;  /* Slightly darker on hover */
                border-color: #b8b0a5;
            }

            QPushButton:pressed {
                background-color: #c8c0b4;  /* Even darker when pressed */
                color: #3a3631;
            }

            /* Group box styling */
            QGroupBox {
                font-weight: bold;
                color: #5c554d;  /* Darker text for better contrast */
                border: 1px solid #d0c8bf;
                border-radius: 8px;
                margin-top: 12px;
                background-color: #f6f2ec;  /* Very light cream background */
                padding: 10px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #6b6359;
            }

            /* Input field styling */
            QLineEdit, QTextEdit {
                border: 1px solid #d0c8bf;
                border-radius: 6px;
                padding: 5px;
                background-color: #faf7f1;  /* Very light cream */
                color: #4f4a41;  /* Dark taupe for good readability */
                selection-background-color: #c2b8a8;  /* Subtle highlight */
            }

            QLineEdit:focus, QTextEdit:focus {
                border-color: #b0a799;
            }

            /* Dropdown styling with enhanced readability */
            QComboBox {
                border: 1px solid #d0c8bf;
                border-radius: 6px;
                padding: 5px;
                min-width: 6em;
                background-color: #f4efe7;  /* Light cream */
                color: #4f4a41;  /* Dark taupe text */
            }

            QComboBox:hover {
                background-color: #eae5dc;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #d0c8bf;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }

            /* Status bar */
            QStatusBar {
                background-color: #eae5dc;
                color: #5c554d;
                border-top: 1px solid #d0c8bf;
            }

            /* Text output area */
            QTextEdit#outputText {
                background-color: #f6f2ec;  /* Very light cream */
                border: 1px solid #d0c8bf;
                color: #3a3631;  /* Darker text for better contrast */
                font-family: Consolas, Monaco, monospace;
                line-height: 150%;  /* Improved line spacing */
            }

            /* Labels with better contrast */
            QLabel {
                color: #4f4a41;  /* Dark taupe text */
            }

            /* List widgets - important for branch selection */
            QListWidget {
                background-color: #f6f2ec;  /* Light cream */
                border: 1px solid #d0c8bf;
                border-radius: 6px;
                alternate-background-color: #eae5dc;
                color: #3a3631;  /* Darker text for contrast */
                padding: 2px;
            }

            QListWidget::item {
                padding: 6px;  /* More padding for better readability */
                border-radius: 4px;
                color: #3a3631;  /* Ensure text is visible */
            }

            QListWidget::item:selected {
                background-color: #d5cbbe;  /* Medium taupe */
                color: #2b2822;  /* Near black text for maximum contrast */
            }

            QListWidget::item:hover:!selected {
                background-color: #e8e1d7;  /* Light taupe */
            }

            /* Menu styling */
            QMenu {
                background-color: #f6f2ec;
                color: #4f4a41;
                border: 1px solid #d0c8bf;
                padding: 5px;
            }

            QMenu::item {
                padding: 5px 20px 5px 20px;
                border-radius: 4px;
            }

            QMenu::item:selected {
                background-color: #d5cbbe;
                color: #2b2822;
            }

            /* Tab widget styling */
            QTabWidget::pane {
                border: 1px solid #d0c8bf;
                border-radius: 6px;
                background-color: #f6f2ec;
            }

            QTabBar::tab {
                background-color: #e0d8cd;
                color: #4f4a41;
                border: 1px solid #d0c8bf;
                border-bottom-color: #d0c8bf;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 6px 12px;
            }

            QTabBar::tab:selected {
                background-color: #f6f2ec;
                border-bottom-color: #f6f2ec;
                color: #3a3631;
            }

            QTabBar::tab:!selected {
                margin-top: 2px;
            }

            /* Dialog specific styling */
            QDialog {
                background-color: #f0ece5;
            }

            /* Scrollbar styling for better visibility */
            QScrollBar:vertical {
                border: none;
                background: #eae5dc;
                width: 10px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background: #c5bdb3;
                min-height: 20px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical:hover {
                background: #b8b0a5;
            }
        """)

    def setup_ui(self):
        # Main central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)  # Slightly more space between elements
        main_layout.setContentsMargins(15, 15, 15, 15)  # More padding around edges

        # Repository configuration group
        repo_group = QGroupBox("Repository Configuration")
        repo_layout = QFormLayout()
        repo_layout.setSpacing(10)
        repo_layout.setContentsMargins(10, 15, 10, 10)

        # Repository path input with browse button
        repo_path_layout = QHBoxLayout()
        self.repo_path = QLineEdit()
        self.repo_path.setPlaceholderText("Select repository directory...")
        self.repo_path.setMinimumHeight(28)  # Make it a bit taller

        browse_button = QPushButton("Browse...")
        browse_button.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        repo_path_layout.addWidget(self.repo_path)
        repo_path_layout.addWidget(browse_button)

        # Remote URL input
        remote_layout = QHBoxLayout()
        self.remote_url = QLineEdit()
        self.remote_url.setPlaceholderText("e.g., https://github.com/username/repo.git")
        remote_layout.addWidget(self.remote_url)

        # Authentication type dropdown
        auth_layout = QHBoxLayout()
        self.auth_type = QComboBox()
        self.auth_type.addItems(["HTTPS", "SSH"])
        self.auth_type.currentTextChanged.connect(self.on_auth_type_changed)

        # SSH key button
        self.ssh_key_button = QPushButton("Configure SSH Key")
        self.ssh_key_button.clicked.connect(self.configure_ssh_key)
        self.ssh_key_button.setEnabled(False)  # Disabled initially if HTTPS is selected

        auth_layout.addWidget(self.auth_type)
        auth_layout.addWidget(self.ssh_key_button)
        auth_layout.addStretch()

        # Branch selection
        branch_layout = QHBoxLayout()
        branch_layout.addWidget(QLabel("Current Branch:"))
        self.branch_label = QLabel("Not selected")
        self.branch_label.setStyleSheet("font-weight: bold;")
        branch_layout.addWidget(self.branch_label)
        self.branch_button = QPushButton("Change Branch")
        self.branch_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        branch_layout.addWidget(self.branch_button)
        branch_layout.addStretch()

        # Add all to the form layout
        repo_layout.addRow("Repository:", repo_path_layout)
        repo_layout.addRow("Remote URL:", remote_layout)
        repo_layout.addRow("Authentication:", auth_layout)
        repo_layout.addRow("Branch:", branch_layout)

        repo_group.setLayout(repo_layout)
        main_layout.addWidget(repo_group)

    # Git operations group
        operations_group = QGroupBox("Git Operations")
        operations_layout = QVBoxLayout()
        operations_layout.setSpacing(12)
        operations_layout.setContentsMargins(10, 15, 10, 10)

        # Initialize repo button
        self.init_button = QPushButton("Initialize")
        self.init_button.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.init_button.setToolTip("Initialize repository or set remote URL")
        self.init_button.clicked.connect(self.initialize_repository)

        # Basic Git operations
        self.push_button = QPushButton("Push")
        self.push_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))
        self.push_button.setToolTip("Push local changes to remote")
        self.push_button.clicked.connect(self.push_changes)

        self.commit_button = PrimaryButton("Commit")
        self.commit_button.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
        self.commit_button.setToolTip("Commit changes with custom message")
        self.commit_button.clicked.connect(self.commit_with_message)

        self.pull_button = QPushButton("Pull")
        self.pull_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowDown))
        self.pull_button.setToolTip("Pull changes from remote")
        self.pull_button.clicked.connect(self.pull_changes)

        self.sync_button = PrimaryButton("Sync All")
        self.sync_button.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.sync_button.setToolTip("Sync files and push to remote")
        self.sync_button.clicked.connect(self.sync_all)

        # Advanced Git operations
        self.rescan_button = QPushButton("Force Rescan")
        self.rescan_button.setToolTip("Rescan repository for changes without committing")
        self.rescan_button.clicked.connect(self.force_rescan)

        self.gitignore_button = QPushButton("Edit .gitignore")
        self.gitignore_button.setToolTip("Edit repository .gitignore settings")
        self.gitignore_button.clicked.connect(self.edit_gitignore)

        self.view_changes_button = QPushButton("View Changes")
        self.view_changes_button.setToolTip("View detailed file changes")
        self.view_changes_button.clicked.connect(self.view_changes)

        self.force_push_button = DangerButton("Force Push")
        self.force_push_button.setToolTip("Force push local changes to remote (use with caution)")
        self.force_push_button.clicked.connect(self.force_push)

        self.reset_button = DangerButton("Reset")
        self.reset_button.setToolTip("Reset local repository to match remote (discards local changes)")
        self.reset_button.clicked.connect(self.reset_repo)


        # Create a container for Git Actions
        actions_container = QGroupBox("Actions")
        actions_container.setStyleSheet("""
            QGroupBox {
                border: 1px solid #d0ccc7;
                border-radius: 6px;
                background-color: #f2efeb;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #625f5c;
            }
        """)

        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(8, 12, 8, 8)
        actions_layout.setSpacing(8)

        # Add buttons to this container
        actions_layout.addWidget(self.init_button)
        actions_layout.addWidget(self.commit_button)
        actions_layout.addWidget(self.push_button)
        actions_layout.addWidget(self.pull_button)
        actions_layout.addWidget(self.sync_button)
        actions_layout.addStretch()

        # Create a container for Advanced Operations
        advanced_container = QGroupBox("Advanced Operations")
        advanced_container.setStyleSheet("""
            QGroupBox {
                border: 1px solid #d0ccc7;
                border-radius: 6px;
                background-color: #f2efeb;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #625f5c;
            }
        """)

        advanced_layout = QHBoxLayout(advanced_container)
        advanced_layout.setContentsMargins(8, 12, 8, 8)
        advanced_layout.setSpacing(8)

        # Add advanced buttons
        advanced_layout.addWidget(self.gitignore_button)
        advanced_layout.addWidget(self.view_changes_button)
        advanced_layout.addWidget(self.rescan_button)
        advanced_layout.addWidget(self.force_push_button)
        advanced_layout.addWidget(self.reset_button)
        advanced_layout.addStretch()

        # Add these containers to the operations layout
        operations_layout.addWidget(actions_container)
        operations_layout.addWidget(advanced_container)

        operations_group.setLayout(operations_layout)
        main_layout.addWidget(operations_group)

        # Status and output area
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout()
        output_layout.setSpacing(8)
        output_layout.setContentsMargins(10, 15, 10, 10)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 9))  # Use a monospace font
        self.output_text.setObjectName("outputText")  # Set object name
        self.output_text.setStyleSheet("""
            background-color: #f9f8f6;
            border: 1px solid #e0dcd7;
            border-radius: 6px;
            padding: 5px;
            color: #4a4a4a;
        """)
        output_layout.addWidget(self.output_text)

        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group, 1)  # Give this more stretch

        # Connect remaining signals
        browse_button.clicked.connect(self.browse_repository)
        self.branch_button.clicked.connect(self.change_branch)

        # Set the central widget
        self.setCentralWidget(central_widget)

        # Create status bar
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

    def browse_repository(self):
        """Open file dialog to select repository directory"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Repository Folder",
            os.path.expanduser("~")
        )

        if folder:
            self.repo_path.setText(folder)
            self.statusBar().showMessage(f"Selected repository: {folder}")

    def initialize_repository(self):
        """Initialize repository and set remote"""
        repo_path = self.repo_path.text()
        remote_url = self.remote_url.text()

        if not repo_path:
            self.show_error("Repository path not specified")
            return

        try:
            # Initialize repository
            self.git_manager.init_repo(repo_path)
            self.log_output(f"Repository initialized at: {repo_path}")

            # Set remote if provided
            if remote_url:
                self.git_manager.set_remote(remote_url)
                self.log_output(f"Remote URL set to: {remote_url}")

            self.update_branch_label()

            self.statusBar().showMessage("Repository initialized successfully")
        except Exception as e:
            self.show_error(f"Failed to initialize repository: {str(e)}")

    def push_changes(self):
        """Push local changes to remote repository"""
        if not self.check_repo_initialized():
            return

        # Ask if user wants to use a custom commit message
        reply = QMessageBox.question(
            self,
            "Push Changes",
            "Would you like to use a custom commit message?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        try:
            self.statusBar().showMessage("Pushing changes...")

            if reply == QMessageBox.Yes:
                # Open commit message dialog
                dialog = CommitDialog(self)
                if dialog.exec() == QDialog.Accepted:
                    commit_message = dialog.get_commit_message()
                    if commit_message:
                        result = self.git_manager.push_changes_with_message(commit_message)
                    else:
                        result = self.git_manager.push_changes()
                else:
                    # Dialog cancelled
                    self.statusBar().showMessage("Push cancelled")
                    return
            else:
                # Use default commit message
                result = self.git_manager.push_changes()

            self.log_output(result)
            self.statusBar().showMessage("Push completed")
        except Exception as e:
            self.show_error(f"Push failed: {str(e)}")

    def pull_changes(self):
        """Pull changes from remote repository"""
        if not self.check_repo_initialized():
            return

        try:
            self.statusBar().showMessage("Pulling changes...")
            self.log_output("Pulling changes from remote...")

            # Perform pull operation
            pull_result = self.git_manager.pull_changes()

            # Check if the result is a dictionary (indicating conflict)
            if isinstance(pull_result, dict) and pull_result.get('status') == 'conflict':
                self.log_output(f"Merge conflicts detected: {pull_result['conflicts']} files")
                self.statusBar().showMessage("Merge conflicts detected")

                # Show conflict resolution dialog
                dialog = ConflictResolutionDialog(self.git_manager, self)
                result = dialog.exec()

                if dialog.resolution_complete:
                    self.log_output("Merge conflicts were resolved successfully")
                    self.statusBar().showMessage("Conflicts resolved")
                else:
                    self.log_output("Merge operation incomplete. Conflicts remain unresolved.")
                    self.statusBar().showMessage("Conflicts remain unresolved")
            else:
                # Normal pull result (string)
                self.log_output(pull_result)
                self.statusBar().showMessage("Pull completed")

        except Exception as e:
            self.show_error(f"Pull failed: {str(e)}")

    def sync_all(self):
        """Sync files and push changes"""
        if not self.check_repo_initialized():
            return

        try:
            # Start sync operation
            self.statusBar().showMessage("Syncing files...")
            self.log_output("Starting file synchronization...")

            # Get repo path
            repo_path = self.repo_path.text()

            # Debug output
            self.log_output(f"Repository path: {repo_path}")

            # Perform sync
            sync_result = self.file_sync.sync_files(repo_path)

            # Log detailed changes
            self.log_output(f"Sync completed. Changes detected:")
            self.log_output(f"  - Added: {sync_result['changes']['added']} files")
            self.log_output(f"  - Modified: {sync_result['changes']['modified']} files")
            self.log_output(f"  - Deleted: {sync_result['changes']['deleted']} files")

            # Debug: Log actual files
            if sync_result['details']['added']:
                self.log_output("Added files:")
                for file in sync_result['details']['added'][:5]:  # Show first 5 files
                    self.log_output(f"  - {file}")
                if len(sync_result['details']['added']) > 5:
                    self.log_output(f"  ... and {len(sync_result['details']['added']) - 5} more")

            if sync_result['details']['modified']:
                self.log_output("Modified files:")
                for file in sync_result['details']['modified'][:5]:  # Show first 5 files
                    self.log_output(f"  - {file}")
                if len(sync_result['details']['modified']) > 5:
                    self.log_output(f"  ... and {len(sync_result['details']['modified']) - 5} more")

            if sync_result['details']['deleted']:
                self.log_output("Deleted files:")
                for file in sync_result['details']['deleted'][:5]:  # Show first 5 files
                    self.log_output(f"  - {file}")
                if len(sync_result['details']['deleted']) > 5:
                    self.log_output(f"  ... and {len(sync_result['details']['deleted']) - 5} more")

            # If there are changes, attempt to push them
            if sync_result['changes']['total_changes'] > 0:
                self.log_output("Changes committed to local repository.")

                # Ask user if they want to push changes
                if self.remote_url.text():
                    reply = QMessageBox.question(
                        self,
                        "Push Changes",
                        "Do you want to push these changes to the remote repository?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes
                    )

                    if reply == QMessageBox.Yes:
                        push_result = self.git_manager.push_changes()
                        self.log_output(push_result)
            else:
                self.log_output("No changes detected.")

            self.statusBar().showMessage("Sync completed")
        except Exception as e:
            self.show_error(f"Sync failed: {str(e)}")


    def check_repo_initialized(self):
        """Check if repository is initialized"""
        if self.git_manager.repo is None:
            self.show_error("Repository not initialized. Use 'Initialize' first.")
            return False
        return True

    def log_output(self, message):
        """Add message to output text area with color formatting and icons"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Format based on message content
        if "ERROR" in message.upper() or "FAILED" in message.upper():
            icon = "❌"  # Error icon
            formatted_message = f"<span style='color:#a94442; font-weight:bold;'>[{timestamp}] {icon} {message}</span>"
        elif "SUCCESS" in message.upper() or "COMPLETED" in message.upper():
            icon = "✅"  # Success icon
            formatted_message = f"<span style='color:#3c763d; font-weight:bold;'>[{timestamp}] {icon} {message}</span>"
        elif "WARNING" in message.upper():
            icon = "⚠️"  # Warning icon
            formatted_message = f"<span style='color:#8a6d3b;'>[{timestamp}] {icon} {message}</span>"
        elif "SYNC" in message.upper() or "PUSH" in message.upper() or "PULL" in message.upper():
            icon = "🔄"  # Sync icon
            formatted_message = f"<span style='color:#31708f; font-weight:bold;'>[{timestamp}] {icon} {message}</span>"
        elif "COMMIT" in message.upper():
            icon = "💾"  # Save icon
            formatted_message = f"<span style='color:#31708f; font-weight:bold;'>[{timestamp}] {icon} {message}</span>"
        else:
            icon = "ℹ️"  # Info icon
            formatted_message = f"<span style='color:#4a4a4a;'>[{timestamp}] {icon} {message}</span>"

        # Add message to output
        self.output_text.append(formatted_message)
        # Ensure the newest text is visible
        self.output_text.ensureCursorVisible()

    def show_error(self, message):
        """Show error message dialog"""
        QMessageBox.critical(self, "Error", message)
        self.log_output(f"ERROR: {message}")

    def view_changes(self):
        """Show dialog with detailed file changes"""
        repo_path = self.repo_path.text()

        if not repo_path:
            self.show_error("Repository path not specified")
            return

        # First try to use current changes
        if hasattr(self.file_sync, 'changes') and (
            self.file_sync.changes['added'] or
            self.file_sync.changes['modified'] or
            self.file_sync.changes['deleted']):
            # Use current changes
            self.log_output("Using current detected changes")
            changes = self.file_sync.changes
        else:
            # Try to load from history
            self.log_output("Attempting to load changes from history")
            if self.file_sync.load_change_history(repo_path):
                changes = self.file_sync.changes
            else:
                # Force a rescan if no history available
                self.log_output("No change history available, forcing rescan")
                try:
                    self.file_sync.detect_changes(repo_path)
                    changes = self.file_sync.changes
                except Exception as e:
                    self.show_error(f"Failed to detect changes: {str(e)}")
                    return

        # Debug: log current changes before showing dialog
        self.log_output("Changes to display:")
        self.log_output(f" - Added: {len(changes['added'])} files")
        self.log_output(f" - Modified: {len(changes['modified'])} files")
        self.log_output(f" - Deleted: {len(changes['deleted'])} files")

        # If no changes at all, show a message
        if (len(changes['added']) == 0 and
            len(changes['modified']) == 0 and
            len(changes['deleted']) == 0):
            self.show_error("No changes detected. Run a sync operation first.")
            return

        # Create and show dialog
        dialog = ChangeDetailsDialog(changes, self)
        dialog.exec()

    def force_rescan(self):
        """Force rescan of repository without committing changes"""
        if not self.check_repo_initialized():
            return

        try:
            repo_path = self.repo_path.text()
            self.log_output(f"Rescanning repository: {repo_path}")

            # Just detect changes without committing
            changes = self.file_sync.detect_changes(repo_path)

            self.log_output(f"Rescan completed. Changes detected:")
            self.log_output(f"  - Added: {changes['added']} files")
            self.log_output(f"  - Modified: {changes['modified']} files")
            self.log_output(f"  - Deleted: {changes['deleted']} files")

            self.statusBar().showMessage("Rescan completed")
        except Exception as e:
            self.show_error(f"Rescan failed: {str(e)}")

    def view_history(self):
        """View change history"""
        repo_path = self.repo_path.text()

        if not repo_path:
            self.show_error("Repository path not specified")
            return

        if not os.path.exists(os.path.join(repo_path, '.git')):
            self.show_error("Not a valid Git repository")
            return

        dialog = ChangeHistoryDialog(repo_path, self)
        dialog.exec()

    def force_push(self):
        """Force push changes to remote repository"""
        if not self.check_repo_initialized():
            return

        # Show warning dialog
        reply = QMessageBox.warning(
            self,
            "Force Push Warning",
            "Force push will overwrite remote changes with your local changes. "
            "This can cause data loss. Are you sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            self.statusBar().showMessage("Force pushing changes...")
            self.log_output("Force pushing changes to remote...")

            # Perform force push
            result = self.git_manager.force_push()
            self.log_output(result)

            self.statusBar().showMessage("Force push completed")
        except Exception as e:
            self.show_error(f"Force push failed: {str(e)}")

    def hard_reset(self, commit="HEAD"):
        """Reset to a specific commit, discarding all changes"""
        if self.repo is None:
            raise ValueError("Repository not initialized")

        try:
            # Perform hard reset
            self.repo.git.reset('--hard', commit)
            return f"Reset to {commit} successful"
        except git.GitCommandError as e:
            return f"Git error during reset: {str(e)}"
        except Exception as e:
            return f"Error during reset: {str(e)}"

    def reset_repo(self):
        """Reset local repository to match remote"""
        if not self.check_repo_initialized():
            return

        # Show warning dialog
        reply = QMessageBox.warning(
            self,
            "Reset Warning",
            "This will discard all local changes and reset to the last commit. "
            "Any uncommitted changes will be lost. Are you sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            self.statusBar().showMessage("Resetting repository...")
            self.log_output("Resetting repository to HEAD...")

            # Perform reset
            result = self.git_manager.hard_reset()
            self.log_output(result)

            self.statusBar().showMessage("Reset completed")
        except Exception as e:
            self.show_error(f"Reset failed: {str(e)}")

    def edit_gitignore(self):
        """Open gitignore editor dialog"""
        if not self.check_repo_initialized():
            return

        try:
            repo_path = self.repo_path.text()
            dialog = GitIgnoreDialog(self.git_manager.gitignore_manager, repo_path, self)

            # Either use the imported QDialog:
            if dialog.exec() == QDialog.Accepted:
                self.log_output(".gitignore file updated successfully")
                self.statusBar().showMessage(".gitignore updated")

            # Or use the result method:
            # dialog.exec()
            # if dialog.result():
            #     self.log_output(".gitignore file updated successfully")
            #     self.statusBar().showMessage(".gitignore updated")
        except Exception as e:
            self.show_error(f"Error editing .gitignore: {str(e)}")

    def change_branch(self):
        """Open branch selection dialog"""
        if not self.check_repo_initialized():
            return

        try:
            dialog = BranchDialog(self.git_manager, self)
            dialog.exec()

            # Use dialog result method instead
            if dialog.result() and dialog.get_selected_branch():
                branch = dialog.get_selected_branch()
                self.log_output(f"Switched to branch: {branch}")
                self.statusBar().showMessage(f"Branch: {branch}")
                self.update_branch_label()
        except Exception as e:
            self.show_error(f"Error changing branch: {str(e)}")

    def update_branch_label(self):
        """Update the branch label with current branch"""
        if not self.git_manager or not self.git_manager.repo:
            self.branch_label.setText("Not selected")
            return

        try:
            branch = self.git_manager.get_current_branch()
            self.branch_label.setText(branch)
        except:
            self.branch_label.setText("Unknown")

    def on_auth_type_changed(self, auth_type):
        """Handle authentication type change"""
        self.ssh_key_button.setEnabled(auth_type == "SSH")

        if auth_type == "SSH":
            self.log_output("SSH authentication selected. Configure your SSH key.")
        else:
            self.log_output("HTTPS authentication selected.")

    def configure_ssh_key(self):
        """Open SSH key configuration dialog"""
        dialog = SSHKeyDialog(self)
        if dialog.exec() == QDialog.Accepted:
            ssh_key_path = dialog.get_ssh_key_path()
            if ssh_key_path:
                try:
                    result = self.git_manager.set_ssh_key(ssh_key_path)
                    self.ssh_key_path = ssh_key_path
                    self.log_output(result)
                    self.statusBar().showMessage("SSH key configured")
                except Exception as e:
                    self.show_error(f"Error configuring SSH key: {str(e)}")

    def commit_with_message(self):
        """Commit changes with custom message"""
        if not self.check_repo_initialized():
            return

        dialog = CommitDialog(self)
        if dialog.exec() == QDialog.Accepted:
            commit_message = dialog.get_commit_message()
            if commit_message:
                try:
                    self.statusBar().showMessage("Committing changes...")

                    # Add all changes and commit
                    self.git_manager.repo.git.add(A=True)

                    # Check if there are changes to commit
                    if self.git_manager.repo.is_dirty() or len(self.git_manager.repo.untracked_files) > 0:
                        self.git_manager.repo.git.commit(m=commit_message)
                        self.log_output(f"Committed changes with message: '{commit_message}'")
                        self.statusBar().showMessage("Changes committed successfully")
                    else:
                        self.log_output("No changes to commit")
                        self.statusBar().showMessage("No changes to commit")
                except Exception as e:
                    self.show_error(f"Commit failed: {str(e)}")
