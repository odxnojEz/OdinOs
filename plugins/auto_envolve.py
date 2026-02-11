import os
import shutil
import datetime
import json
from core.utils import ask_ai

# Plugin configuration
config = {
    "label": "Auto-Evolve (create functionality)",
    "icon": "🧬"
}

# --- BACKUP FUNCTION (ZIP MODE) ---
def perform_backup(plugin_folder_path):
    """
    Compresses the entire plugin folder into a ZIP within /backups.
    Example: backups/calculator_20260211_1430.zip
    """
    # 1. Check user preference in config.json
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r") as f:
                settings = json.load(f)
                if not settings.get("preferences", {}).get("backup_before_evolve", True):
                    return 
        except: 
            pass

    # 2. Prepare backup directory
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # 3. Define ZIP name: plugin_name + timestamp
    plugin_name = os.path.basename(plugin_folder_path)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Base filename (shutil.make_archive adds .zip automatically)
    zip_base_name = os.path.join(backup_dir, f"{plugin_name}_{timestamp}")

    # 4. Create ZIP archive
    try:
        shutil.make_archive(zip_base_name, 'zip', plugin_folder_path)
        print(f"🛡️  Full backup (ZIP) created: {zip_base_name}.zip")
    except Exception as e:
        print(f"⚠️  Failed to create backup ZIP: {e}")

def update_context_file():
    """Gathers all project source code into a single text file for AI context."""
    output_file = "totalcode.txt"
    print(f"🔍 Scanning project context...")
    
    extensions = ('.py', '.json')
    with open(output_file, "w", encoding="utf-8") as out:
        for root, dirs, files in os.walk("."):
            # Ignore hidden folders, cache, and system directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ["__pycache__", "backups", "temp_exports", "temp_imports"]]
            
            for file in files:
                if file.endswith(extensions):
                    path = os.path.join(root, file)
                    # Avoid reading the context file itself
                    if path == f"./{output_file}" or path == output_file: 
                        continue
                    
                    out.write(f"{'-'*48}\nFILE: {path}\n{'-'*48}\n")
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            out.write(f.read())
                    except: 
                        continue
                    out.write("\n\n")
    return output_file

def clean_ai_code(text):
    """Extracts raw code from AI response, removing markdown and conversational text."""
    if "```python" in text:
        text = text.split("```python")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    
    lines = text.split('\n')
    clean_lines = []
    # Markers indicating the start of conversational/non-code text
    stop_markers = ("Notes:", "Summary:", "Note:", "Hope this", "Explanation:", "Done.", "Here is")
    
    for line in lines:
        stripped = line.strip()
        if any(stripped.startswith(marker) for marker in stop_markers): 
            break
        clean_lines.append(line)
        
    return '\n'.join(clean_lines).strip()

def sanitize_folder_name(name):
    """Cleans a string to create a valid folder name."""
    clean = "".join(e for e in name if e.isalnum() or e == " ").lower().replace(" ", "_")
    return clean if clean else "new_plugin"

def run():
    """Main plugin execution loop."""
    while True:
        os.system('clear')
        print("=== 🧬 SYSTEM EVOLUTION (AUTO-EVOLVE) ===")
        print("1) Create New Plugin (As Folder)")
        print("2) Fix / Improve Existing Plugin")
        print("0) 🔙 Back")
        
        mode = input("\nSelect mode: ").strip()
        if mode == "0": 
            break

        # Refresh context file before AI request
        context_path = update_context_file()
        try:
            with open(context_path, "r", encoding="utf-8") as f: 
                full_context = f.read()
        except: 
            full_context = ""

        base_sys_prompt = f"""YOU ARE A TERMINAL CODE GENERATOR.
        CONTEXT: {full_context}
        STRICT RULES:
        1. Output MUST BE 100% RAW PYTHON CODE ONLY.
        2. NO introductory text, NO markdown blocks.
        3. CODE MUST START DIRECTLY WITH 'import', 'from' OR 'config ='.
        4. USE ENGLISH FOR ALL COMMENTS AND VARIABLE NAMES.
        """

        if mode == "1":
            plugin_name = input("\n📝 New Plugin Name (or 0 to cancel): ")
            if plugin_name == "0": 
                continue
            plugin_task = input("⚙️ What should it do?: ")
            
            folder_name = sanitize_folder_name(plugin_name)
            plugin_dir = os.path.join("plugins", folder_name)
            
            prompt = f"Create a new plugin named '{plugin_name}' that does: {plugin_task}."
            print(f"\n🧠 Programming {folder_name}/main.py...")
            
            code = ask_ai(prompt, base_sys_prompt)
            if code:
                os.makedirs(plugin_dir, exist_ok=True)
                save_path = os.path.join(plugin_dir, "main.py")
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(clean_ai_code(code))
                print(f"\n✅ Plugin installed at: {save_path}")
                input("\nPress Enter...")
        
        elif mode == "2":
            if not os.path.exists("plugins"): 
                os.makedirs("plugins")
            items = sorted([i for i in os.listdir("plugins") if not i.startswith(".") and i != "__pycache__"])
            
            print("\n--- SELECT PLUGIN TO IMPROVE ---")
            for i, item in enumerate(items, 1): 
                print(f"{i}) {item}")
            print("0) Cancel")
            
            choice_in = input("\nChoice: ").strip()
            if choice_in == "0" or not choice_in.isdigit(): 
                continue
            
            idx = int(choice_in) - 1
            if 0 <= idx < len(items):
                name = items[idx]
                p_path = os.path.join("plugins", name)
                
                # Verify if it's a folder-based plugin
                if os.path.isdir(p_path):
                    target_file = os.path.join(p_path, "main.py")
                    # Perform safety backup before modification
                    perform_backup(p_path)
                else:
                    # Legacy support for single-file plugins
                    target_file = p_path
                    print("⚠️ Single-file plugin detected. Consider migrating to folders.")
                
                if os.path.exists(target_file):
                    with open(target_file, "r", encoding="utf-8") as f: 
                        old_code = f.read()
                    
                    issue = input("\n🛠️ Improvement task: ")
                    if issue == "0": 
                        continue
                    
                    print(f"\n🧠 Thinking and improving {name}...")
                    new_code = ask_ai(f"Improve this code:\n{old_code}\nTask: {issue}", base_sys_prompt)
                    
                    if new_code:
                        with open(target_file, "w", encoding="utf-8") as f:
                            f.write(clean_ai_code(new_code))
                        print(f"\n✅ Updated: {target_file}")
                        input("\nPress Enter...")