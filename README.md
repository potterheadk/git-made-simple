
---

# Git Made Simple — Simplifying Git for Everyone

<p align="center">
  <img src="placeholder.png" alt="Git Made Simple Screenshot" width="600"> 
  <!-- TODO: Replace placeholder.png with an actual screenshot of the application -->
</p>

**Git Made Simple** is a clean, intuitive desktop application built with **Python** and **PySide6**, designed to help you manage your Git repositories without ever touching a terminal (unless you want to 😉).

Whether you're a beginner or just prefer a GUI over the command line, Git Made Simple lets you handle version control like a pro — no cryptic commands, just smooth Git operations.

---

## ✨ Features You'll Love

- 🎉 **One-Click Setup**: Initialize or connect to Git repositories instantly.
- 🌐 **Remote Management**: Easily set/update remote URLs (HTTPS or SSH).
- 💬 **Commit, Push, Pull**: Core Git actions made straightforward.
- 🔄 **Smart File Sync**: Detect changes and sync with just a click.
- ⚔️ **Visual Conflict Resolver**:
  - See conflicted files listed clearly.
  - Choose “Yours” vs “Theirs” or edit manually with syntax highlighting.
  - View simplified diffs and resolve conflicts visually.
- 🌿 **Branching Simplified**: Switch, create, or checkout branches with ease.
- 🚫 **Built-in `.gitignore` Editor**:
  - Apply a default or add presets (Python, Node.js, etc.)
  - Edit directly in-app.
- 🔍 **Change Tracker**: Review file changes before you commit.
- 📜 **Sync History**: View a timeline of your sync operations.
- 🔐 **SSH Support**: Add and manage your SSH keys.
- 🛠️ **Advanced Tools** *(use with care)*:
  - Force Push
  - Hard Reset (wipe local changes)
- 📘 **Live Output Log**: Timestamped operation logs.
- 🖼️ **Modern UI**: Clean design with a subtle, eye-friendly color theme.

---

## 📦 Requirements

- **Python**: 3.7+
- **Git**: Installed and available in your system's PATH
- **pip**: Should come with Python

---

## ⚙️ Installation Guide

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/potterheadk/git-made-simple.git
   cd git-made-simple
   ```

2. **Create a Virtual Environment (Recommended):**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   Add this to `requirements.txt`:
   ```txt
   PySide6>=6.0.0
   GitPython>=3.1.0
   ```
   Then install:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🏃 Quick Start

1. **Launch the App**:
   ```bash
   python git-made-simple/main.py
   ```

2. **Connect or Init a Repo**:
   - Browse to your local folder
   - Add a remote URL (optional)
   - Pick HTTPS or SSH (you can select a private key for SSH)
   - Hit **Initialize** and you’re good to go!

3. **Manage Your Repo**:
   - Click **Sync All** to auto-detect changes and push with a timestamped commit.
   - Use buttons like:
     - **Commit**: With your own message
     - **Push/Pull**: To update your remote/local

4. **Merge Conflicts? No Stress**:
   - A dialog pops up automatically.
   - Pick a file, choose a resolution method, or edit manually.
   - Click **Apply** → repeat → **Complete Merge**.

5. **More Tools**:
   - **Branch Manager**: Create, switch, or delete branches.
   - **`.gitignore` Editor**: Add patterns or presets.
   - **View Changes**: Get a clear breakdown of what's changed.

---

## 🗂️ Project Structure

```
git-made-simple/
├── core/
│   ├── git_manager.py         # Git commands & repo logic
│   ├── file_sync.py           # Detects/stages changes
│   ├── conflict_handler.py    # Merge conflict logic
│   └── gitignore_manager.py   # Manages .gitignore
├── gui/
│   ├── main_window.py         # Main GUI window
│   ├── animated_dialog.py     # Dialogs with animations
│   ├── *_dialog.py            # Specialized dialogs (branches, commits, etc.)
├── main.py                    # App entry point
```

Each component is modular, cleanly separated, and documented with in-line comments.

---

## 🔮 Coming Soon...

We're working on even more features:

- 🔐 **Credential Manager**: Store your HTTPS credentials securely.
- ⏱️ **Scheduled Syncs**: Set auto-backups at intervals.
- 📥 **Stashing Support**: Temporarily save your local changes.
- 🖥️ **Better Diffs**: Advanced side-by-side comparison tools.
- 💡 Got ideas? [Submit a feature request!](#🤝-contributing)

---

## 🤝 Contributing

We welcome PRs! 💖

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push and open a PR 🎉

Report bugs and suggestions via GitHub Issues!

---

## 🧠 Fun Fact

This app was built because... not everyone dreams in terminal commands. If you’ve ever forgotten whether `git pull --rebase` will break something — **Git Made Simple** is your new best friend.

---
