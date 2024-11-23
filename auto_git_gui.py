import os
import time
import subprocess
import logging
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import paramiko
from datetime import datetime
import re
import shutil

class SSHGitBackup:
    def __init__(self, notes_path, repo_url, ssh_key_path=None, branch='main', username=None, password=None):
               self.notes_path = os.path.abspath(notes_path)
               self.repo_url = repo_url
               self.branch = branch
               self.repo_name = self._extract_repo_name(repo_url)
               self.ssh_key_path = ssh_key_path
               self.username = username
               self.password = password
               self.is_ssh = self._is_ssh_url(repo_url)
               self.backup_status = {}

               logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
               self.logger = logging.getLogger(__name__)

               # Set up git credentials right after initialization
               if not self.is_ssh and self.username and self.password:
                   self._setup_https_credentials()

    def _setup_https_credentials(self):
            """Setup HTTPS credentials using Git credential helper."""
            try:
                # Create the credentials file
                credentials_file = os.path.expanduser('~/.git-credentials')

                # Format the URL with credentials
                parsed_url = self.repo_url.rstrip('/')
                if not parsed_url.startswith('https://'):
                    parsed_url = 'https://' + parsed_url.split('://')[-1]

                credential_url = parsed_url.replace('https://', f'https://{self.username}:{self.password}@')

                # Write credentials to file
                with open(credentials_file, 'w') as f:
                    f.write(credential_url + '\n')

                # Configure Git to use the credential store
                subprocess.run(['git', 'config', '--global', 'credential.helper', 'store'], check=True)

                self.logger.info("HTTPS credentials configured successfully")
                return True
            except Exception as e:
                self.logger.error(f"Failed to setup HTTPS credentials: {e}")
                return False

    def _is_ssh_url(self, url):
            """Determine if the URL is SSH format."""
            return url.startswith('git@') or url.startswith('ssh://')

    def _extract_repo_name(self, repo_url):
            """Extract repository name from URL."""
            try:
                if self._is_ssh_url(repo_url):
                    return repo_url.split(':')[-1].replace('.git', '').split('/')[-1]
                else:
                    return repo_url.split('/')[-1].replace('.git', '')
            except Exception as e:
                self.logger.error(f"Failed to extract repo name from URL: {e}")
                return "backup_repository"

    def setup_git_config(self):
            """Setup git configuration based on authentication method."""
            try:
                if self.is_ssh and self.ssh_key_path:
                    # SSH configuration
                    ssh_command = f"ssh -i {self.ssh_key_path} -o StrictHostKeyChecking=no"
                    subprocess.run(['git', 'config', '--global', 'core.sshCommand', ssh_command], check=True)
                elif not self.is_ssh and self.username and self.password:
                    # HTTPS configuration - reuse existing credentials
                    pass  # Credentials are already set up in __init__

                subprocess.run(['git', 'config', '--global', 'pull.rebase', 'false'], check=True)
                self.logger.info("Git configuration updated successfully")
                return True
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Git config failed: {e}")
                return False

    def _find_default_ssh_key(self):
        """Find default SSH key with expanded key types."""
        key_types = ['id_rsa', 'id_ed25519', 'id_ecdsa', 'id_dsa']
        for key_type in key_types:
            path = os.path.expanduser(f'~/.ssh/{key_type}')
            if os.path.exists(path):
                return path
        return None

    def _test_ssh_connection(self):
        """Test SSH connection with improved error handling."""
        try:
            if self.ssh_key_path.endswith('.pub'):
                raise ValueError("Cannot use public key for SSH authentication")

            key = paramiko.RSAKey.from_private_key_file(self.ssh_key_path)
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect('github.com', username='git', pkey=key, timeout=10)
            client.close()
            return True
        except paramiko.SSHException as e:
            self.logger.error(f"SSH Authentication failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"SSH Connection Test Failed: {e}")
            return False

    def init_repository(self):
        """Initialize repository with improved setup and source folder handling."""
        try:
            repo_path = os.path.join(os.path.expanduser('~'), self.repo_name)
            self.repo_path = repo_path

            # Create repo directory if it doesn't exist
            if not os.path.exists(repo_path):
                os.makedirs(repo_path)

            os.chdir(repo_path)

            # Check if git is already initialized
            if not os.path.exists(os.path.join(repo_path, '.git')):
                # Initialize new repository
                subprocess.run(['git', 'init'], check=True)
                subprocess.run(['git', 'checkout', '-b', self.branch], check=True)

                # Configure remote
                try:
                    subprocess.run(['git', 'remote', 'remove', 'origin'], check=True)
                except subprocess.CalledProcessError:
                    pass  # Ignore if remote doesn't exist

                subprocess.run(['git', 'remote', 'add', 'origin', self.repo_url], check=True)

                # Create .gitignore
                self._create_gitignore(repo_path)

                # Make initial commit if needed
                try:
                    subprocess.run(['git', 'add', '.gitignore'], check=True)
                    subprocess.run(['git', 'commit', '-m', "Initial commit: Setup repository"], check=True)
                except subprocess.CalledProcessError:
                    pass  # Ignore if commit fails

            # Copy files from source to repo
            if os.path.exists(self.notes_path):
                self._sync_files(self.notes_path, repo_path)
            else:
                raise Exception(f"Source path does not exist: {self.notes_path}")

            self.logger.info(f"Repository ready at {repo_path}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Repository initialization failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during repository initialization: {e}")
            return False

    def _create_gitignore(self, repo_path):
        """Create .gitignore with common patterns."""
        gitignore_content = """
        .*
        !.gitignore
        !.github/
        .DS_Store
        Thumbs.db
        *.swp
        *.bak
        *.tmp
        .env
        node_modules/
        __pycache__/
        *.pyc
        """
        with open(os.path.join(repo_path, '.gitignore'), 'w') as f:
            f.write(gitignore_content.strip())

    def setup_git_config(self):
        """Setup git configuration with error handling."""
        try:
            ssh_command = f"ssh -i {self.ssh_key_path} -o StrictHostKeyChecking=no"
            subprocess.run(['git', 'config', '--global', 'core.sshCommand', ssh_command], check=True)
            subprocess.run(['git', 'config', '--global', 'pull.rebase', 'false'], check=True)
            self.logger.info("Git SSH configuration updated")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git config failed: {e}")
            return False


    def init_repository(self):
        """Initialize repository with improved setup."""
        try:
            repo_path = os.path.join(os.path.expanduser('~'), self.repo_name)

            if not os.path.exists(repo_path):
                os.makedirs(repo_path)

            os.chdir(repo_path)

            # Check if git is already initialized
            if not os.path.exists(os.path.join(repo_path, '.git')):
                # Initialize new repository
                subprocess.run(['git', 'init'], check=True)
                subprocess.run(['git', 'checkout', '-b', self.branch], check=True)

                # Configure remote
                try:
                    subprocess.run(['git', 'remote', 'remove', 'origin'], check=True)
                except subprocess.CalledProcessError:
                    pass  # Ignore if remote doesn't exist

                subprocess.run(['git', 'remote', 'add', 'origin', self.repo_url], check=True)

                # Create .gitignore
                self._create_gitignore(repo_path)

                # Make initial commit if needed
                try:
                    subprocess.run(['git', 'add', '.gitignore'], check=True)
                    subprocess.run(['git', 'commit', '-m', "Initial commit: Setup repository"], check=True)
                except subprocess.CalledProcessError:
                    pass  # Ignore if commit fails

            self.logger.info(f"Repository ready at {repo_path}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Repository initialization failed: {e}")
            return False

    def _clean_submodule_state(self):
        """Clean up problematic submodule state."""
        try:
            # Remove submodule from .gitmodules if it exists
            if os.path.exists('.gitmodules'):
                subprocess.run(['git', 'config', '--file', '.gitmodules', '--remove-section',
                              'submodule.Turtle_notes/cs_notes'], check=False)

            # Remove submodule from .git/config
            subprocess.run(['git', 'config', '--remove-section',
                           'submodule.Turtle_notes/cs_notes'], check=False)

            # Clean up submodule directories
            subprocess.run(['git', 'rm', '--cached', '-f', 'Turtle_notes/cs_notes'], check=False)

            # Remove the submodule directory from .git
            git_submodule_path = os.path.join('.git', 'modules', 'Turtle_notes/cs_notes')
            if os.path.exists(git_submodule_path):
                shutil.rmtree(git_submodule_path, ignore_errors=True)

            # Commit the cleanup if there are changes
            try:
                subprocess.run(['git', 'add', '.gitmodules'], check=False)
                subprocess.run(['git', 'commit', '-m', "Clean up submodule state"], check=False)
            except:
                pass

            return True
        except Exception as e:
            self.logger.error(f"Error cleaning submodule state: {e}")
            return False

    def _initialize_submodule(self, submodule_path):
        """Initialize a submodule with proper error handling."""
        try:
            # Get absolute path of the submodule
            abs_submodule_path = os.path.join(self.notes_path, 'Turtle_notes/cs_notes')
            rel_submodule_path = 'Turtle_notes/cs_notes'

            # Check if it's already a submodule
            submodule_status = subprocess.run(
                ['git', 'submodule', 'status', rel_submodule_path],
                capture_output=True,
                text=True
            ).stdout.strip()

            if not submodule_status:
                # Clean up any existing problematic state
                self._clean_submodule_state()

                # Initialize new submodule
                try:
                    # First, check if the target directory exists and is a git repo
                    target_git_dir = os.path.join(abs_submodule_path, '.git')
                    if os.path.exists(target_git_dir):
                        # Get the remote URL from the existing repository
                        os.chdir(abs_submodule_path)
                        remote_url = subprocess.run(
                            ['git', 'config', '--get', 'remote.origin.url'],
                            capture_output=True,
                            text=True
                        ).stdout.strip()
                        os.chdir(self.repo_path)

                        if remote_url:
                            # Add submodule using the existing remote URL
                            subprocess.run(['git', 'submodule', 'add', remote_url, rel_submodule_path], check=True)
                        else:
                            raise Exception("No remote URL found in existing repository")
                    else:
                        raise Exception("Target directory is not a git repository")

                except subprocess.CalledProcessError as e:
                    if "already exists in the index" in str(e.stderr):
                        # If it's already in the index, try to recover
                        subprocess.run(['git', 'submodule', 'init'], check=False)
                        subprocess.run(['git', 'submodule', 'update'], check=False)
                    else:
                        raise

            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize submodule: {e}")
            return False

    def backup(self, force=False):
        """Complete backup method with enhanced error handling and support for both SSH and HTTPS."""
        try:
            # Modify the remote URL to include credentials if using HTTPS
            if not self.is_ssh and self.username and self.password:
                parsed_url = self.repo_url.rstrip('/')
                if not parsed_url.startswith('https://'):
                    parsed_url = 'https://' + parsed_url.split('://')[-1]
                self.repo_url = parsed_url.replace('https://', f'https://{self.username}:{self.password}@')

            # Setup repository path
            repo_path = os.path.join(os.path.expanduser('~'), self.repo_name)
            self.repo_path = repo_path

            # Initialize repository if needed
            if not self.init_repository():
                self.logger.error("Repository initialization failed")
                return False

            os.chdir(repo_path)

            # Setup git configuration based on authentication method
            if not self.setup_git_config():
                self.logger.error("Git configuration failed")
                return False

            # Initialize submodule with error handling
            submodule_success = self._initialize_submodule('Turtle_notes/cs_notes')
            if not submodule_success:
                self.logger.warning("Continuing backup without submodule initialization")

            # Sync files from source to destination
            try:
                self._sync_files(self.notes_path, repo_path)
            except Exception as e:
                self.logger.error(f"File synchronization failed: {e}")
                return False

            # Handle submodules if they exist
            try:
                subprocess.run(['git', 'submodule', 'foreach', 'git', 'add', '-A'], check=False)
                subprocess.run(['git', 'submodule', 'foreach', 'git', 'commit', '-m',
                              f"Submodule update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"],
                              check=False)
            except Exception as e:
                self.logger.warning(f"Submodule update warning: {e}")

            # Add all changes including submodule references
            try:
                subprocess.run(['git', 'add', '-A'], check=True)
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to add files to git: {e}")
                return False

            # Get status and check for changes
            try:
                status_output = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    capture_output=True,
                    text=True
                ).stdout.strip()
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to get git status: {e}")
                return False

            # Proceed with commit if there are changes or force flag is set
            if status_output or force:
                # Generate commit message
                commit_msg = self._generate_commit_message()

                # Attempt to commit changes
                try:
                    subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
                except subprocess.CalledProcessError as e:
                    if "nothing to commit" not in str(e.stderr):
                        self.logger.error(f"Commit failed: {e}")
                        return False
                    self.logger.info("No changes to commit")
                    return True

                # Pull changes with conflict handling
                try:
                    # Fetch first to check for updates
                    subprocess.run(['git', 'fetch', 'origin'], check=True)

                    # Check if we need to pull
                    local_commit = subprocess.run(['git', 'rev-parse', 'HEAD'],
                                               capture_output=True, text=True).stdout.strip()
                    remote_commit = subprocess.run(['git', 'rev-parse', f'origin/{self.branch}'],
                                                capture_output=True, text=True).stdout.strip()

                    if local_commit != remote_commit:
                        # Try pulling changes
                        try:
                            subprocess.run(['git', 'pull', '--no-rebase'], check=True)
                        except subprocess.CalledProcessError:
                            self.logger.warning("Pull failed, attempting to continue")

                            # Check for conflicts
                            if "CONFLICT" in subprocess.run(['git', 'status'],
                                                          capture_output=True, text=True).stdout:
                                self.logger.error("Merge conflicts detected")
                                self._handle_conflicts()
                                return False

                except subprocess.CalledProcessError as e:
                    self.logger.error(f"Failed to sync with remote: {e}")
                    return False

                # Push changes with retry logic and credential handling
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        # Set up push command with credentials if using HTTPS
                        push_cmd = ['git', 'push']
                        if attempt > 0:
                            user_response = messagebox.askyesno(
                                "Push Failed",
                                "Normal push failed. Would you like to force push? "
                                "This will overwrite remote changes!"
                            )
                            if user_response:
                                push_cmd.append('-f')
                            else:
                                self.logger.warning("Push cancelled by user")
                                return False

                        push_cmd.extend(['origin', self.branch])

                        # Execute push command
                        subprocess.run(push_cmd, check=True)
                        break  # If push successful, break the retry loop

                    except subprocess.CalledProcessError as e:
                        if attempt == max_retries - 1:  # Last attempt failed
                            self.logger.error(f"Failed to push changes after {max_retries} attempts: {e}")
                            return False
                        self.logger.warning(f"Push attempt {attempt + 1} failed, retrying...")
                        time.sleep(2)  # Wait before retry

                self.logger.info("Changes successfully pushed to repository")
                return True

            else:
                self.logger.info("No changes detected to backup")
                return True

        except subprocess.CalledProcessError as e:
            error_message = str(e)
            if hasattr(e, 'stderr') and e.stderr:
                error_message = e.stderr.decode()
            self.logger.error(f"Backup failed: {error_message}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during backup: {e}")
            return False
        finally:
            # Clean up credentials if using HTTPS
            if not self.is_ssh:
                credentials_file = os.path.expanduser('~/.git-credentials')
                if os.path.exists(credentials_file):
                    try:
                        os.remove(credentials_file)
                        subprocess.run(['git', 'config', '--global', '--unset', 'credential.helper'], check=True)
                    except Exception as e:
                        self.logger.warning(f"Failed to clean up credentials: {e}")

    def _sync_files(self, source, destination):
        """Improved sync method with better change detection."""
        try:
            # Reset backup status for new sync
            self.backup_status = {}

            # Ensure destination directory exists
            os.makedirs(destination, exist_ok=True)

            # Get lists of files
            source_files = set()
            for root, _, files in os.walk(source):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), source)
                    source_files.add(rel_path)

            dest_files = set()
            for root, _, files in os.walk(destination):
                if '.git' not in root.split(os.sep):  # Skip .git directory
                    for file in files:
                        rel_path = os.path.relpath(os.path.join(root, file), destination)
                        dest_files.add(rel_path)

            # Copy new and modified files
            for rel_path in source_files:
                src_file = os.path.join(source, rel_path)
                dest_file = os.path.join(destination, rel_path)

                # Create destination directory if needed
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)

                try:
                    # Copy if file is new or modified
                    if not os.path.exists(dest_file) or \
                       os.path.getmtime(src_file) > os.path.getmtime(dest_file) or \
                       os.path.getsize(src_file) != os.path.getsize(dest_file):
                        shutil.copy2(src_file, dest_file)
                        self.backup_status[rel_path] = 'updated'
                        self.logger.info(f"Updated: {rel_path}")
                except Exception as e:
                    self.logger.error(f"Failed to copy {rel_path}: {e}")
                    self.backup_status[rel_path] = 'failed'

            # Remove deleted files
            for rel_path in dest_files - source_files:
                if not rel_path.startswith('.git'):  # Skip .git files
                    try:
                        file_to_delete = os.path.join(destination, rel_path)
                        if os.path.exists(file_to_delete):
                            os.remove(file_to_delete)
                            self.backup_status[rel_path] = 'deleted'
                            self.logger.info(f"Deleted: {rel_path}")
                    except Exception as e:
                        self.logger.error(f"Failed to delete {rel_path}: {e}")

            # Remove empty directories
            for root, dirs, _ in os.walk(destination, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    if '.git' not in dir_path and not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        self.logger.info(f"Removed empty directory: {dir_path}")

        except Exception as e:
            self.logger.error(f"Sync error: {e}")
            raise

    def _generate_commit_message(self):
        """Generate detailed commit message including deletions."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated_files = len([f for f, status in self.backup_status.items() if status == 'updated'])
        deleted_files = len([f for f, status in self.backup_status.items() if status == 'deleted'])
        failed_files = len([f for f, status in self.backup_status.items() if status == 'failed'])

        msg = f"Backup: {timestamp}\n\n"
        if updated_files > 0:
            msg += f"Files updated: {updated_files}\n"
        if deleted_files > 0:
            msg += f"Files deleted: {deleted_files}\n"
        if failed_files > 0:
            msg += f"Files failed: {failed_files}\n"
        return msg

    def handle_git_pull(self):
        """Enhanced git pull handling."""
        try:
            subprocess.run(['git', 'fetch', 'origin'], check=True)
            subprocess.run(['git', 'pull', '--no-rebase'], check=True)
            return True
        except subprocess.CalledProcessError as e:
            if "CONFLICT" in subprocess.run(['git', 'status'], capture_output=True, text=True).stdout:
                self.logger.error("Merge conflicts detected")
                self._handle_conflicts()
                return False
            self.logger.error(f"Pull failed: {e}")
            return False

    def _handle_conflicts(self):
        """Handle merge conflicts."""
        try:
            # Create backup of conflicted files
            status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
            for line in status.stdout.splitlines():
                if line.startswith('UU'):
                    file_path = line[3:].strip()
                    backup_path = f"{file_path}.backup"
                    shutil.copy2(file_path, backup_path)
                    self.logger.info(f"Created backup of conflicted file: {backup_path}")

            # Reset to pre-conflict state
            subprocess.run(['git', 'reset', '--hard', 'HEAD'], check=True)
            self.logger.info("Reset to pre-conflict state")
        except Exception as e:
            self.logger.error(f"Error handling conflicts: {e}")

# BackupApp s and other UI methods...

class BackupApp:
    def __init__(self, root):
            self.root = root
            self.root.title("Git Backup Tool")
            self.root.geometry("800x600")
            self.create_widgets()
            self.backup_thread = None
            self.is_backing_up = False

    def create_widgets(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Settings Frame
        settings_frame = ttk.LabelFrame(main_frame, text="Backup Settings", padding="10")
        settings_frame.pack(fill=tk.X, padx=5, pady=5)

        # Grid layout for settings
        self.notes_path_entry = self._create_path_entry(settings_frame, "Notes Path:", 0, self.browse_notes_path)
        self._create_repo_url_entry(settings_frame, "Repository URL:", 1)

        # Authentication Frame
        auth_frame = ttk.LabelFrame(main_frame, text="Authentication", padding="10")
        auth_frame.pack(fill=tk.X, padx=5, pady=5)

        # SSH Authentication
        self.auth_var = tk.StringVar(value="ssh")
        ttk.Radiobutton(auth_frame, text="SSH", variable=self.auth_var, value="ssh",
                       command=self.toggle_auth_method).pack(anchor=tk.W)

        self.ssh_frame = ttk.Frame(auth_frame)
        self.ssh_frame.pack(fill=tk.X)
        self._create_ssh_key_entry(self.ssh_frame, "SSH Key Path:", 0, self.browse_ssh_key)

        # HTTPS Authentication
        ttk.Radiobutton(auth_frame, text="HTTPS", variable=self.auth_var, value="https",
                       command=self.toggle_auth_method).pack(anchor=tk.W)

        self.https_frame = ttk.Frame(auth_frame)
        self.https_frame.pack(fill=tk.X)
        self._create_https_entries(self.https_frame)
        self.https_frame.pack_forget()  # Hidden by default

        # Branch entry
        self._create_branch_entry(settings_frame, "Branch:", 2)

        # Backup button
        self.backup_button = ttk.Button(main_frame, text="Start Backup", command=self.start_backup)
        self.backup_button.pack(pady=10)

        # Status text box
        self.status_text = scrolledtext.ScrolledText(main_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _create_path_entry(self, parent, label_text, row, browse_command):
        label = ttk.Label(parent, text=label_text)
        label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        path_entry = ttk.Entry(parent, width=50)
        path_entry.grid(row=row, column=1, padx=5, pady=5)
        browse_button = ttk.Button(parent, text="Browse", command=browse_command)
        browse_button.grid(row=row, column=2, padx=5, pady=5)
        return path_entry

    def _create_repo_url_entry(self, parent, label_text, row):
        label = ttk.Label(parent, text=label_text)
        label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.repo_url_entry = ttk.Entry(parent, width=50)
        self.repo_url_entry.grid(row=row, column=1, padx=5, pady=5)

    def _create_ssh_key_entry(self, parent, label_text, row, browse_command):
        label = ttk.Label(parent, text=label_text)
        label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.ssh_key_entry = ttk.Entry(parent, width=50)
        self.ssh_key_entry.grid(row=row, column=1, padx=5, pady=5)
        browse_button = ttk.Button(parent, text="Browse", command=browse_command)
        browse_button.grid(row=row, column=2, padx=5, pady=5)

    def _create_branch_entry(self, parent, label_text, row):
        label = ttk.Label(parent, text=label_text)
        label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.branch_entry = ttk.Entry(parent, width=50)
        self.branch_entry.grid(row=row, column=1, padx=5, pady=5)

    def browse_notes_path(self):
        path = filedialog.askdirectory()
        if path:
            self.notes_path_entry.delete(0, tk.END)
            self.notes_path_entry.insert(0, path)



    def browse_ssh_key(self):
        # Open the file dialog with filter for RSA files and all files
        ssh_key_path = filedialog.askopenfilename(
            title="Select SSH Key",
            filetypes=[("RSA Key Files", "*.rsa"), ("All Files", "*.*")]
        )

        # If the user selects a file, update the entry
        if ssh_key_path:
            self.ssh_key_entry.delete(0, tk.END)  # Clear the entry
            self.ssh_key_entry.insert(0, ssh_key_path)


    def _create_https_entries(self, parent):
            # Username
            username_label = ttk.Label(parent, text="Username:")
            username_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            self.username_entry = ttk.Entry(parent, width=50)
            self.username_entry.grid(row=0, column=1, padx=5, pady=5)

            # Password
            password_label = ttk.Label(parent, text="Password/Token:")
            password_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            self.password_entry = ttk.Entry(parent, width=50, show="*")
            self.password_entry.grid(row=1, column=1, padx=5, pady=5)

    def toggle_auth_method(self):
            if self.auth_var.get() == "ssh":
                self.https_frame.pack_forget()
                self.ssh_frame.pack(fill=tk.X)
            else:
                self.ssh_frame.pack_forget()
                self.https_frame.pack(fill=tk.X)

    def start_backup(self):
            if self.is_backing_up:
                messagebox.showinfo("Backup In Progress", "A backup is already in progress.")
                return

            # Gather input values
            notes_path = self.notes_path_entry.get()
            repo_url = self.repo_url_entry.get()
            branch = self.branch_entry.get() or 'main'

            # Get authentication details based on selected method
            if self.auth_var.get() == "ssh":
                ssh_key_path = self.ssh_key_entry.get()
                backup = SSHGitBackup(notes_path, repo_url, ssh_key_path=ssh_key_path, branch=branch)
            else:
                username = self.username_entry.get()
                password = self.password_entry.get()
                backup = SSHGitBackup(notes_path, repo_url, username=username, password=password, branch=branch)

            self.is_backing_up = True
            self.update_status("Starting backup...")

            self.backup_thread = threading.Thread(target=self.run_backup, args=(backup,))
            self.backup_thread.start()

    def run_backup(self, backup):
        success = backup.backup()
        self.is_backing_up = False
        if success:
            self.update_status("Backup completed successfully.")
        else:
            self.update_status("Backup failed. Check the logs for more details.")

    def update_status(self, message):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.yview(tk.END)
        self.status_text.config(state=tk.DISABLED)

# Running the application
if __name__ == "__main__":
    root = tk.Tk()
    app = BackupApp(root)
    root.mainloop()
