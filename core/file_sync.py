# core/file_sync.py
import os
import shutil
import time
import hashlib
from datetime import datetime
import logging
import json

class FileSync:
    def __init__(self, git_manager=None):
        self.git_manager = git_manager
        self.last_sync_data = {}
        self.changes = {
            'added': [],
            'modified': [],
            'deleted': []
        }
        # Add debug flag
        self.debug = True

    def set_git_manager(self, git_manager):
        """Set the Git manager instance"""
        self.git_manager = git_manager

    def debug_log(self, message):
        """Print debug messages if debug is enabled"""
        if self.debug:
            print(f"[DEBUG] {message}")

    def load_last_sync_data(self, repo_path):
        """Load data from the last synchronization"""
        sync_data_path = os.path.join(repo_path, '.git', 'last_sync.json')

        if os.path.exists(sync_data_path):
            try:
                with open(sync_data_path, 'r') as f:
                    self.last_sync_data = json.load(f)
                self.debug_log(f"Loaded sync data with {len(self.last_sync_data)} files")
                return True
            except Exception as e:
                logging.error(f"Error loading sync data: {str(e)}")
                self.debug_log(f"Error loading sync data: {str(e)}")
                self.last_sync_data = {}
        else:
            self.debug_log(f"No previous sync data found at {sync_data_path}")
            self.last_sync_data = {}
        return False

    def save_sync_data(self, repo_path):
        """Save synchronization data for future comparison"""
        sync_data_path = os.path.join(repo_path, '.git', 'last_sync.json')

        try:
            # Create the data structure with file info
            current_files = {}

            for root, dirs, files in os.walk(repo_path):
                # Skip .git directory
                if '.git' in root.split(os.sep):
                    continue

                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, repo_path)

                    # Get file stats
                    stats = os.stat(file_path)

                    # Calculate file hash for future comparisons
                    file_hash = self._calculate_file_hash(file_path)

                    current_files[rel_path] = {
                        'size': stats.st_size,
                        'mtime': stats.st_mtime,
                        'hash': file_hash
                    }

            # Save to JSON file
            with open(sync_data_path, 'w') as f:
                json.dump(current_files, f, indent=2)

            self.debug_log(f"Saved sync data with {len(current_files)} files")
            return True
        except Exception as e:
            logging.error(f"Error saving sync data: {str(e)}")
            self.debug_log(f"Error saving sync data: {str(e)}")
            return False

    def _calculate_file_hash(self, file_path, block_size=65536):
        """Calculate SHA-256 hash of a file"""
        try:
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for block in iter(lambda: f.read(block_size), b''):
                    sha256.update(block)
            return sha256.hexdigest()
        except Exception as e:
            logging.error(f"Error calculating hash for {file_path}: {str(e)}")
            self.debug_log(f"Error calculating hash for {file_path}: {str(e)}")
            return None

    def detect_changes(self, repo_path):
        """Detect added, modified, and deleted files"""
        if not os.path.exists(repo_path):
            raise ValueError(f"Repository path does not exist: {repo_path}")

        # Reset changes
        self.changes = {
            'added': [],
            'modified': [],
            'deleted': []
        }

        # Load previous sync data
        self.load_last_sync_data(repo_path)

        # Get current files
        current_files = {}

        self.debug_log(f"Starting change detection in {repo_path}")

        for root, dirs, files in os.walk(repo_path):
            # Skip .git directory
            if '.git' in root.split(os.sep):
                continue

            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)

                # Get file stats
                stats = os.stat(file_path)
                file_hash = self._calculate_file_hash(file_path)

                current_files[rel_path] = {
                    'size': stats.st_size,
                    'mtime': stats.st_mtime,
                    'hash': file_hash,
                    'path': file_path
                }

                # Check if file is new or modified
                if rel_path not in self.last_sync_data:
                    self.changes['added'].append(rel_path)
                    self.debug_log(f"Added file detected: {rel_path}")
                elif file_hash != self.last_sync_data[rel_path]['hash']:
                    self.changes['modified'].append(rel_path)
                    self.debug_log(f"Modified file detected: {rel_path}")

        # Check for deleted files
        for rel_path in self.last_sync_data:
            if rel_path not in current_files:
                self.changes['deleted'].append(rel_path)
                self.debug_log(f"Deleted file detected: {rel_path}")

        # Return summary
        changes_summary = {
            'added': len(self.changes['added']),
            'modified': len(self.changes['modified']),
            'deleted': len(self.changes['deleted']),
            'total_changes': len(self.changes['added']) + len(self.changes['modified']) + len(self.changes['deleted'])
        }

        self.debug_log(f"Change detection summary: {changes_summary}")
        return changes_summary

    def sync_files(self, source_dir, target_dir=None):
        """Synchronize files between directories

        If target_dir is None, we're just detecting changes in source_dir for Git
        """
        if not os.path.exists(source_dir):
            raise ValueError(f"Source directory does not exist: {source_dir}")

        self.debug_log(f"Starting sync operation from {source_dir}")

        # If target_dir is specified, we're syncing between directories
        if target_dir:
            # Implementation for directory-to-directory sync
            # (Keeping the existing implementation)
            pass

        # Detect changes for Git repo
        change_summary = self.detect_changes(source_dir)

        # Ensure Git manager is available
        if not self.git_manager or not self.git_manager.repo:
            self.debug_log("Git manager not available, skipping commit operation")
            # Save sync data even if we can't commit
            self.save_sync_data(source_dir)
            return {
                'changes': change_summary,
                'details': self.changes
            }

        # If changes detected, commit them
        if change_summary['total_changes'] > 0:
            try:
                # Add all changes to Git
                self.git_manager.repo.git.add(A=True)

                # Create commit message with change details
                commit_msg = f"Sync {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: "
                commit_msg += f"{change_summary['added']} added, "
                commit_msg += f"{change_summary['modified']} modified, "
                commit_msg += f"{change_summary['deleted']} deleted"

                # Commit changes
                if self.git_manager.repo.is_dirty() or len(self.git_manager.repo.untracked_files) > 0:
                    self.git_manager.repo.git.commit(m=commit_msg)
                    self.debug_log(f"Committed changes with message: {commit_msg}")
            except Exception as e:
                logging.error(f"Error committing changes: {str(e)}")
                self.debug_log(f"Error committing changes: {str(e)}")
        else:
            self.debug_log("No changes to commit")

        # Save sync data for future comparison
        self.save_sync_data(source_dir)

        # Save change history
        self.save_change_history(source_dir)

        return {
            'changes': change_summary,
            'details': self.changes
        }

    def get_detailed_changes(self):
        """Get detailed information about changes"""
        return self.changes

    def verify_with_git_status(self, repo_path):
        """Use git status to verify changes"""
        if not self.git_manager or not self.git_manager.repo:
            self.debug_log("Git manager not available, skipping git status verification")
            return

        try:
            # Get status from git
            repo = self.git_manager.repo

            # Get untracked files (new files)
            untracked = repo.untracked_files
            self.debug_log(f"Git untracked files: {len(untracked)}")

            # Get modified files
            modified = [item.a_path for item in repo.index.diff(None)]
            self.debug_log(f"Git modified files: {len(modified)}")

            # Get deleted files
            deleted = [item.a_path for item in repo.index.diff(None) if item.deleted_file]
            self.debug_log(f"Git deleted files: {len(deleted)}")

            # Print some debug info for comparison
            self.debug_log(f"Our tracked added files: {len(self.changes['added'])}")
            self.debug_log(f"Our tracked modified files: {len(self.changes['modified'])}")
            self.debug_log(f"Our tracked deleted files: {len(self.changes['deleted'])}")

            # Optionally enhance our tracking with git status
            # This is commented out as it might interfere with your current logic
            # self.changes['added'] = untracked
            # self.changes['modified'] = modified
            # self.changes['deleted'] = deleted
        except Exception as e:
            self.debug_log(f"Error verifying with git status: {str(e)}")


    def save_change_history(self, repo_path):
        """Save change history for later viewing"""
        history_path = os.path.join(repo_path, '.git', 'change_history.json')

        try:
            # Load existing history if available
            history = []
            if os.path.exists(history_path):
                try:
                    with open(history_path, 'r') as f:
                        history = json.load(f)
                except:
                    history = []

            # Create new history entry
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_entry = {
                'timestamp': timestamp,
                'changes': self.changes.copy(),
                'summary': {
                    'added': len(self.changes['added']),
                    'modified': len(self.changes['modified']),
                    'deleted': len(self.changes['deleted']),
                    'total': len(self.changes['added']) + len(self.changes['modified']) + len(self.changes['deleted'])
                }
            }

            # Add to history (keep last 10 entries)
            history.insert(0, new_entry)
            history = history[:10]  # Keep only last 10 entries

            # Save updated history
            with open(history_path, 'w') as f:
                json.dump(history, f, indent=2)

            self.debug_log(f"Saved change history to {history_path}")
            return True
        except Exception as e:
            self.debug_log(f"Error saving change history: {str(e)}")
            return False

    def load_change_history(self, repo_path):
        """Load the most recent change history"""
        history_path = os.path.join(repo_path, '.git', 'change_history.json')

        if os.path.exists(history_path):
            try:
                with open(history_path, 'r') as f:
                    history = json.load(f)

                if history:
                    # Get most recent history entry
                    latest = history[0]
                    self.changes = latest['changes']
                    self.debug_log(f"Loaded change history from {timestamp}")
                    return True
            except Exception as e:
                self.debug_log(f"Error loading change history: {str(e)}")

        return False
