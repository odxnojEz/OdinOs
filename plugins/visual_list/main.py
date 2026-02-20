import os
import subprocess
import time
import json
import sys
import html
import webbrowser
import shutil
from urllib.parse import quote
from core.utils import is_server_active

# Plugin Configuration
config = {"label": "Visual Launcher", "icon": "📱"}

def _find_base_folder():
    candidates = ["my_apps", "my_app"]
    for c in candidates:
        if os.path.isdir(c):
            return c
    os.makedirs("my_apps", exist_ok=True)
    return "my_apps"

def _list_projects(base_folder):
    try:
        entries = []
        for d in sorted(os.listdir(base_folder)):
            if d.startswith('.') or d == ".visual_list":
                continue
            path = os.path.join(base_folder, d)
            if not os.path.isdir(path):
                continue
            if os.path.exists(os.path.join(path, "index.html")) or os.path.exists(os.path.join(path, "main.py")):
                entries.append(d)
        return entries
    except Exception:
        return []

def _ensure_server():
    if is_server_active():
        return True
    start = input("\n⚠️ Local server is OFF. Start it to preview apps in the browser? (y/n): ").strip().lower()
    if start != "y":
        return False
    print("📡 Starting background server (port 8080)...")
    try:
        subprocess.Popen([sys.executable, "-m", "http.server", "8080"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
    except Exception as e:
        print(f"⚠️ Failed to start server: {e}")
        return False
    return is_server_active()

def _generate_launcher_html(base, projects):
    apps = []
    for p in projects:
        index_path = os.path.join(base, p, "index.html")
        has_index = os.path.exists(index_path)
        qbase = quote(base)
        qp = quote(p)
        url = f"http://localhost:8080/{qbase}/{qp}/index.html" if has_index else ""
        apps.append({"name": p, "url": url, "has_index": has_index})

    # Modern OS Launcher Template
    html_content = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0"/>
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#0a0a0c">
<title>Acornix OS</title>
<style>
  :root {{
    --bg: #0a0a0c;
    --card-bg: rgba(255, 255, 255, 0.05);
    --text-main: #ffffff;
    --text-muted: #8e8e93;
  }}
  
  * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
  
  body {{
    margin: 0; padding: 0; background: var(--bg);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: var(--text-main); min-height: 100vh;
  }}

  /* Glassmorphism Header */
  .header {{
    position: sticky; top: 0; z-index: 100;
    padding: 20px 20px 15px 20px;
    background: rgba(10, 10, 12, 0.75);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border-bottom: 1px solid rgba(255,255,255,0.05);
  }}

  .title-row {{ display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 15px; }}
  .title-row h1 {{ margin: 0; font-size: 28px; font-weight: 700; letter-spacing: -0.5px; }}
  .app-count {{ color: var(--text-muted); font-size: 14px; font-weight: 500; margin-bottom: 4px; }}

  /* Search Bar */
  .search-bar {{
    width: 100%; padding: 12px 16px;
    border-radius: 12px; border: none; outline: none;
    background: var(--card-bg); color: white;
    font-size: 16px; transition: background 0.2s;
  }}
  .search-bar:focus {{ background: rgba(255, 255, 255, 0.1); }}
  .search-bar::placeholder {{ color: var(--text-muted); }}

  /* App Grid */
  .grid-container {{ padding: 20px; }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 20px 15px;
  }}

  .app-card {{
    display: flex; flex-direction: column; align-items: center;
    cursor: pointer; text-decoration: none;
    transition: transform 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  }}
  .app-card:active {{ transform: scale(0.92); }}

  .app-icon {{
    width: 70px; height: 70px;
    border-radius: 18px;
    display: flex; align-items: center; justify-content: center;
    font-size: 28px; font-weight: bold; color: white;
    box-shadow: 0 8px 16px rgba(0,0,0,0.4), inset 0 1px 1px rgba(255,255,255,0.2);
    margin-bottom: 8px;
  }}

  .app-icon.python {{ background: #2c2c2e; color: #ffcc00; box-shadow: none; border: 1px solid rgba(255,255,255,0.1); }}

  .app-name {{
    font-size: 12px; font-weight: 500; text-align: center;
    width: 100%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }}

  .empty-state {{ text-align: center; color: var(--text-muted); margin-top: 50px; font-size: 16px; display: none; }}
</style>
</head>
<body>

  <div class="header">
    <div class="title-row">
      <h1>App Library</h1>
      <span class="app-count">{len(apps)} Apps</span>
    </div>
    <input type="text" id="searchInput" class="search-bar" placeholder="Search applications..." autocomplete="off">
  </div>

  <div class="grid-container">
    <div class="grid" id="appsGrid">
"""
    # Generate HTML for each app
    for a in apps:
        name = a.get("name") or "App"
        letter = html.escape(name[0].upper())
        js_url = json.dumps(a["url"])
        js_name = json.dumps(name)
        safe_name = html.escape(name)
        
        # Add data-name for the live search filtering
        if a["has_index"]:
            html_content += f"""
      <div class="app-card" data-name="{safe_name.lower()}" onclick='openApp({js_url})'>
        <div class="app-icon dynamic-bg" data-seed="{safe_name}">{letter}</div>
        <div class="app-name">{safe_name}</div>
      </div>"""
        else:
            # Python scripts get a dark gray icon to differentiate them from WebApps
            html_content += f"""
      <div class="app-card" data-name="{safe_name.lower()}" onclick='notifyNoWeb({js_name})'>
        <div class="app-icon python">py</div>
        <div class="app-name" style="color: #8e8e93;">{safe_name}</div>
      </div>"""

    html_content += """
    </div>
    <div class="empty-state" id="emptyState">No apps found matching your search.</div>
  </div>

<script>
// Open App Logic
function openApp(url){ if(!url) return; window.location.href = url; }
function notifyNoWeb(name){ alert("'" + name + "' is a Python script.\\nRun it from the terminal using Acornix."); }

// Live Search Filter
const searchInput = document.getElementById('searchInput');
const apps = document.querySelectorAll('.app-card');
const emptyState = document.getElementById('emptyState');

searchInput.addEventListener('input', (e) => {
    const term = e.target.value.toLowerCase();
    let visibleCount = 0;
    
    apps.forEach(app => {
        const name = app.getAttribute('data-name');
        if (name.includes(term)) {
            app.style.display = 'flex';
            visibleCount++;
        } else {
            app.style.display = 'none';
        }
    });
    
    emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
});

// Dynamic Gradient Generator based on string hash
const gradients = [
    'linear-gradient(135deg, #FF0080 0%, #FF8C00 100%)', // Pink-Orange
    'linear-gradient(135deg, #00C9FF 0%, #92FE9D 100%)', // Cyan-Green
    'linear-gradient(135deg, #f12711 0%, #f5af19 100%)', // Fire
    'linear-gradient(135deg, #654ea3 0%, #eaafc8 100%)', // Purple
    'linear-gradient(135deg, #1CB5E0 0%, #000851 100%)', // Deep Blue
    'linear-gradient(135deg, #FC466B 0%, #3F5EFB 100%)', // Berry
    'linear-gradient(135deg, #00b09b 0%, #96c93d 100%)'  // Lime
];

function stringToHash(string) {
    let hash = 0;
    for (let i = 0; i < string.length; i++) {
        hash = string.charCodeAt(i) + ((hash << 5) - hash);
    }
    return Math.abs(hash);
}

document.querySelectorAll('.dynamic-bg').forEach(icon => {
    const seed = icon.getAttribute('data-seed');
    const hash = stringToHash(seed);
    const colorIndex = hash % gradients.length;
    icon.style.background = gradients[colorIndex];
});
</script>
</body>
</html>"""
    return html_content

def _open_url(url):
    if not url: return False
    termux_cmd = shutil.which("termux-open-url")
    try:
        if termux_cmd:
            os.system(f'{termux_cmd} "{url}"')
            return True
        else:
            webbrowser.open(url)
            return True
    except Exception:
        webbrowser.open(url)
        return True

def run():
    os.system("clear")
    print("==========================================")
    print(" 📱 ACORNIX VISUAL LAUNCHER ")
    print("==========================================\n")
    
    base = _find_base_folder()
    projects = _list_projects(base)
    
    if not projects:
        print("🚫 No applications found in directory:", base)
        input("\nPress Enter to return...")
        return
        
    if not _ensure_server():
        return

    launcher_dir = os.path.join(base, ".visual_list")
    os.makedirs(launcher_dir, exist_ok=True)
    launcher_path = os.path.join(launcher_dir, "index.html")

    try:
        with open(launcher_path, "w", encoding="utf-8") as f:
            f.write(_generate_launcher_html(base, projects))
    except Exception as e:
        print(f"⚠️ Could not write launcher file: {e}")
        input("\nPress Enter to return...")
        return

    if is_server_active():
        qbase = quote(base)
        url = f"http://localhost:8080/{qbase}/.visual_list/index.html"
        print(f"🌐 Opening Launcher: {url}")
        
        # PWA Tip for the user
        print("\n💡 TIP: Add this page to your Home Screen to use it like a native OS!")
        
        if not _open_url(url):
            print("⚠️ Could not open URL automatically. Please open manually at:", url)
    else:
        print("\n⚠️ Local server is not active after generating launcher.")
    
    input("\n👉 Press [ENTER] to return to Acornix...")

if __name__ == "__main__":
    run()