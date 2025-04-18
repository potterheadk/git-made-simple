# core/git_manager.py
import os
import git
from git import Repo, GitCommandError
import subprocess
from datetime import datetime

# module imports
from core.conflict_handler import ConflictHandler
from core.gitignore_manager import GitIgnoreManager


class GitManager:
    def __init__(self):
        self.repo = None
        self.repo_path = None
        self.conflict_handler = ConflictHandler(self)
        self.gitignore_manager = GitIgnoreManager(self)

    def init_repo(self, path):
        """Initialize or open existing Git repository"""
        self.repo_path = path

        try:
            if not os.path.exists(os.path.join(path, '.git')):
                # Initialize new repo
                self.repo = Repo.init(path)
                return f"Initialized new Git repository at {path}"
            else:
                # Open existing repo
                self.repo = Repo(path)
                return f"Opened existing Git repository at {path}"
        except Exception as e:
            raise Exception(f"Failed to initialize repository: {str(e)}")

    def set_remote(self, url, name="origin"):
        """Set or update remote URL"""
        if self.repo is None:
            raise ValueError("Repository not initialized")

        try:
            # Check if remote exists
            try:
                remote = self.repo.remote(name)
                # Update URL if remote exists
                self.repo.git.remote('set-url', name, url)
                return f"Updated remote '{name}' URL to {url}"
            except ValueError:
                # Create new remote if it doesn't exist
                self.repo.create_remote(name, url)
                return f"Added new remote '{name}' with URL {url}"

        except Exception as e:
            raise Exception(f"Failed to set remote: {str(e)}")

    def push_changes(self, remote="origin", branch="master"):
        """Push local changes to remote"""
        if self.repo is None:
            raise ValueError("Repository not initialized")

        try:
            # First add all changes
            self.repo.git.add(A=True)

            # Check if there are changes to commit
            if self.repo.is_dirty() or len(self.repo.untracked_files) > 0:
                # Commit changes
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                commit_message = f"Automatic backup commit - {timestamp}"
                self.repo.git.commit(m=commit_message)
                commit_result = f"Committed changes with message: '{commit_message}'"
            else:
                commit_result = "No changes to commit"

            # Get current branch name
            try:
                current_branch = self.repo.active_branch.name
            except:
                # Detached HEAD state or other issues
                current_branch = branch

            # Push changes
            push_info = self.repo.git.push(remote, current_branch)

            return f"{commit_result}\nPush result: {push_info if push_info else 'Success'}"
        except GitCommandError as e:
            return f"Git error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"

    def pull_changes(self, remote="origin", branch=None, handle_conflicts=True):
        """Pull changes from remote"""
        if self.repo is None:
            raise ValueError("Repository not initialized")

        try:
            # Get current branch if not specified
            if branch is None:
                try:
                    branch = self.repo.active_branch.name
                except:
                    branch = "master"  # Default if can't determine

            # Pull changes
            try:
                pull_result = self.repo.git.pull(remote, branch)
                return f"Pull result: {pull_result if pull_result else 'Success (no changes)'}"
            except git.GitCommandError as e:
                # Check if this is a merge conflict
                if "CONFLICT" in str(e) or "Merge conflict" in str(e):
                    if handle_conflicts:
                        # Detect conflicts
                        if self.conflict_handler.detect_conflicts():
                            # Backup conflicted files
                            self.conflict_handler.backup_conflicted_files()
                            # Return conflict information
                            return {
                                "status": "conflict",
                                "message": "Merge conflicts detected",
                                "conflicts": len(self.conflict_handler.conflict_files),
                                "conflict_details": self.conflict_handler.conflict_files
                            }
                    return f"Git conflict during pull: {str(e)}"
                else:
                    return f"Git error during pull: {str(e)}"
        except Exception as e:
            return f"Error during pull: {str(e)}"

    def has_conflicts(self):
        """Check if repository has merge conflicts"""
        if self.repo is None:
            return False

        return self.conflict_handler.detect_conflicts()

    def get_status(self):
        """Get repository status"""
        if self.repo is None:
            return "Repository not initialized"

        try:
            status_output = self.repo.git.status()
            return status_output
        except Exception as e:
            return f"Error getting status: {str(e)}"

    def handle_conflicts(self):
        """Handle merge conflicts (placeholder for Phase 5)"""
        return "Conflict handling will be implemented in Phase 5"

    def sync_submodules(self):
        """Update and sync submodules if any"""
        if self.repo is None:
            raise ValueError("Repository not initialized")

        try:
            if len(self.repo.submodules) > 0:
                self.repo.git.submodule('update', '--init', '--recursive')
                return f"Synchronized {len(self.repo.submodules)} submodules"
            return "No submodules found"
        except Exception as e:
            return f"Error syncing submodules: {str(e)}"

    def force_push(self, remote="origin", branch=None):
        """Force push changes to remote (use with caution)"""
        if self.repo is None:
            raise ValueError("Repository not initialized")

        try:
            # Get current branch if not specified
            if branch is None:
                try:
                    branch = self.repo.active_branch.name
                except:
                    branch = "master"  # Default if can't determine

            # Force push
            result = self.repo.git.push(remote, branch, force=True)
            return f"Force push result: {result if result else 'Success'}"
        except git.GitCommandError as e:
            return f"Git error during force push: {str(e)}"
        except Exception as e:
            return f"Error during force push: {str(e)}"

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

    def get_current_branch(self):
        """Get the name of the current branch"""
        if self.repo is None:
            raise ValueError("Repository not initialized")

        try:
            return self.repo.active_branch.name
        except Exception as e:
            # Probably in detached HEAD state
            return "DETACHED_HEAD"

    def get_all_branches(self):
        """Get list of all branches (local and remote)"""
        if self.repo is None:
            raise ValueError("Repository not initialized")

        branches = {
            'local': [],
            'remote': []
        }

        try:
            # Get local branches
            for branch in self.repo.branches:
                branches['local'].append(branch.name)

            # Get remote branches
            for remote in self.repo.remotes:
                # Fetch from remote to ensure we have latest information
                try:
                    remote.fetch()
                except Exception as e:
                    logging.warning(f"Could not fetch from remote {remote.name}: {str(e)}")

                for ref in remote.refs:
                    # Skip HEAD reference
                    if ref.name.endswith('/HEAD'):
                        continue

                    # Remote branches are usually in the format 'origin/branch_name'
                    remote_branch = ref.name.split('/', 1)[1] if '/' in ref.name else ref.name
                    branches['remote'].append(remote_branch)

            return branches
        except Exception as e:
            logging.error(f"Error getting branches: {str(e)}")
            return branches
            def fetch_remote(self, remote_name="origin"):
                """Fetch updates from remote"""
                if self.repo is None:
                    raise ValueError("Repository not initialized")

                try:
                    if remote_name in [remote.name for remote in self.repo.remotes]:
                        remote = self.repo.remote(remote_name)
                        remote.fetch()
                        return f"Fetched updates from {remote_name}"
                    else:
                        available_remotes = [remote.name for remote in self.repo.remotes]
                        return f"Remote {remote_name} not found. Available remotes: {', '.join(available_remotes)}"
                except git.GitCommandError as e:
                    return f"Git error during fetch: {str(e)}"
                except Exception as e:
                    return f"Error during fetch: {str(e)}"

    def checkout_branch(self, branch_name, create=False):
        """Checkout a specific branch"""
        if self.repo is None:
            raise ValueError("Repository not initialized")

        try:
            # Check if branch exists
            if branch_name in [b.name for b in self.repo.branches]:
                self.repo.git.checkout(branch_name)
                return f"Switched to branch '{branch_name}'"
            elif create:
                # Create and checkout new branch
                self.repo.git.checkout('-b', branch_name)
                return f"Created and switched to new branch '{branch_name}'"
            else:
                # Try to checkout remote branch
                for remote in self.repo.remotes:
                    try:
                        remote_branch = f"{remote.name}/{branch_name}"
                        if remote_branch in [ref.name for ref in remote.refs]:
                            self.repo.git.checkout('-b', branch_name, remote_branch)
                            return f"Checked out remote branch '{branch_name}'"
                    except:
                        pass

                return f"Branch '{branch_name}' not found"
        except git.GitCommandError as e:
            return f"Git error during checkout: {str(e)}"
        except Exception as e:
            return f"Error during checkout: {str(e)}"

    def create_branch(self, branch_name):
        """Create a new branch"""
        if self.repo is None:
            raise ValueError("Repository not initialized")

        try:
            self.repo.git.branch(branch_name)
            return f"Created branch '{branch_name}'"
        except git.GitCommandError as e:
            return f"Git error creating branch: {str(e)}"
        except Exception as e:
            return f"Error creating branch: {str(e)}"

    def set_ssh_key(self, key_path):
        """Set SSH key for authentication"""
        if not os.path.exists(key_path):
            raise ValueError(f"SSH key file not found: {key_path}")

        # Set GIT_SSH_COMMAND environment variable
        os.environ['GIT_SSH_COMMAND'] = f'ssh -i {key_path} -o StrictHostKeyChecking=no'
        return f"SSH key set to: {key_path}"

    def push_changes_with_message(self, commit_message, remote="origin", branch=None):
        """Push local changes with custom commit message"""
        if self.repo is None:
            raise ValueError("Repository not initialized")

        try:
            # First add all changes
            self.repo.git.add(A=True)

            # Get current branch if not specified
            if branch is None:
                try:
                    branch = self.repo.active_branch.name
                except:
                    branch = "master"  # Default if can't determine

            # Check if there are changes to commit
            if self.repo.is_dirty() or len(self.repo.untracked_files) > 0:
                # Commit changes with custom message
                self.repo.git.commit(m=commit_message)
                commit_result = f"Committed changes with message: '{commit_message}'"
            else:
                commit_result = "No changes to commit"

            # Push changes
            push_info = self.repo.git.push(remote, branch)

            return f"{commit_result}\nPush result: {push_info if push_info else 'Success'}"
        except git.GitCommandError as e:
            return f"Git error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
