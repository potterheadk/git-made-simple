# core/conflict_handler.py
import os
import shutil
import tempfile
import logging
from datetime import datetime
import re

class ConflictHandler:
    def __init__(self, git_manager=None):
        self.git_manager = git_manager
        self.backup_dir = None
        self.conflict_files = []
        self.debug = True

    def set_git_manager(self, git_manager):
        """Set the Git manager instance"""
        self.git_manager = git_manager

    def debug_log(self, message):
        """Print debug messages if debug is enabled"""
        if self.debug:
            print(f"[CONFLICT HANDLER] {message}")
            logging.debug(message)

    def detect_conflicts(self):
        """Detect if there are any merge conflicts in the repository"""
        if not self.git_manager or not self.git_manager.repo:
            raise ValueError("Git manager not initialized")

        repo = self.git_manager.repo
        repo_path = repo.working_dir

        self.conflict_files = []

        try:
            # Check for merge state
            if os.path.exists(os.path.join(repo_path, '.git', 'MERGE_HEAD')):
                self.debug_log("Repository is in a merge state")

                # Get conflicted files using git status
                status_output = repo.git.status()

                # Parse status output to find conflicted files
                for line in status_output.splitlines():
                    if "both modified:" in line:
                        file_path = line.split("both modified:")[1].strip()
                        full_path = os.path.join(repo_path, file_path)
                        self.conflict_files.append({
                            'path': file_path,
                            'full_path': full_path,
                            'status': 'both_modified'
                        })
                        self.debug_log(f"Conflict detected: {file_path}")
                    elif "added by us:" in line:
                        file_path = line.split("added by us:")[1].strip()
                        full_path = os.path.join(repo_path, file_path)
                        self.conflict_files.append({
                            'path': file_path,
                            'full_path': full_path,
                            'status': 'added_by_us'
                        })
                        self.debug_log(f"Conflict detected: {file_path} (added by us)")
                    elif "added by them:" in line:
                        file_path = line.split("added by them:")[1].strip()
                        full_path = os.path.join(repo_path, file_path)
                        self.conflict_files.append({
                            'path': file_path,
                            'full_path': full_path,
                            'status': 'added_by_them'
                        })
                        self.debug_log(f"Conflict detected: {file_path} (added by them)")
                    elif "deleted by us:" in line:
                        file_path = line.split("deleted by us:")[1].strip()
                        full_path = os.path.join(repo_path, file_path)
                        self.conflict_files.append({
                            'path': file_path,
                            'full_path': full_path,
                            'status': 'deleted_by_us'
                        })
                        self.debug_log(f"Conflict detected: {file_path} (deleted by us)")
                    elif "deleted by them:" in line:
                        file_path = line.split("deleted by them:")[1].strip()
                        full_path = os.path.join(repo_path, file_path)
                        self.conflict_files.append({
                            'path': file_path,
                            'full_path': full_path,
                            'status': 'deleted_by_them'
                        })
                        self.debug_log(f"Conflict detected: {file_path} (deleted by them)")

            return len(self.conflict_files) > 0

        except Exception as e:
            self.debug_log(f"Error detecting conflicts: {str(e)}")
            raise

    def backup_conflicted_files(self):
        """Backup conflicted files before resolution"""
        if not self.conflict_files:
            return False

        if not self.git_manager or not self.git_manager.repo:
            raise ValueError("Git manager not initialized")

        repo_path = self.git_manager.repo.working_dir
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = os.path.join(repo_path, '.git', 'conflict_backups', timestamp)

        try:
            # Create backup directory
            os.makedirs(self.backup_dir, exist_ok=True)
            self.debug_log(f"Created backup directory: {self.backup_dir}")

            # Copy conflicted files
            for conflict in self.conflict_files:
                if os.path.exists(conflict['full_path']):
                    file_path = conflict['path']
                    backup_path = os.path.join(self.backup_dir, file_path)

                    # Create directory structure
                    os.makedirs(os.path.dirname(backup_path), exist_ok=True)

                    # Copy file
                    shutil.copy2(conflict['full_path'], backup_path)
                    self.debug_log(f"Backed up: {file_path}")

            return True
        except Exception as e:
            self.debug_log(f"Error backing up conflicted files: {str(e)}")
            return False

    def resolve_use_ours(self, file_path=None):
        """Resolve conflict using our version (local)"""
        if not self.git_manager or not self.git_manager.repo:
            raise ValueError("Git manager not initialized")

        try:
            repo = self.git_manager.repo

            if file_path:
                # Resolve specific file
                repo.git.checkout('--ours', file_path)
                repo.git.add(file_path)
                self.debug_log(f"Resolved conflict using ours: {file_path}")
                return True
            else:
                # Resolve all conflicts
                for conflict in self.conflict_files:
                    if conflict['status'] in ['both_modified', 'added_by_them']:
                        repo.git.checkout('--ours', conflict['path'])
                        repo.git.add(conflict['path'])
                    elif conflict['status'] == 'deleted_by_us':
                        # If we deleted it, keep it deleted
                        repo.git.rm(conflict['path'])
                    elif conflict['status'] == 'added_by_us':
                        # If we added it, keep our version
                        repo.git.add(conflict['path'])

                self.debug_log("Resolved all conflicts using ours")
                return True
        except Exception as e:
            self.debug_log(f"Error resolving conflicts using ours: {str(e)}")
            return False

    def resolve_use_theirs(self, file_path=None):
        """Resolve conflict using their version (remote)"""
        if not self.git_manager or not self.git_manager.repo:
            raise ValueError("Git manager not initialized")

        try:
            repo = self.git_manager.repo

            if file_path:
                # Resolve specific file
                repo.git.checkout('--theirs', file_path)
                repo.git.add(file_path)
                self.debug_log(f"Resolved conflict using theirs: {file_path}")
                return True
            else:
                # Resolve all conflicts
                for conflict in self.conflict_files:
                    if conflict['status'] in ['both_modified', 'added_by_us']:
                        repo.git.checkout('--theirs', conflict['path'])
                        repo.git.add(conflict['path'])
                    elif conflict['status'] == 'deleted_by_them':
                        # If they deleted it, keep it deleted
                        repo.git.rm(conflict['path'])
                    elif conflict['status'] == 'added_by_them':
                        # If they added it, keep their version
                        repo.git.add(conflict['path'])

                self.debug_log("Resolved all conflicts using theirs")
                return True
        except Exception as e:
            self.debug_log(f"Error resolving conflicts using theirs: {str(e)}")
            return False

    def abort_merge(self):
        """Abort the current merge operation"""
        if not self.git_manager or not self.git_manager.repo:
            raise ValueError("Git manager not initialized")

        try:
            repo = self.git_manager.repo
            repo.git.merge('--abort')
            self.debug_log("Merge aborted")
            return True
        except Exception as e:
            self.debug_log(f"Error aborting merge: {str(e)}")
            return False

    def complete_merge(self, commit_message=None):
        """Complete the merge after conflicts have been resolved"""
        if not self.git_manager or not self.git_manager.repo:
            raise ValueError("Git manager not initialized")

        try:
            repo = self.git_manager.repo

            # Check if all conflicts are resolved
            status_output = repo.git.status()
            if "All conflicts fixed but you are still merging" in status_output:
                # All conflicts are resolved, commit the merge
                if not commit_message:
                    commit_message = f"Merge conflict resolution - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

                repo.git.commit(m=commit_message)
                self.debug_log(f"Merge completed with message: {commit_message}")
                return True
            else:
                # Check if there are still unresolved conflicts
                if "You have unmerged paths" in status_output:
                    self.debug_log("Cannot complete merge: There are still unresolved conflicts")
                    return False
                elif "nothing to commit" in status_output:
                    # No changes to commit, merge may have been already completed
                    self.debug_log("Nothing to commit, merge may have been already completed")
                    return True

            return False
        except Exception as e:
            self.debug_log(f"Error completing merge: {str(e)}")
            return False

    def get_conflict_content(self, file_path):
        """Get the content of a conflicted file with markers"""
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            return content
        except Exception as e:
            self.debug_log(f"Error reading conflicted file: {str(e)}")
            return None

    def save_edited_content(self, file_path, content):
        """Save edited content to resolve conflict manually"""
        try:
            # Write the edited content to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Add the file to mark conflict as resolved
            if self.git_manager and self.git_manager.repo:
                self.git_manager.repo.git.add(file_path)

            self.debug_log(f"Saved edited content for: {file_path}")
            return True
        except Exception as e:
            self.debug_log(f"Error saving edited content: {str(e)}")
            return False
