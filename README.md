
# 🚀 **Git-Made-Simple: Git Without the Grit!**

Tired of wrestling with Git commands? Meet **Git-Made-Simple**—your friendly neighborhood tool that helps you notice changes, track deletions, manage creations, and effortlessly push your code to GitHub. It's simple, yet powerful, and still evolving! 🌱✨

---

## 🎥 Demo Video  
Check out how **Git-Made-Simple** works in action!  


https://github.com/user-attachments/assets/3c35de66-9c88-41f2-ba90-3a10cf748fc3

---

## 🛠️ **Getting Started**
### **Important for Your Repository**  
When using this tool for your own repository, you **must** clone your repository using the correct URL format:  

- For **SSH access**, use:  
  ```bash
  git clone git@github.com:<your-username>/<your-repository>.git
  ```

- For **HTTPS access**, use:  
  ```bash
  git clone https://github.com/<your-username>/<your-repository>.git
  ```

> **Note:** If you don’t use the correct URL type (SSH or HTTPS), the script will prompt you for your credentials in the terminal.


### Step 1: Clone the Repository  
```bash
git clone https://github.com/potterheadk/github-made-simple.git
cd github-made-simple
```
---

### Step 2: Set Up Your Environment  
We recommend using a virtual environment for a clean setup. Here’s how to do it (example for Arch Linux):  
```bash
python -m venv venv
source venv/bin/activate
```

For other operating systems, search for your OS-specific instructions on Google! 😄  

---

### Step 3: Install Requirements  
```bash
pip install -r requirement.txt
```

---

### Step 4: Run the Script  
```bash
python auto_git_gui.py
```

---

## 🧑‍💻 **How to Use the Script**

### 🗝️ Method 1: SSH Access  
1. Ensure your GitHub account's SSH key is set up. Learn how to generate one [here](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).  
2. Place your private SSH key in the default directory:  
   - **Linux/Mac:** `~/.ssh/id_rsa`  
   - **Windows:** Your SSH key's path in your terminal tool (e.g., Git Bash).  
3. If you already have an `id_rsa` file (your private key), upload it in the **Browse** section in the script's UI by renaming it with a `.rsa` extension.  
4. In the script UI, select the **SSH method**, and you're ready to roll!

---

### 🔐 Method 2: HTTPS Access  
1. In the script UI, choose the **HTTPS method**.  
2. Enter your GitHub username and either your password or a personal access token (PAT).  
   - **Pro tip:** Tokens are safer than passwords! Learn how to create one [here](https://github.com/settings/tokens).

---

## 🧭 **Key Features**  
- **Track All Changes:** Detect additions, deletions, or updates with ease.  
- **Push with a Click:** No more terminal gymnastics!  
- **Simple and Lightweight:** Designed for efficiency without the bloat.
- **Some Error Handeling:** It handles submodules,clears cache if there is error in some cases.

---

## ⚠️ **Important Warnings!**  
1. **Clone First:** Always clone your repo before using this tool. It won't create a new repository for you.  
2. **Repo Selection:** Double-check the repository path in the UI. Picking the wrong path might result in data loss—ouch! 😬  

---

## 🤝 **Contributing**

### Found an Error? Create a PR!  
Help us improve! If you encounter bugs or have ideas for enhancements let me know :)

---

### Got Feature Ideas? Let’s Talk!  
Open an issue to suggest new features or improvements. We're always excited to grow with our community!  

---

## 🌟 **Happy Coding!**  
Git-Made-Simple has your back! 💪  
