# 🌳 acornix

**The intelligent seed for your Termux ecosystem.**

`acornix` is an AI-powered assistant designed to generate apps, manage plugins, and automate workflows directly from your terminal. Built with a nod to the legacy of **Acorn Computers** and the power of **ARM** architecture, it transforms your phone into a portable development powerhouse.

---

## 1. Environment Setup (Android)
Before touching the code, you need the base tools on your mobile device:

* **Install Termux:** Download it preferably from F-Droid or its official GitHub (the Google Play version is obsolete). [Termux](https://f-droid.org/es/packages/com.termux/)
* **Install Termux:API:** Download the Termux:API extension (this allows the AI to control phone functions). [Termux:API](https://f-droid.org/es/packages/com.termux/)


Open Termux and update everything is up to date before you begin:

```bash
pkg update && pkg upgrade
```

---

## 2. Initial Configuration
Open Termux and make sure everything is updated before starting:

## 🚀 Quick Install

Run this command in Termux to set up everything automatically (dependencies, permissions, and alias):

```bash
pkg update && pkg upgrade -y && pkg install python git termux-api binutils -y && termux-setup-storage && git clone [https://github.com/gonzaroman/acornix.git](https://github.com/gonzaroman/acornix.git) && cd acornix && pip install requests python-dotenv psutil && echo "alias acornix='cd $(pwd) && python main.py'" >> ~/.bashrc && source ~/.bashrc && python main.py
```



Note: You'll be asked for storage permissions. Please grant them to allow acornix to save your projects.

✨ Key Features
AI App Generator: Create web apps and scripts using natural language.

Plugin System: Extend acornix capabilities with modular plugins.

Termux Native: Fully optimized for mobile environments and ARM processors.

Zero Config: The one-liner takes care of everything, including your custom acornix command.

🛠 Usage
After installation, you can launch the system from anywhere by simply typing:

```bash
acornix
```
Main Menu Options:
Generate App: Describe what you want, and acornix will build it.

Manage Plugins: Install or update system extensions.

Launch Server: Preview your generated apps on your local network.

if you have a problem with the server, reebot the server:
```bash
pkill -f "python -m http.server"
python -m http.server 8080
```

# 🌳 acornix: The AI-Powered OS for Termux
> "Transform your mobile terminal into a neural development hub."

<img width="401" height="551" alt="Captura de pantalla 2026-02-12 113642" src="https://github.com/user-attachments/assets/4512a785-429c-482a-96bc-cca568c102df" />


**acornix** isn't just a script; it's a procedural engine designed to bridge the gap between AI intelligence and mobile hardware. It allows you to orchestrate complex applications, automate local environments, and extend your terminal capabilities using natural language.
Markdown
> "Transform your mobile terminal into a neural development hub."

**acornix** isn't just a script; it's a procedural engine designed to bridge the gap between AI intelligence and mobile hardware. It allows you to orchestrate complex applications, automate local environments, and extend your terminal capabilities using natural language.


You can create games, applications, or in agent mode, ask it to control your phone, such as opening YouTube and searching for a Nirvana video, or ask your phone to do anything, such as sending an S.O.S. signal with the flashlight. The only limit is your imagination.
You can create whatever you want and share it with whoever you want. The system has a simple tool for exporting and importing creations, apps, etc.
<br />

### 📸 Showcase
| | |
| :---: | :---: |
| <img src="https://github.com/user-attachments/assets/3c93ac34-93e7-438c-8c14-f37b43ccabb2" width="300" alt="avion"> | <img src="https://github.com/user-attachments/assets/f15c1201-72ab-4e8a-b76f-d34232688be7" width="300" alt="plano"> |
| <img src="https://github.com/user-attachments/assets/06667fcb-43b4-4098-839f-09383ce8aeb4" width="300" alt="arckanoid"> | <img src="https://github.com/user-attachments/assets/bca05911-68cf-4a70-be84-abc4e4fa1b23" width="300" alt="nirvana"> |


---

## 🧠 Why acornix?
Most mobile environments are limited. **acornix** breaks those barriers by using a **Context-Aware Architecture** to turn simple text prompts into fully functional, locally-hosted software.

---

## ✨ Advanced Capabilities

| Feature | Description | Technical Edge |
| :--- | :--- | :--- |
| **Neural Architect** | Generate high-performance web apps and Python tools from scratch. | Uses custom system prompts for ARM optimization. |
| **Modular Core** | Hot-swappable plugin system to add new commands without restarts. | Dynamic importing via `core/` logic. |
| **Environment Sync** | Automatic SFTP and local server management for instant previews. | Integrated `http.server` with automatic port cleanup. |
| **Hardware Mastery** | Direct access to Termux API for hardware-level interaction. | Low-level integration with `binutils` and `psutil`. |

---

## 🛠 Pro Workflow: From Idea to Execution
Don't just run code. **Build systems.** Here is how acornix handles the lifecycle of a project:

$$\text{Prompt} \xrightarrow{\text{IA Engine}} \text{Optimized Code} \xrightarrow{\text{Acornix Core}} \text{Local Deployment}$$

### Example Commands:
> *"Create a dashboard to monitor my device battery and CPU usage using a modern dark-mode UI."*

1.  **Generation:** acornix builds the HTML5/CSS3/JS bundle.
2.  **Deployment:** The system places it in `my_apps/monitor_pro`.
3.  **Hosting:** Start the local server and access it at `localhost:8080`.

---

## 📂 System Architecture
The heart of **acornix** is organized for scalability:

```text
acornix/
├── 🧠 main.py           # The Kernel: Entry point & process manager
├── 🛠 core/             # The Brain: Neural logic and prompt engineering
├── 🔌 plugins/          # The Limbs: Modular extensions for the system
├── 📦 my_apps/          # The Vault: AI-generated projects & assets
└── ⚙️ .env              # The DNA: Secure credentials and API keys
```
Gonzalo Román Márquez
