import os
import json

# Plugin Configuration
config = {"label": "Global Settings Hub", "icon": "⚙️"}
CONFIG_FILE = "config.json"

def load_settings():
    """Loads settings from config.json or returns defaults if file doesn't exist."""
    if not os.path.exists(CONFIG_FILE):
        return {
            "active_provider": "openai",
            "api_keys": {"openai": "", "anthropic": ""},
            "models": {"openai": "gpt-4o-mini", "anthropic": "claude-3-5-sonnet"},
            "preferences": {"backup_before_evolve": True}
        }
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f: 
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Error reading config: {e}")
        return {}

def save_settings(data):
    """Saves the settings dictionary to config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"❌ Error saving settings: {e}")

def run():
    """Main loop for the Settings Hub."""
    while True:
        os.system("clear")
        settings = load_settings()
        if not settings:
            print("❌ Critical Error: Could not load configuration.")
            input("Press Enter to return...")
            break

        active_prov = settings.get('active_provider', 'openai')
        provider_list = list(settings.get('api_keys', {}).keys())
        
        print(f"=== ⚙️ GLOBAL SETTINGS HUB ===")
        print(f"ACTIVE: {active_prov.upper()} | MODEL: {settings['models'].get(active_prov)}")
        print("-" * 35)
        print("1) 🚀 Guided Configuration (Provider -> Model -> Key)")
        print("2) 🧠 Change Active Provider")
        print("3) 🛠️ System Preferences")
        print("\n0) 🔙 Back")
        
        option = input("\nSelect an option: ").strip()
        
        if option == "0":
            break

        if option == "1":
            print("\n--- STEP 1: Select Provider ---")
            for i, name in enumerate(provider_list, 1):
                print(f"{i}) {name.capitalize()}")
            print("0) Cancel")
            
            p_idx = input("\nSelect provider number: ")
            if p_idx == "0": continue

            if p_idx.isdigit() and 1 <= int(p_idx) <= len(provider_list):
                provider = provider_list[int(p_idx)-1]
                
                print(f"\n--- STEP 2: Set Model for {provider.upper()} ---")
                print("Enter manually (e.g., gpt-4o, claude-3-5-sonnet, etc.)")
                current_model = settings['models'].get(provider, "Not set")
                new_model = input(f"Model (current: {current_model}): ").strip()
                if new_model: 
                    settings['models'][provider] = new_model
                
                print(f"\n--- STEP 3: API Key ---")
                new_key = input(f"Enter API Key for {provider}: ").strip()
                if new_key: 
                    settings['api_keys'][provider] = new_key
                
                settings['active_provider'] = provider
                save_settings(settings)
                print(f"\n✅ {provider.upper()} configured and activated.")
            else:
                print("❌ Invalid selection.")
            input("\nPress Enter to continue...")

        elif option == "2":
            print("\n--- 🧠 SELECT ACTIVE AI ---")
            for i, name in enumerate(provider_list, 1):
                print(f"{i}) {name.capitalize()}")
            print("0) Cancel")
            
            p_idx = input("\nSelect the provider to activate: ")
            if p_idx == "0": continue

            if p_idx.isdigit() and 1 <= int(p_idx) <= len(provider_list):
                settings['active_provider'] = provider_list[int(p_idx)-1]
                save_settings(settings)
                print(f"✅ Active provider changed to: {settings['active_provider'].upper()}")
            else:
                print("❌ Invalid selection.")
            input("\nPress Enter to continue...")

        elif option == "3":
            print("\n--- 🛠️ SYSTEM PREFERENCES ---")
            backup_pref = settings.get('preferences', {}).get('backup_before_evolve', True)
            print(f"1) Backup before Evolution: {'YES' if backup_pref else 'NO'}")
            print("0) Back")
            
            pref_opt = input("\nSelect preference number to toggle: ")
            if pref_opt == "1":
                if 'preferences' not in settings: settings['preferences'] = {}
                settings['preferences']['backup_before_evolve'] = not backup_pref
                save_settings(settings)
                print("✅ Preference updated.")
            elif pref_opt == "0":
                continue
            input("\nPress Enter to continue...")