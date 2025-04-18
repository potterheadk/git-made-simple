# gui/conflict_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QListWidget, QListWidgetItem, QSplitter,
                              QTextEdit, QDialogButtonBox, QComboBox, QMessageBox,
                              QTabWidget, QWidget, QRadioButton, QButtonGroup,
                              QGroupBox)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont, QColor, QTextCharFormat, QBrush, QSyntaxHighlighter

class ConflictSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for conflict markers"""
    def __init__(self, document):
        super().__init__(document)

        # Define formatting for different parts
        self.conflict_start_format = QTextCharFormat()
        self.conflict_start_format.setBackground(QBrush(QColor("#ffebd6")))
        self.conflict_start_format.setForeground(QBrush(QColor("#b03000")))
        self.conflict_start_format.setFontWeight(QFont.Bold)

        self.conflict_separator_format = QTextCharFormat()
        self.conflict_separator_format.setBackground(QBrush(QColor("#f0f0ff")))
        self.conflict_separator_format.setForeground(QBrush(QColor("#0030b0")))
        self.conflict_separator_format.setFontWeight(QFont.Bold)

        self.conflict_end_format = QTextCharFormat()
        self.conflict_end_format.setBackground(QBrush(QColor("#e6ffe6")))
        self.conflict_end_format.setForeground(QBrush(QColor("#006000")))
        self.conflict_end_format.setFontWeight(QFont.Bold)

        self.our_format = QTextCharFormat()
        self.our_format.setBackground(QBrush(QColor("#ffefef")))

        self.their_format = QTextCharFormat()
        self.their_format.setBackground(QBrush(QColor("#efffef")))

    def highlightBlock(self, text):
        """Highlight conflict markers in text"""
        # Highlight conflict markers
        if "<<<<<<< HEAD" in text:
            self.setFormat(text.find("<<<<<<< HEAD"), len("<<<<<<< HEAD"), self.conflict_start_format)

        if "=======" in text:
            self.setFormat(text.find("======="), len("======="), self.conflict_separator_format)

        if ">>>>>>>" in text:
            # Find the position and length of the end marker
            pos = text.find(">>>>>>>")
            length = len(text) - pos  # Highlight until end of line
            self.setFormat(pos, length, self.conflict_end_format)

        # Attempt to highlight content between markers (simple approach)
        if "<<<<<<< HEAD" in text:
            # This is an "our" section start
            section_start = text.find("<<<<<<< HEAD") + len("<<<<<<< HEAD")
            self.setFormat(section_start, len(text) - section_start, self.our_format)

        if "=======" in text and ">>>>>>>>" not in text:
            # This is a "their" section start
            section_start = text.find("=======") + len("=======")
            self.setFormat(section_start, len(text) - section_start, self.their_format)

class ConflictResolutionDialog(QDialog):
    """Dialog for resolving Git merge conflicts"""

    def __init__(self, git_manager, parent=None):
        super().__init__(parent)
        self.git_manager = git_manager
        self.conflict_handler = git_manager.conflict_handler
        self.conflicts = []
        self.current_conflict = None
        self.resolution_complete = False

        self.setWindowTitle("Resolve Merge Conflicts")
        self.setMinimumSize(900, 700)

        # Detect conflicts
        self.refresh_conflicts()
        self.setup_ui()

    def refresh_conflicts(self):
        """Refresh the list of conflicts"""
        if self.conflict_handler.detect_conflicts():
            self.conflicts = self.conflict_handler.conflict_files
        else:
            self.conflicts = []

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Header label with explanation
        header_label = QLabel("Merge conflicts were detected during the pull operation. "
                              "Please resolve each conflict by choosing an option for each file.")
        header_label.setWordWrap(True)
        main_layout.addWidget(header_label)

        # Conflict count label
        self.conflict_count_label = QLabel(f"Total conflicts: {len(self.conflicts)}")
        main_layout.addWidget(self.conflict_count_label)

        # Main splitter: list of conflicts on left, resolution on right
        splitter = QSplitter(Qt.Horizontal)

        # Left panel: List of conflicted files
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        self.conflict_list = QListWidget()
        # Populate list
        for conflict in self.conflicts:
            item = QListWidgetItem(conflict['path'])
            item.setData(Qt.UserRole, conflict)
            self.conflict_list.addItem(item)

        self.conflict_list.currentItemChanged.connect(self.on_conflict_selected)
        left_layout.addWidget(self.conflict_list)

        # Right panel: Conflict resolution options
        right_panel = QWidget()
        self.right_layout = QVBoxLayout(right_panel)

        # Tab widget for different resolution methods
        self.resolution_tabs = QTabWidget()

        # Tab 1: Quick Resolution
        quick_tab = QWidget()
        quick_layout = QVBoxLayout(quick_tab)

        resolution_group = QGroupBox("Resolution Method")
        resolution_layout = QVBoxLayout(resolution_group)

        self.use_local = QRadioButton("Use my version (local)")
        self.use_remote = QRadioButton("Use their version (remote)")
        self.manual_edit = QRadioButton("Edit manually")

        self.resolution_method = QButtonGroup()
        self.resolution_method.addButton(self.use_local, 1)
        self.resolution_method.addButton(self.use_remote, 2)
        self.resolution_method.addButton(self.manual_edit, 3)

        # Default selection
        self.use_local.setChecked(True)

        resolution_layout.addWidget(self.use_local)
        resolution_layout.addWidget(self.use_remote)
        resolution_layout.addWidget(self.manual_edit)

        quick_layout.addWidget(resolution_group)

        # Apply button
        apply_button = QPushButton("Apply Resolution")
        apply_button.clicked.connect(self.apply_resolution)
        quick_layout.addWidget(apply_button)

        # Status label
        self.status_label = QLabel("")
        quick_layout.addWidget(self.status_label)

        # Add stretchy space
        quick_layout.addStretch()

        self.resolution_tabs.addTab(quick_tab, "Quick Resolution")

        # Tab 2: Manual Edit
        edit_tab = QWidget()
        edit_layout = QVBoxLayout(edit_tab)

        edit_label = QLabel("Edit the file content below to resolve conflicts. "
                            "Remove conflict markers (<<<<<<< HEAD, =======, >>>>>>>) when done.")
        edit_label.setWordWrap(True)
        edit_layout.addWidget(edit_label)

        self.edit_text = QTextEdit()
        self.highlighter = ConflictSyntaxHighlighter(self.edit_text.document())
        edit_layout.addWidget(self.edit_text)

        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(self.save_manual_edit)
        edit_layout.addWidget(save_button)

        self.resolution_tabs.addTab(edit_tab, "Manual Edit")

        # Tab 3: Diff View (simplified)
        diff_tab = QWidget()
        diff_layout = QVBoxLayout(diff_tab)

        diff_label = QLabel("This view shows the differences between your version and the remote version.")
        diff_label.setWordWrap(True)
        diff_layout.addWidget(diff_label)

        self.diff_text = QTextEdit()
        self.diff_text.setReadOnly(True)
        diff_layout.addWidget(self.diff_text)

        self.resolution_tabs.addTab(diff_tab, "Diff View")

        self.right_layout.addWidget(self.resolution_tabs)

        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([200, 700])  # Initial sizes

        main_layout.addWidget(splitter, 1)  # 1 = stretch factor

        # Bottom buttons
        buttons_layout = QHBoxLayout()

        abort_button = QPushButton("Abort Merge")
        abort_button.clicked.connect(self.abort_merge)

        resolve_all_local_button = QPushButton("Resolve All Using Mine")
        resolve_all_local_button.clicked.connect(self.resolve_all_local)

        resolve_all_remote_button = QPushButton("Resolve All Using Theirs")
        resolve_all_remote_button.clicked.connect(self.resolve_all_remote)

        complete_button = QPushButton("Complete Merge")
        complete_button.clicked.connect(self.complete_merge)

        buttons_layout.addWidget(abort_button)
        buttons_layout.addWidget(resolve_all_local_button)
        buttons_layout.addWidget(resolve_all_remote_button)
        buttons_layout.addWidget(complete_button)

        main_layout.addLayout(buttons_layout)

        # If no conflicts, show a message
        if not self.conflicts:
            self.status_label.setText("No conflicts detected.")

    def on_conflict_selected(self, current, previous):
        """Handle selection of a conflict in the list"""
        if not current:
            return

        self.current_conflict = current.data(Qt.UserRole)
        file_path = self.current_conflict['full_path']

        # Load file content for manual edit
        content = self.conflict_handler.get_conflict_content(file_path)
        if content:
            self.edit_text.setText(content)

            # Generate a simplified diff view
            self.generate_diff_view(content)
        else:
            self.edit_text.setText("Error: Could not load file content")
            self.diff_text.setText("Error: Could not load file content")

    def generate_diff_view(self, content):
        """Generate a simplified diff view from the conflict markers"""
        diff_text = "CONFLICT DIFF VIEW:\n\n"

        # Split content by lines
        lines = content.splitlines()

        in_our_section = False
        in_their_section = False
        our_content = []
        their_content = []

        for line in lines:
            if line.startswith("<<<<<<< HEAD"):
                in_our_section = True
                in_their_section = False
                continue
            elif line.startswith("======="):
                in_our_section = False
                in_their_section = True
                continue
            elif line.startswith(">>>>>>>"):
                in_our_section = False
                in_their_section = False
                continue

            if in_our_section:
                our_content.append(line)
            elif in_their_section:
                their_content.append(line)

        # Create diff output
        diff_text += "YOUR VERSION (LOCAL):\n"
        diff_text += "-" * 40 + "\n"
        diff_text += "\n".join(our_content)
        diff_text += "\n\n" + "-" * 40 + "\n\n"

        diff_text += "THEIR VERSION (REMOTE):\n"
        diff_text += "-" * 40 + "\n"
        diff_text += "\n".join(their_content)

        self.diff_text.setText(diff_text)

    def apply_resolution(self):
        """Apply the selected resolution method to the current conflict"""
        if not self.current_conflict:
            self.status_label.setText("Error: No conflict selected")
            return

        try:
            file_path = self.current_conflict['path']

            if self.use_local.isChecked():
                # Use local version
                self.conflict_handler.resolve_use_ours(file_path)
                self.status_label.setText(f"Applied local version to {file_path}")
            elif self.use_remote.isChecked():
                # Use remote version
                self.conflict_handler.resolve_use_theirs(file_path)
                self.status_label.setText(f"Applied remote version to {file_path}")
            elif self.manual_edit.isChecked():
                # Switch to manual edit tab
                self.resolution_tabs.setCurrentIndex(1)
                self.status_label.setText("Please edit the file manually in the Manual Edit tab")
                return

            # Refresh the conflict list
            self.refresh_conflicts()
            current_index = self.conflict_list.currentRow()

            # Update the list
            self.conflict_list.clear()
            for conflict in self.conflicts:
                item = QListWidgetItem(conflict['path'])
                item.setData(Qt.UserRole, conflict)
                self.conflict_list.addItem(item)

            # Update count label
            self.conflict_count_label.setText(f"Total conflicts: {len(self.conflicts)}")

            # Select the next conflict
            if self.conflicts:
                if current_index >= 0 and current_index < len(self.conflicts):
                    self.conflict_list.setCurrentRow(current_index)
                elif current_index >= len(self.conflicts) and len(self.conflicts) > 0:
                    self.conflict_list.setCurrentRow(len(self.conflicts) - 1)

        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    def save_manual_edit(self):
        """Save manually edited content"""
        if not self.current_conflict:
            return

        try:
            content = self.edit_text.toPlainText()
            file_path = self.current_conflict['full_path']

            # Check if conflict markers still exist
            if "<<<<<<< HEAD" in content or "=======" in content or ">>>>>>>" in content:
                reply = QMessageBox.question(
                    self,
                    "Conflict Markers Detected",
                    "The file still contains conflict markers. Save anyway?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if reply == QMessageBox.No:
                    return

            # Save the content
            if self.conflict_handler.save_edited_content(file_path, content):
                self.status_label.setText(f"Successfully saved changes to {self.current_conflict['path']}")

                # Refresh conflicts
                self.refresh_conflicts()
                current_index = self.conflict_list.currentRow()

                # Update the list
                self.conflict_list.clear()
                for conflict in self.conflicts:
                    item = QListWidgetItem(conflict['path'])
                    item.setData(Qt.UserRole, conflict)
                    self.conflict_list.addItem(item)

                # Update count label
                self.conflict_count_label.setText(f"Total conflicts: {len(self.conflicts)}")
            else:
                self.status_label.setText(f"Error saving changes to {self.current_conflict['path']}")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    def abort_merge(self):
        """Abort the merge operation"""
        reply = QMessageBox.question(
            self,
            "Abort Merge",
            "Are you sure you want to abort the merge? All changes will be lost.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                if self.conflict_handler.abort_merge():
                    self.status_label.setText("Merge aborted successfully")
                    self.resolution_complete = True
                    self.accept()
                else:
                    self.status_label.setText("Failed to abort merge")
            except Exception as e:
                self.status_label.setText(f"Error: {str(e)}")

        def resolve_all_local(self):
            """Resolve all conflicts using local versions"""
            reply = QMessageBox.question(
                self,
                "Resolve All Using Mine",
                "Are you sure you want to resolve all conflicts using your (local) versions?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                try:
                    if self.conflict_handler.resolve_use_ours():
                        self.status_label.setText("All conflicts resolved using local versions")
                        # Refresh conflicts
                        self.refresh_conflicts()

                        # Update the list
                        self.conflict_list.clear()
                        for conflict in self.conflicts:
                            item = QListWidgetItem(conflict['path'])
                            item.setData(Qt.UserRole, conflict)
                            self.conflict_list.addItem(item)

                        # Update count label
                        self.conflict_count_label.setText(f"Total conflicts: {len(self.conflicts)}")

                        if len(self.conflicts) == 0:
                            QMessageBox.information(
                                self,
                                "Conflicts Resolved",
                                "All conflicts have been resolved. You can now complete the merge.",
                                QMessageBox.Ok
                            )
                    else:
                        self.status_label.setText("Failed to resolve all conflicts")
                except Exception as e:
                    self.status_label.setText(f"Error: {str(e)}")

        def resolve_all_remote(self):
            """Resolve all conflicts using remote versions"""
            reply = QMessageBox.question(
                self,
                "Resolve All Using Theirs",
                "Are you sure you want to resolve all conflicts using remote versions?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                try:
                    if self.conflict_handler.resolve_use_theirs():
                        self.status_label.setText("All conflicts resolved using remote versions")
                        # Refresh conflicts
                        self.refresh_conflicts()

                        # Update the list
                        self.conflict_list.clear()
                        for conflict in self.conflicts:
                            item = QListWidgetItem(conflict['path'])
                            item.setData(Qt.UserRole, conflict)
                            self.conflict_list.addItem(item)

                        # Update count label
                        self.conflict_count_label.setText(f"Total conflicts: {len(self.conflicts)}")

                        if len(self.conflicts) == 0:
                            QMessageBox.information(
                                self,
                                "Conflicts Resolved",
                                "All conflicts have been resolved. You can now complete the merge.",
                                QMessageBox.Ok
                            )
                    else:
                        self.status_label.setText("Failed to resolve all conflicts")
                except Exception as e:
                    self.status_label.setText(f"Error: {str(e)}")

        def complete_merge(self):
            """Complete the merge operation after resolving conflicts"""
            # Check if there are any remaining conflicts
            if self.conflicts:
                reply = QMessageBox.question(
                    self,
                    "Unresolved Conflicts",
                    f"There are still {len(self.conflicts)} unresolved conflicts. "
                    "Do you want to complete the merge anyway?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if reply == QMessageBox.No:
                    return

            try:
                commit_message = f"Merge conflict resolution - {len(self.conflicts)} remaining"
                if self.conflict_handler.complete_merge(commit_message):
                    self.status_label.setText("Merge completed successfully")
                    self.resolution_complete = True

                    QMessageBox.information(
                        self,
                        "Merge Completed",
                        "The merge has been completed successfully.",
                        QMessageBox.Ok
                    )

                    self.accept()
                else:
                    self.status_label.setText("Failed to complete merge. Check for remaining conflicts.")
            except Exception as e:
                self.status_label.setText(f"Error completing merge: {str(e)}")

        def closeEvent(self, event):
            """Handle dialog close event"""
            if not self.resolution_complete and self.conflicts:
                reply = QMessageBox.question(
                    self,
                    "Unresolved Conflicts",
                    "There are unresolved conflicts. If you close this dialog, "
                    "the merge will remain incomplete. Do you want to close anyway?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    event.accept()
                else:
                    event.ignore()
            else:
                event.accept()
