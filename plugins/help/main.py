import os

# Plugin Configuration
config = {"label": "Help", "icon": "📘"}

def run():
    """Displays the comprehensive system manual and usage guidelines."""
    while True:
        os.system('clear')
        print("==========================================")
        print("       🚀  MANUAL         ")
        print("==========================================")
        print("\nThis system is composed of dynamic modules (plugins).")
        print("Select a section to learn more:")
        print("1) 🏗️ Web App Creator & Editor")
        print("2) 🧬 Auto-Evolve & System Growth")
        print("3) 🧠 Agent Mode (Total Control)")
        print("4) 🗂️ Project & App Management")
        print("5) 💡 General Tips & Shortcuts")
        print("\n0) 🔙 Back to Main Menu")

        choice = input("\nSelect a topic: ").strip()

        if choice == "0":
            break

        os.system('clear')
        if choice == "1":
            print("=== 🏗️ WEB APP CREATOR & EDITOR ===")
            print("\n- PURPOSE: Creates Single Page Applications (HTML/CSS/JS).")
            print("- USAGE: Provide a project name and an idea. The AI generates")
            print("  code in ---CODE--- and ---SUGGESTION--- format.")
            print("- STORAGE: Files are saved in 'my_apps/<name>/index.html'.")
            print("- PREVIEW: If the local server (port 8080) is off, the plugin")
            print("  will offer to start it and open your browser automatically.")

        elif choice == "2":
            print("=== 🧬 AUTO-EVOLVE (SYSTEM EDITOR) ===")
            print("\n- PURPOSE: Scans the OS context and updates plugins.")
            print("- USAGE: Create new plugins (as folders) or fix existing ones.")
            print("- CONTEXT: This module reads 'totalcode.txt' so the AI knows")
            print("  exactly how your system works before writing code.")
            print("- WARNING: Always review the code generated in 'plugins/'")
            print("  before executing it. Use 'Time Machine' if something breaks.")

        elif choice == "3":
            print("=== 🧠 AGENT MODE (TOTAL CONTROL) ===")
            print("\n- PURPOSE: A flexible mode for various system/mobile tasks.")
            print("- USAGE: Type any command for your environment. The agent")
            print("  usually responds with Python code to be executed.")
            print("- POWER: It can move files, check system status, or organize")
            print("  your project structure autonomously.")

        elif choice == "4":
            print("=== 🗂️ PROJECT & APP MANAGEMENT ===")
            print("\n- APPS MANAGER: Lists projects in 'my_apps/', opens them in")
            print("  the browser, or executes 'main.py' if it exists.")
            print("- VISUAL LIST: Generates a mobile-style launcher to browse")
            print("  your web apps visually.")
            print("- DELETE APPS: Safely removes project folders. It includes")
            print("  security checks to prevent accidental deletions.")

        elif choice == "5":
            print("=== 💡 GENERAL TIPS & SHORTCUTS ===")
            print("\n- WORKING DIRECTORY: Your creations live in 'my_apps/'.")
            print("- PLUGINS FOLDER: System tools live in 'plugins/'.")
            print("- FORMATS: Many modules rely on ---CODE--- tags. Do not")
            print("  modify these if you want the processor to parse them.")
            print("- BROWSER: If 'termux-open-url' is missing, the OS will")
            print("  attempt to use the standard system browser.")
            print("- REQUIREMENTS: For advanced health stats, run:")
            print("  'pip install psutil'")
            print("\nQUICK COMMANDS:")
            print("- Manual Server: python -m http.server 8080")
            print("- List Apps: ls my_apps")

        input("\n\n[Press Enter to return to Help Menu]")

if __name__ == "__main__":
    run()