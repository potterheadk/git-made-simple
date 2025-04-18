# gui/gitignore_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QTextEdit, QDialogButtonBox, QCheckBox,
                              QListWidget, QSplitter, QWidget, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class GitIgnoreDialog(QDialog):
    def __init__(self, gitignore_manager, repo_path, parent=None):
        super().__init__(parent)
        self.gitignore_manager = gitignore_manager
        self.repo_path = repo_path

        self.setWindowTitle("Edit .gitignore")
        self.setMinimumSize(700, 500)

        self.setup_ui()
        self.load_gitignore()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header with explanation
        header_label = QLabel("Edit the .gitignore file to specify which files and folders should be ignored by Git.")
        header_label.setWordWrap(True)
        layout.addWidget(header_label)

        # Splitter for presets and editor
        splitter = QSplitter(Qt.Horizontal)

        # Left side: Common presets
        presets_widget = QWidget()
        presets_layout = QVBoxLayout(presets_widget)

        presets_label = QLabel("Common ignore patterns:")
        presets_layout.addWidget(presets_label)

        self.presets_list = QListWidget()
        # Add common presets
        common_presets = [
            "Python",
            "Node.js",
            "Java",
            "C++",
            "Environments",
            "IDE Files",
            "Logs",
            "OS Files",
            "Build Output"
        ]
        self.presets_list.addItems(common_presets)
        self.presets_list.currentItemChanged.connect(self.on_preset_selected)
        presets_layout.addWidget(self.presets_list)

        # Add preset button
        add_preset_button = QPushButton("Add Selected Preset")
        add_preset_button.clicked.connect(self.add_selected_preset)
        presets_layout.addWidget(add_preset_button)

        # Right side: Editor
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)

        editor_label = QLabel(".gitignore content:")
        editor_layout.addWidget(editor_label)

        self.editor = QTextEdit()
        self.editor.setFont(QFont("Courier New", 10))  # Monospace font
        editor_layout.addWidget(self.editor)

        # Add widgets to splitter
        splitter.addWidget(presets_widget)
        splitter.addWidget(editor_widget)
        splitter.setSizes([200, 500])  # Initial sizes

        layout.addWidget(splitter, 1)  # 1 = stretch factor

        # Buttons at bottom
        buttons_layout = QHBoxLayout()

        self.apply_default_button = QPushButton("Apply Default .gitignore")
        self.apply_default_button.clicked.connect(self.apply_default)

        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_gitignore)
        button_box.rejected.connect(self.reject)

        buttons_layout.addWidget(self.apply_default_button)
        buttons_layout.addWidget(button_box)

        layout.addLayout(buttons_layout)

    def load_gitignore(self):
        """Load existing .gitignore content"""
        content = self.gitignore_manager.read_gitignore(self.repo_path)
        self.editor.setText(content)

    def save_gitignore(self):
        """Save .gitignore content"""
        content = self.editor.toPlainText()

        if self.gitignore_manager.save_gitignore(self.repo_path, content):
            QMessageBox.information(
                self,
                "Success",
                ".gitignore file saved successfully.",
                QMessageBox.Ok
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Error",
                "Failed to save .gitignore file.",
                QMessageBox.Ok
            )

    def apply_default(self):
        """Apply default .gitignore content"""
        reply = QMessageBox.question(
            self,
            "Apply Default",
            "This will replace the current content with default .gitignore patterns. Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            default_content = self.gitignore_manager.get_default_gitignore()
            self.editor.setText(default_content)

    def add_selected_preset(self):
        """Add selected preset patterns to the editor"""
        current_item = self.presets_list.currentItem()
        if not current_item:
            return

        preset_name = current_item.text()
        patterns = self.get_preset_patterns(preset_name)

        if not patterns:
            return

        # Get current content and add patterns
        current_content = self.editor.toPlainText()

        # Add a header for the section
        new_content = f"{current_content}\n\n# {preset_name} specific\n"
        new_content += "\n".join(patterns)

        self.editor.setText(new_content)

    def on_preset_selected(self, current, previous):
        """Show a preview of the selected preset"""
        if not current:
            return

        preset_name = current.text()
        patterns = self.get_preset_patterns(preset_name)

        if patterns:
            # Show a preview in status bar or tooltip
            preview = ", ".join(patterns[:3])
            if len(patterns) > 3:
                preview += "..."
            self.setStatusTip(f"{preset_name} patterns: {preview}")

    def get_preset_patterns(self, preset_name):
        """Get patterns for a specific preset"""
        patterns = []

        if preset_name == "Python":
            patterns = [
                "__pycache__/",
                "*.py[cod]",
                "*$py.class",
                "*.so",
                ".Python",
                "build/",
                "develop-eggs/",
                "dist/",
                "*.egg-info/",
                ".installed.cfg",
                "*.egg"
            ]
        elif preset_name == "Node.js":
            patterns = [
                "node_modules/",
                "npm-debug.log",
                "yarn-debug.log",
                "yarn-error.log",
                ".pnp/",
                ".pnp.js",
                "package-lock.json"
            ]
        elif preset_name == "Java":
            patterns = [
                "*.class",
                "*.jar",
                "*.war",
                "*.ear",
                "*.log",
                "target/",
                ".classpath",
                ".project"
            ]
        elif preset_name == "C++":
            patterns = [
                "*.o",
                "*.obj",
                "*.exe",
                "*.dll",
                "*.so",
                "*.dylib",
                "*.lib",
                "*.a",
                "*.out",
                "CMakeFiles/",
                "CMakeCache.txt"
            ]
        elif preset_name == "Environments":
            patterns = [
                ".env",
                ".venv",
                "env/",
                "venv/",
                "ENV/",
                ".env.*",
                "*.env",
                "env.local",
                "env.development",
                "env.test",
                "env.production",
                ".secrets",
                "secrets.*"
            ]
        elif preset_name == "IDE Files":
            patterns = [
                ".idea/",
                ".vscode/",
                "*.swp",
                "*.swo",
                "*.sublime-project",
                "*.sublime-workspace",
                ".project",
                ".settings/",
                "*.tmproj",
                "*.njsproj"
            ]
        elif preset_name == "Logs":
            patterns = [
                "*.log",
                "logs/",
                "log/",
                "npm-debug.log*",
                "yarn-debug.log*",
                "yarn-error.log*"
            ]
        elif preset_name == "OS Files":
            patterns = [
                ".DS_Store",
                ".DS_Store?",
                "._*",
                ".Spotlight-V100",
                ".Trashes",
                "Thumbs.db",
                "ehthumbs.db",
                "Desktop.ini"
            ]
        elif preset_name == "Build Output":
            patterns = [
                "build/",
                "dist/",
                "out/",
                "target/",
                "bin/",
                "obj/",
                "*.min.js",
                "*.min.css"
            ]

        return patterns
