# core/__init__.py
# Package initialization file
from .git_manager import GitManager
from .file_sync import FileSync
from .conflict_handler import ConflictHandler
from .gitignore_manager import GitIgnoreManager

__all__ = ['GitManager', 'FileSync', 'ConflictHandler', 'GitIgnoreManager']
