# core/gitignore_manager.py
import os
import logging

class GitIgnoreManager:
    def __init__(self, git_manager=None):
        self.git_manager = git_manager
        self.default_ignores = [
            # Python
            "__pycache__/",
            "*.py[cod]",
            "*$py.class",
            "*.so",
            ".Python",
            "env/",
            "venv/",
            "ENV/",
            "build/",
            "develop-eggs/",
            "dist/",
            "downloads/",
            "eggs/",
            ".eggs/",
            "lib/",
            "lib64/",
            "parts/",
            "sdist/",
            "var/",
            "*.egg-info/",
            ".installed.cfg",
            "*.egg",

            # Environments and secrets
            ".env",
            ".venv",
            ".env.*",
            "*.env",
            "env.local",
            "env.development",
            "env.test",
            "env.production",
            ".secrets",
            "secrets.*",

            # IDE files
            ".idea/",
            ".vscode/",
            "*.swp",
            "*.swo",
            ".DS_Store",
            ".DS_Store?",

            # Logs
            "*.log",
            "logs/",

            # Node
            "node_modules/",
            "npm-debug.log",

            # Others
            ".git/",
            ".cache/",
            "coverage/",
            ".coverage",
            "htmlcov/"
        ]

    def set_git_manager(self, git_manager):
        """Set the Git manager instance"""
        self.git_manager = git_manager

    def get_gitignore_path(self, repo_path):
        """Get path to .gitignore file"""
        return os.path.join(repo_path, '.gitignore')

    def read_gitignore(self, repo_path):
        """Read existing .gitignore file or return default contents"""
        gitignore_path = self.get_gitignore_path(repo_path)

        if os.path.exists(gitignore_path):
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return content
            except Exception as e:
                logging.error(f"Error reading .gitignore: {str(e)}")
                return ""
        else:
            # Return default gitignore content
            return "\n".join(self.default_ignores)

    def save_gitignore(self, repo_path, content):
        """Save content to .gitignore file"""
        gitignore_path = self.get_gitignore_path(repo_path)

        try:
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Add .gitignore to git if git manager is available
            if self.git_manager and self.git_manager.repo:
                try:
                    self.git_manager.repo.git.add(gitignore_path)
                    # We don't commit automatically here - user can commit through normal workflow
                except Exception as e:
                    logging.error(f"Error adding .gitignore to git: {str(e)}")

            return True
        except Exception as e:
            logging.error(f"Error saving .gitignore: {str(e)}")
            return False

    def get_default_gitignore(self):
        """Get default gitignore content"""
        return "\n".join(self.default_ignores)

    def apply_default_gitignore(self, repo_path):
        """Apply default gitignore to repository"""
        return self.save_gitignore(repo_path, self.get_default_gitignore())
