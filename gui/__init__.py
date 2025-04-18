# gui/__init__.py
# Package initialization file
from .main_window import MainWindow
from .change_dialog import ChangeDetailsDialog
from .history_dialog import ChangeHistoryDialog
from .conflict_dialog import ConflictResolutionDialog
from .gitignore_dialog import GitIgnoreDialog
from .branch_dialog import BranchDialog

__all__ = ['MainWindow', 'ChangeDetailsDialog', 'ChangeHistoryDialog',
           'ConflictResolutionDialog', 'GitIgnoreDialog', 'BranchDialog']
