import os
import shutil

# Plugin Configuration
config = {
    "label": "Delete Apps", 
    "icon": "🗑️"
}

def _find_base_folder():
    """Locates the directory where applications are stored."""
    candidates = ["my_apps", "my_app"]
    for c in candidates:
        if os.path.isdir(c):
            return c
    # Fallback to creating 'my_apps' if neither exists
    os.makedirs("my_apps", exist_ok=True)
    return "my_apps"

def _list_projects(base_folder):
    """Returns a sorted list of project directories."""
    try:
        entries = sorted([d for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d))])
        return entries
    except Exception:
        return []

def run():
    """Main execution loop for the Delete Apps plugin."""
    base = _find_base_folder()
    
    while True:
        os.system('clear')
        print("=== 🗑️ DELETE APPS MANAGER ===")
        print(f"Base Directory: {base}\n")
        
        projects = _list_projects(base)

        if not projects:
            print("🚫 No projects found in the directory.")
            print("0) Back")
            choice = input("\nSelection: ").strip()
            if choice == "0": 
                break
            continue

        # List available projects
        for i, p in enumerate(projects, 1):
            print(f"{i}) {p}")
        
        refresh_idx = len(projects) + 1
        print(f"{refresh_idx}) 🔄 Refresh List")
        print("0) ❌ Back")

        choice = input("\nEnter the project number to delete (or 0 to exit): ").strip()
        
        if choice == "0":
            break
            
        if not choice.isdigit():
            continue

        idx = int(choice)

        # Refresh Logic
        if idx == refresh_idx:
            continue

        # Deletion Logic
        real_idx = idx - 1
        if 0 <= real_idx < len(projects):
            proj = projects[real_idx]
            proj_path = os.path.join(base, proj)
            
            # Path Traversal Security Check
            try:
                base_abs = os.path.abspath(base)
                target_abs = os.path.abspath(proj_path)
                if not target_abs.startswith(base_abs):
                    print("\n⚠️ Invalid path detected. Operation cancelled for security.")
                    input("\nPress Enter to continue...")
                    continue
            except:
                pass

            confirm = input(f"\nAre you sure you want to delete '{proj}'? (y/n): ").strip().lower()
            
            if confirm == 'y':
                try:
                    shutil.rmtree(proj_path)
                    print(f"\n✅ Project '{proj}' has been successfully deleted.")
                except Exception as e:
                    print(f"\n❌ Error during deletion: {e}")
            else:
                print("\n🔙 Deletion cancelled.")
            
            input("\nPress Enter to continue...")