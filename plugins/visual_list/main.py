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
config = {"label": "Visual List", "icon": "📱"}

def _find_base_folder():
    """Locates the directory where applications are stored."""
    candidates = ["my_apps", "my_app"]
    for c in candidates:
        if os.path.isdir(c):
            return c
    os.makedirs("my_apps", exist_ok=True)
    return "my_apps"

def _list_projects(base_folder):
    """
    Returns only folders that appear to be projects/apps:
    - Excludes hidden folders and the launcher's own folder (.visual_list).
    - Includes only folders containing index.html or main.py.
    """
    try:
        entries = []
        for d in sorted(os.listdir(base_folder)):
            if d.startswith('.') or d == ".visual_list":
                continue
            path = os.path.join(base_folder, d)
            if not os.path.isdir(path):
                continue
            # Project valid if it has index.html (web app) or main.py (script)
            if os.path.exists(os.path.join(path, "index.html")) or os.path.exists(os.path.join(path, "main.py")):
                entries.append(d)
        return entries
    except Exception:
        return []

def _ensure_server():
    """Checks if the local server is running; starts it if the user agrees."""
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
    """Generates the HTML content for the mobile-style visual launcher."""
    apps = []
    for p in projects:
        index_path = os.path.join(base, p, "index.html")
        has_index = os.path.exists(index_path)
        qbase = quote(base)
        qp = quote(p)
        url = f"http://localhost:8080/{qbase}/{qp}/index.html" if has_index else ""
        apps.append({"name": p, "url": url, "has_index": has_index})

    # UI Design Template
    html_content = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"/>
<title>Visual Launcher</title>
<style>
  :root {{
    --bg:#0f1724;
    --phone-bg:#0b1220;
    --muted:#9aa4b2;
    --panel:#0f1724;
    --accent1:#2b6ef6;
    --accent2:#8b5cf6;
    --text:#dfe7f3;
  }}
  html,body{{height:100%;margin:0;background:var(--bg);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial;}}
  .wrap{{min-height:100vh;display:flex;align-items:flex-start;justify-content:center;padding:28px 12px;box-sizing:border-box;}}
  .phone {{
    width: min(420px, 92vw);
    height: min(820px, 92vh);
    background:var(--phone-bg);
    border-radius:28px;
    box-shadow: 0 20px 50px rgba(0,0,0,0.6);
    padding:14px;
    color:#fff;
    position:relative;
    overflow:hidden;
    display:flex;
    flex-direction:column;
  }}
  .notch {{ width:120px;height:26px;background:#09111a;border-radius:14px;margin:6px auto 8px auto; }}
  .screen {{ background: rgba(255,255,255,0.02); border-radius:16px; flex:1; padding:12px; display:flex; flex-direction:column; min-height:0; }}
  .header{{display:flex;justify-content:space-between;align-items:center;padding:6px 8px;color:var(--muted);font-size:14px;}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(76px,1fr));gap:10px;margin-top:10px;flex:1;overflow:auto;padding-bottom:6px;}}
  .app{{background:rgba(255,255,255,0.03);border-radius:12px;padding:10px;display:flex;flex-direction:column;align-items:center;justify-content:center;cursor:pointer;transition:transform .12s,box-shadow .12s;min-height:86px;}}
  .app:active{{transform:scale(.995);}}
  .app:hover{{transform:translateY(-6px);box-shadow:0 8px 20px rgba(0,0,0,0.35);}}
  .icon{{width:56px;height:56px;border-radius:12px;background:linear-gradient(135deg,var(--accent1),var(--accent2));display:flex;align-items:center;justify-content:center;font-weight:700;font-size:22px;color:white;margin-bottom:8px;}}
  .icon.alt{{background:#4b5563}}
  .name{{font-size:12px;text-align:center;color:var(--text);word-break:break-word;}}
  .footer{{text-align:center;font-size:12px;color:#7f8b9a;padding:8px;margin-top:6px;}}
</style>
</head>
<body>
  <div class="wrap">
    <div class="phone">
      <div class="notch"></div>
      <div class="screen">
        <div class="header"><div>Visual Launcher</div><div>{len(apps)} apps</div></div>
        <div class="grid" id="appsGrid">
"""
    for a in apps:
        name = a.get("name") or ""
        letter = html.escape(name[0].upper()) if name else "?"
        js_url = json.dumps(a["url"])
        js_name = json.dumps(name)
        safe_name = html.escape(name)

        if a["has_index"]:
            html_content += f'<div class="app" onclick=\'openApp({js_url})\'><div class="icon">{letter}</div><div class="name">{safe_name}</div></div>'
        else:
            html_content += f'<div class="app" onclick=\'notifyNoWeb({js_name})\'><div class="icon alt">{letter}</div><div class="name">{safe_name}</div></div>'

    html_content += """
        </div>
        <div class="footer">Tap to open. Non-web apps use APPs Manager.</div>
      </div>
    </div>
  </div>
<script>
function openApp(url){ if(!url){ alert("No URL available."); return; } window.location.href = url; }
function notifyNoWeb(name){ alert("The app '" + name + "' does not contain an index.html file."); }
</script>
</body></html>"""
    return html_content

def _open_url(url):
    """Try termux-open-url (Android), otherwise fallback to standard webbrowser."""
    if not url:
        return False
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
    """Main execution of the Visual List plugin."""
    base = _find_base_folder()
    projects = _list_projects(base)
    
    if not projects:
        print("\n🚫 No applications found in directory:", base)
        input("\nPress Enter to return...")
        return
        
    if not _ensure_server():
        return

    # Save launcher in a hidden folder so it doesn't appear in the app list
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
        print(f"\n🌐 Opening Launcher: {url}")
        if not _open_url(url):
            print("⚠️ Could not open URL automatically. Please open manually at:", url)
    else:
        print("\n⚠️ Local server is not active after generating launcher.")
    
    input("\nPress Enter to return...")