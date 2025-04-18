# gui/main_window.py
from PySide6.QtWidgets import (QMainWindow, QWidget, QPushButton, QVBoxLayout,
                              QHBoxLayout, QLabel, QLineEdit, QFileDialog,
                              QTextEdit, QGroupBox, QFormLayout, QComboBox,
                              QMessageBox, QStatusBar)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont, QIcon
import os

# Module imports
from core.git_manager import GitManager
from core.file_sync import FileSync
from gui.change_dialog import ChangeDetailsDialog
from gui.history_dialog import ChangeHistoryDialog
from gui.conflict_dialog import ConflictResolutionDialog
from gui.gitignore_dialog import GitIgnoreDialog
from gui.branch_dialog import BranchDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize window properties
        self.setWindowTitle("Git Backup Tool")
        self.setMinimumSize(800, 500)

        # Initialize core components
        self.git_manager = GitManager()
        self.file_sync = FileSync(self.git_manager)

        # Setup UI components
        self.setup_ui()

        # Initialize status bar
        self.statusBar().showMessage("Ready")

    def setup_ui(self):
        # Main central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Repository configuration group
        repo_group = QGroupBox("Repository Configuration")
        repo_layout = QFormLayout()

        # Repository path input with browse button
        repo_path_layout = QHBoxLayout()
        self.repo_path = QLineEdit()
        self.repo_path.setPlaceholderText("Select repository directory...")

        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_repository)
        repo_path_layout.addWidget(self.repo_path)
        repo_path_layout.addWidget(browse_button)

        # Remote URL input
        self.remote_url = QLineEdit()
        self.remote_url.setPlaceholderText("e.g., https://github.com/username/repo.git")

        # Authentication type dropdown
        self.auth_type = QComboBox()
        self.auth_type.addItems(["HTTPS", "SSH"])

        # Add all to the form layout
        repo_layout.addRow("Repository Path:", repo_path_layout)
        repo_layout.addRow("Remote URL:", self.remote_url)
        repo_layout.addRow("Authentication:", self.auth_type)

        repo_group.setLayout(repo_layout)
        main_layout.addWidget(repo_group)

        # Action buttons group
        actions_group = QGroupBox("Git Operations")
        actions_layout = QHBoxLayout()

        # Create action buttons
        self.init_button = QPushButton("Initialize")
        self.init_button.setToolTip("Initialize repository or set remote URL")

        self.push_button = QPushButton("Push")
        self.push_button.setToolTip("Push local changes to remote")

        self.pull_button = QPushButton("Pull")
        self.pull_button.setToolTip("Pull changes from remote")

        self.sync_button = QPushButton("Sync All")
        self.sync_button.setToolTip("Sync files and push to remote")

        # Connect buttons to slots
        self.init_button.clicked.connect(self.initialize_repository)
        self.push_button.clicked.connect(self.push_changes)
        self.pull_button.clicked.connect(self.pull_changes)
        self.sync_button.clicked.connect(self.sync_all)

        #"View Changes" button
        self.view_changes_button = QPushButton("View Changes")
        self.view_changes_button.setToolTip("View detailed file changes")
        self.view_changes_button.clicked.connect(self.view_changes)

        #force rescan button
        self.rescan_button = QPushButton("Force Rescan")
        self.rescan_button.setToolTip("Rescan repository for changes without committing")
        self.rescan_button.clicked.connect(self.force_rescan)

        #history button
        self.history_button = QPushButton("Change History")
        self.history_button.setToolTip("View change history")
        self.history_button.clicked.connect(self.view_history)

        # Force push button
        self.force_push_button = QPushButton("Force Push")
        self.force_push_button.setToolTip("Force push local changes to remote (use with caution)")
        self.force_push_button.clicked.connect(self.force_push)

        # Hard reset button
        self.reset_button = QPushButton("Reset")
        self.reset_button.setToolTip("Reset local repository to match remote (discards local changes)")
        self.reset_button.clicked.connect(self.reset_repo)

        # branch selection dropdown and button
        branch_layout = QHBoxLayout()
        branch_layout.addWidget(QLabel("Current Branch:"))
        self.branch_label = QLabel("Not selected")
        branch_layout.addWidget(self.branch_label)
        self.branch_button = QPushButton("Change Branch")
        self.branch_button.clicked.connect(self.change_branch)
        branch_layout.addWidget(self.branch_button)
        repo_layout.addRow("", branch_layout)


        # Add gitignore button to the actions section:
        self.gitignore_button = QPushButton("Edit .gitignore")
        self.gitignore_button.setToolTip("Edit repository .gitignore settings")
        self.gitignore_button.clicked.connect(self.edit_gitignore)

        # Add buttons to layout
        actions_layout.addWidget(self.gitignore_button)
        actions_layout.addWidget(self.force_push_button)
        actions_layout.addWidget(self.reset_button)
        actions_layout.addWidget(self.history_button)
        actions_layout.addWidget(self.rescan_button)
        actions_layout.addWidget(self.view_changes_button)
        actions_layout.addWidget(self.init_button)
        actions_layout.addWidget(self.push_button)
        actions_layout.addWidget(self.pull_button)
        actions_layout.addWidget(self.sync_button)

        actions_group.setLayout(actions_layout)
        main_layout.addWidget(actions_group)

        # Status and output area
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout()

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        output_layout.addWidget(self.output_text)

        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group, 1)  # Give this more stretch

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

    def push_changes(self, remote="origin", branch=None):
        """Push local changes to remote"""
        if self.repo is None:
            raise ValueError("Repository not initialized")

        try:
            # First add all changes
            self.repo.git.add(A=True)

            # Get current branch if not specified - ADD THIS BLOCK HERE
            if branch is None:
                try:
                    branch = self.repo.active_branch.name
                except:
                    branch = "master"  # Default if can't determine

            # Check if there are changes to commit
            if self.repo.is_dirty() or len(self.repo.untracked_files) > 0:
                # Commit changes
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                commit_message = f"Automatic backup commit - {timestamp}"
                self.repo.git.commit(m=commit_message)
                commit_result = f"Committed changes with message: '{commit_message}'"
            else:
                commit_result = "No changes to commit"

            # Push changes - use the branch variable here
            push_info = self.repo.git.push(remote, branch)

            return f"{commit_result}\nPush result: {push_info if push_info else 'Success'}"
        except GitCommandError as e:
            return f"Git error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"

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
        """Add message to output text area"""
        self.output_text.append(message)
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
            result = dialog.exec()

            if result == QDialog.Accepted:
                self.log_output(".gitignore file updated successfully")
                self.statusBar().showMessage(".gitignore updated")
        except Exception as e:
            self.show_error(f"Error editing .gitignore: {str(e)}")

    def change_branch(self):
        """Open branch selection dialog"""
        if not self.check_repo_initialized():
            return

        try:
            dialog = BranchDialog(self.git_manager, self)
            result = dialog.exec()

            if result == QDialog.Accepted and dialog.get_selected_branch():
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
