import os
import subprocess
import time
from core.utils import is_server_active

# Plugin Configuration
config = {"label": "APPs Manager", "icon": "🗂️"}

def _find_base_folder():
    """Locates the directory where applications are stored."""
    candidates = ["my_apps", "my_app"]
    for c in candidates:
        if os.path.isdir(c):
            return c
    # Create default folder if none exist
    os.makedirs("my_apps", exist_ok=True)
    return "my_apps"

def _list_projects(base_folder):
    """Returns a sorted list of directories inside the base folder."""
    try:
        entries = sorted([d for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d))])
        return entries
    except Exception:
        return []

def _start_server():
    """Starts a local Python HTTP server on port 8080."""
    print("\n📡 Starting background server (port 8080)...")
    subprocess.Popen(["python", "-m", "http.server", "8080"],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

def run():
    """Main loop for managing and launching projects."""
    base = _find_base_folder()
    while True:
        os.system('clear')
        print("=== 🗂️ APPs MANAGER ===")
        print(f"Base folder: {base}\n")
        projects = _list_projects(base)
        
        # CASE: No projects available
        if not projects:
            print("🚫 No projects found in the current folder.")
            print("1) Create an example project")
            print("0) Back")
            choice = input("\nSelect an option: ").strip()
            
            if choice == "1":
                example = os.path.join(base, "example_app")
                os.makedirs(example, exist_ok=True)
                with open(os.path.join(example, "index.html"), "w", encoding="utf-8") as f:
                    f.write("<!doctype html><html><head><title>Example</title></head><body><h1>Example App</h1><p>Ready to build!</p></body></html>")
                print("\n✅ Example project created successfully.")
                input("Press Enter to continue...")
                continue
            elif choice == "0":
                break
            else:
                continue

        # CASE: List available projects
        for i, p in enumerate(projects, 1):
            print(f"{i}) {p}")
        
        # Menu navigation options
        refresh_idx = len(projects) + 1
        print(f"{refresh_idx}) 🔄 Refresh")
        print("0) 🔙 Back")

        choice = input("\nSelect a project to open (or 0): ").strip()
        
        if choice == "0":
            break
            
        if not choice.isdigit():
            continue
            
        idx = int(choice)

        # Refresh Logic
        if idx == refresh_idx:
            continue

        # Project Selection Logic
        proj_idx = idx - 1
        if 0 <= proj_idx < len(projects):
            proj = projects[proj_idx]
            proj_path = os.path.join(base, proj)
            index_path = os.path.join(proj_path, "index.html")

            # Server Validation
            if not is_server_active():
                print("\n⚠️ Local server is currently OFF.")
                if input("Start server? (y/n): ").lower() == "y":
                    _start_server()
                else:
                    continue

            # Project Launch Sequence
            url = f"http://localhost:8080/{base}/{proj}/index.html"
            
            if not os.path.exists(index_path):
                print(f"\n⚠️ 'index.html' not found in this project.")
                run_file = os.path.join(proj_path, "main.py")
                if os.path.exists(run_file):
                    if input("Would you like to run 'main.py' instead? (y/n): ").lower() == "y":
                        print(f"🚀 Executing {proj}/main.py...\n")
                        subprocess.run(["python", run_file])
                        input("\nExecution finished. Press Enter...")
                else:
                    print("🚫 No valid entry point (index.html or main.py) found.")
                    input("Press Enter to return...")
                continue

            # Open Web App in Browser
            print(f"\n🌍 Opening project at: {url}")
            os.system(f'termux-open-url "{url}"')
            input("\nPress Enter to return to manager...")