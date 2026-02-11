import os
import shutil
import datetime
import zipfile

# Plugin configuration
config = {
    "label": "Time Machine (Restore)",
    "icon": "⏪"
}

BACKUP_DIR = "backups"
PLUGINS_DIR = "plugins"
APPS_DIR = "my_apps"

def get_readable_date(timestamp_str):
    """Converts YYYYMMDD_HHMMSS to 'DD/MM/YYYY HH:MM:SS' format."""
    try:
        dt = datetime.datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except:
        return timestamp_str

def list_zip_backups():
    """Returns a list of .zip files in the backup directory, sorted by date."""
    if not os.path.exists(BACKUP_DIR):
        return []
    files = [f for f in os.listdir(BACKUP_DIR) if f.endswith(".zip")]
    # Sort reverse to get the most recent first
    files.sort(reverse=True)
    return files

def find_restore_target(project_name):
    """Checks if the project belongs to plugins or my_apps."""
    # 1. Check in PLUGINS
    plugin_path = os.path.join(PLUGINS_DIR, project_name)
    if os.path.exists(plugin_path):
        return plugin_path, "PLUGIN"
        
    # 2. Check in MY_APPS
    app_path = os.path.join(APPS_DIR, project_name)
    if os.path.exists(app_path):
        return app_path, "APP"
        
    return None, None

def run():
    """Main loop for the Restore system."""
    while True:
        os.system("clear")
        print("=== ⏪ TIME MACHINE (UNIVERSAL RESTORE) ===")
        
        backups = list_zip_backups()
        
        if not backups:
            print("\n🚫 No backup files found.")
            print("0) Back")
            input("\nPress Enter to return...")
            break

        print("\nAvailable Backups (Most recent first):")
        print(f"{'ID':<4} {'PROJECT':<25} {'DATE CREATED':<20}")
        print("-" * 55)

        for i, f in enumerate(backups, 1):
            # Expected format: project_name_YYYYMMDD_HHMMSS.zip
            base = f.replace(".zip", "")
            parts = base.split('_')
            
            if len(parts) >= 3:
                # Reconstruct name in case it contains underscores
                p_name = "_".join(parts[:-2])
                date_str = f"{parts[-2]}_{parts[-1]}"
                nice_date = get_readable_date(date_str)
            else:
                p_name = base
                nice_date = "Unknown date"

            display_name = (p_name[:22] + '..') if len(p_name) > 22 else p_name
            print(f"{i:<4} {display_name:<25} {nice_date:<20}")

        print("-" * 55)
        print("0) ❌ Back")
        
        choice = input("\nSelect the backup ID to restore (or 0): ").strip()
        if choice == "0": 
            break
        if not choice.isdigit(): 
            continue
        
        idx = int(choice) - 1
        if 0 <= idx < len(backups):
            backup_file = backups[idx]
            
            # Extract project name from filename
            base = backup_file.replace(".zip", "")
            parts = base.split('_')
            project_name = "_".join(parts[:-2])
            
            # AUTOMATICALLY LOCATE TARGET
            target_path, type_found = find_restore_target(project_name)
            
            # Manual fallback if project directory was deleted
            if not target_path:
                print(f"\n⚠️ Original project '{project_name}' not found.")
                print("Where should it be restored?")
                print(f"1) To {PLUGINS_DIR}/")
                print(f"2) To {APPS_DIR}/")
                print("0) Cancel")
                
                sub = input("Select choice: ")
                if sub == "1": 
                    target_path = os.path.join(PLUGINS_DIR, project_name)
                elif sub == "2": 
                    target_path = os.path.join(APPS_DIR, project_name)
                else: 
                    continue
            
            print(f"\n🚨 RESTORE REPORT 🚨")
            print(f"📦 Backup: {backup_file}")
            print(f"📂 Destination: {target_path}")
            if type_found:
                print(f"ℹ️  Detected as: {type_found}")
            
            confirm = input("\nAre you sure? This will OVERWRITE current data. (yes/no): ").lower()
            
            if confirm == "yes" or confirm == "y":
                try:
                    # Clean the current directory before restoring
                    if os.path.exists(target_path):
                        shutil.rmtree(target_path)
                    
                    # Unpack the ZIP
                    shutil.unpack_archive(os.path.join(BACKUP_DIR, backup_file), target_path)
                    print(f"\n✅ Restore successful.")
                except Exception as e:
                    print(f"\n❌ Restore Error: {e}")
            else:
                print("\nOperation cancelled.")
            
            input("\nPress Enter to continue...")