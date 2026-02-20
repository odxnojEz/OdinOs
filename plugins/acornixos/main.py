import os
import http.server
import socketserver
import threading
import mimetypes
import time
import html
import json
import shutil
import sys
import builtins
import importlib.util
import subprocess
from urllib.parse import quote, unquote, urlparse

# Plugin Configuration
config = {"label": "acornixOS", "icon": "🍏"}
PORT = 8085

# --- WEB TERMINAL ENGINE ---
class WebTerminal:
    def __init__(self):
        self.output_buffer = ""
        self.input_queue = []
        self.is_waiting_input = False
        self.is_running = False
        self.lock = threading.Lock()

    def write(self, text):
        with self.lock:
            self.output_buffer += str(text)

    def flush(self):
        pass

    def readline(self):
        self.is_waiting_input = True
        while True:
            with self.lock:
                if not self.is_running:
                    raise KeyboardInterrupt("Terminal closed by OS")
                if self.input_queue:
                    val = self.input_queue.pop(0)
                    self.is_waiting_input = False
                    return val + "\n"
            time.sleep(0.1)

web_term = WebTerminal()

def run_system_terminal():
    print("=======================================")
    print(" 💻 acornixOS NATIVE TERMINAL ")
    print("=======================================")
    print("Type 'exit' to close this window.\n")
    
    while True:
        try:
            cwd = os.getcwd()
            cmd = input(f"acornix@{cwd}$ ")
            cmd = cmd.strip()
            
            if not cmd: continue
            if cmd.lower() in ("exit", "quit"): break
                
            if cmd.startswith("cd "):
                target_dir = cmd[3:].strip()
                try: os.chdir(target_dir)
                except Exception as e: print(f"cd: {e}")
            else:
                try:
                    output = subprocess.getoutput(cmd)
                    if output: print(output)
                except Exception as e: print(f"Error: {e}")
                    
        except KeyboardInterrupt: break
        except Exception as e:
            print(f"Fatal Terminal Error: {e}")
            break

def execute_plugin(plugin_entry_point, module_name):
    global web_term
    web_term.output_buffer = ""
    web_term.input_queue = []
    
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    original_stdin = sys.stdin
    original_os_system = os.system

    def fake_system(cmd):
        if cmd == 'clear':
            with web_term.lock: web_term.output_buffer += "--- [CLEAR SCREEN] ---\n"
        else: original_os_system(cmd)

    sys.stdout = web_term
    sys.stderr = web_term
    sys.stdin = web_term
    os.system = fake_system
    
    try:
        if module_name == "__terminal__":
            run_system_terminal()
        else:
            spec = importlib.util.spec_from_file_location(module_name, plugin_entry_point)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            if module_name != "__main__" and hasattr(module, 'run'):
                module.run()
    except KeyboardInterrupt: web_term.write("\n[Terminal Process Closed]")
    except Exception as e: web_term.write(f"\n[System Error]: {e}")
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        sys.stdin = original_stdin
        os.system = original_os_system
        web_term.is_running = False
        with web_term.lock: web_term.output_buffer += "\n[Process Terminated]\n"

# --- SCANNING ENGINE ---
def _find_base_folder():
    candidates = ["my_apps", "my_app"]
    for c in candidates:
        if os.path.isdir(c): return c
    os.makedirs("my_apps", exist_ok=True)
    return "my_apps"

def _list_apps(base_folder):
    entries = []
    if os.path.exists(base_folder):
        for d in sorted(os.listdir(base_folder)):
            if d.startswith('.') or d in (".visual_list", "acornixOS_desktop"): continue
            path = os.path.join(base_folder, d)
            if not os.path.isdir(path): continue
            
            has_index = os.path.exists(os.path.join(path, "index.html"))
            has_main = os.path.exists(os.path.join(path, "main.py"))
            
            if has_index:
                entries.append({
                    "name": d, "type": "app",
                    "url": f"http://localhost:{PORT}/{quote(base_folder)}/{quote(d)}/index.html",
                    "entry_point": "", "module_name": ""
                })
            elif has_main:
                entries.append({
                    "name": d, "type": "python_app", "url": "",
                    "entry_point": os.path.join(path, "main.py"), "module_name": "__main__"
                })
    return entries

def _list_plugins():
    plugin_dir = "plugins"
    entries = []
    if not os.path.exists(plugin_dir): return entries
        
    for item in os.listdir(plugin_dir):
        if item in ("__init__.py", "__pycache__") or item.startswith("."): continue
        item_path = os.path.join(plugin_dir, item)
        module_name, entry_point = "", ""
        
        if item.endswith(".py"): module_name, entry_point = item[:-3], item_path
        elif os.path.isdir(item_path):
            main_file = os.path.join(item_path, "main.py")
            if os.path.exists(main_file): module_name, entry_point = item, main_file
        
        if module_name == "acornixOS": continue
        if entry_point:
            try:
                spec = importlib.util.spec_from_file_location(module_name, entry_point)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, 'config') and hasattr(module, 'run'):
                    entries.append({
                        "name": module.config.get("label", module_name),
                        "type": "plugin", "icon": module.config.get("icon", "🧩"),
                        "entry_point": entry_point, "module_name": module_name, "url": ""
                    })
            except: pass
    return sorted(entries, key=lambda x: x["name"].lower())

# --- OS HTML GENERATOR ---
def _generate_desktop_html():
    base = _find_base_folder()
    apps = _list_apps(base)
    plugins = _list_plugins()
    sys_apps = [{"name": "Terminal", "type": "system_app", "icon": "💻", "url": "", "entry_point": "internal", "module_name": "__terminal__"}]
    all_items = sys_apps + apps + plugins
    items_json = json.dumps(all_items)
    
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0"/>
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#000000">
<title>acornixOS</title>
<style>
  :root {{ --dock-bg: rgba(255, 255, 255, 0.2); --topbar-bg: rgba(0, 0, 0, 0.4); --text-color: #ffffff; }}
  * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; user-select: none; }}
  body {{
    margin: 0; padding: 0; height: 100vh; width: 100vw;
    background: url('https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop') center/cover no-repeat;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: var(--text-color); overflow: hidden; display: flex; flex-direction: column;
  }}
  
  .menubar {{
    height: 28px; width: 100%; background: var(--topbar-bg);
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    display: flex; justify-content: space-between; align-items: center;
    padding: 0 15px; font-size: 13px; font-weight: 500; z-index: 10000;
  }}
  .menubar-left {{ display: flex; align-items: center; gap: 15px; }}
  .menubar-right {{ display: flex; align-items: center; gap: 10px; }}
  .btn-refresh {{ cursor: pointer; color: #a1d4ff; }}
  .btn-refresh:active {{ opacity: 0.5; }}
  
  .desktop {{ flex: 1; position: relative; overflow: hidden; }}
  
  .dock-wrapper {{
    position: absolute; bottom: 10px; left: 0; width: 100%;
    display: flex; justify-content: center; z-index: 10; pointer-events: none;
  }}
  .dock-container {{
    background: var(--dock-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.15); border-radius: 24px; padding: 10px;
    display: flex; gap: 15px; align-items: center; box-shadow: 0 15px 35px rgba(0,0,0,0.4);
    overflow-x: auto; max-width: 95vw; pointer-events: auto;
  }}
  .dock-container::-webkit-scrollbar {{ display: none; }}
  .dock-icon {{
    width: 50px; height: 50px; flex-shrink: 0; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; cursor: pointer; transition: transform 0.2s; box-shadow: 0 4px 10px rgba(0,0,0,0.2);
  }}
  .dock-icon:active {{ transform: scale(0.9); }}
  .dock-icon.launchpad {{ background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%); }}

  .launchpad-overlay {{
    position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6);
    backdrop-filter: blur(30px); -webkit-backdrop-filter: blur(30px); z-index: 9500;
    display: flex; flex-direction: column; opacity: 0; pointer-events: none; transition: opacity 0.3s ease;
  }}
  .launchpad-overlay.active {{ opacity: 1; pointer-events: auto; }}
  .launchpad-search {{
    margin: 40px auto 20px auto; width: 80%; max-width: 400px; background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; padding: 10px 15px; color: white;
    text-align: center; font-size: 16px; outline: none;
  }}
  .launchpad-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); gap: 30px 15px; padding: 20px 30px; overflow-y: auto; align-content: flex-start; }}
  .lp-app {{ display: flex; flex-direction: column; align-items: center; gap: 8px; cursor: pointer; }}
  .lp-icon {{ width: 60px; height: 60px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 28px; color: white; box-shadow: 0 5px 15px rgba(0,0,0,0.2); transition: filter 0.2s; }}
  .lp-app:active .lp-icon {{ filter: brightness(0.8) scale(0.95); }}
  .lp-name {{ font-size: 12px; text-align: center; width: 100%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  
  #window-container {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 1000; }}
  
  .os-window {{
    position: absolute; background: #fff; border-radius: 12px; overflow: hidden;
    box-shadow: 0 20px 50px rgba(0,0,0,0.6); display: flex; flex-direction: column;
    pointer-events: auto; transform: scale(0.9); opacity: 0;
    transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275), opacity 0.2s;
  }}
  .os-window.active {{ transform: scale(1); opacity: 1; }}
  .os-window.maximized {{ 
      top: 28px !important; left: 0 !important; 
      width: 100% !important; height: calc(100% - 28px) !important; 
      border-radius: 0; transition: all 0.3s ease; 
  }}
  
  .window-header {{
    height: 40px; background: #e0e0e0; color: #333; display: flex; align-items: center;
    padding: 0 15px; font-weight: 600; font-size: 14px; justify-content: space-between;
    cursor: grab; flex-shrink: 0; touch-action: none;
  }}
  .window-header:active {{ cursor: grabbing; }}
  .window-controls {{ display: flex; gap: 8px; }}
  .win-btn {{ width: 12px; height: 12px; border-radius: 50%; background: #ccc; cursor: pointer; display: flex; align-items: center; justify-content: center; }}
  .win-close {{ background: #ff5f56; }}
  .win-max {{ background: #27c93f; }}
  
  .resize-handle {{
      position: absolute; bottom: 0; right: 0; width: 25px; height: 25px;
      cursor: se-resize; z-index: 100; touch-action: none;
  }}
  .resize-handle::after {{
      content: ''; position: absolute; bottom: 6px; right: 6px; width: 10px; height: 10px;
      border-right: 2px solid rgba(100,100,100,0.5); border-bottom: 2px solid rgba(100,100,100,0.5);
      border-bottom-right-radius: 2px;
  }}
  
  .window-content {{ flex: 1; border: none; width: 100%; height: 100%; background: #fff; display: block; }}
  
  .terminal-container {{ display: flex; flex-direction: column; flex: 1; background: #0d0d0d; color: #00ff00; font-family: monospace; font-size: 14px; padding: 10px; overflow: hidden; }}
  .terminal-output {{ flex: 1; overflow-y: auto; white-space: pre-wrap; padding-bottom: 10px; user-select: text; word-break: break-all; }}
  .terminal-input-wrapper {{ display: flex; border-top: 1px solid #333; padding-top: 10px; flex-shrink: 0; }}
  .terminal-input-wrapper.hidden {{ display: none; }}
  .terminal-input {{ flex: 1; background: transparent; border: none; color: #00ff00; font-family: monospace; font-size: 15px; outline: none; }}

  .toast {{ position: absolute; top: 40px; right: -300px; width: 280px; background: rgba(255,255,255,0.9); color: #333; padding: 15px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); z-index: 10000; transition: right 0.4s; backdrop-filter: blur(10px); }}
  .toast.show {{ right: 15px; }}
  .toast-title {{ font-weight: bold; margin-bottom: 5px; font-size: 14px; }}
  .toast-msg {{ font-size: 13px; color: #555; }}
</style>
</head>
<body>

  <div class="menubar">
    <div class="menubar-left"><div>🍏 acornixOS</div></div>
    <div class="menubar-right">
      <div class="btn-refresh" onclick="location.reload()">🔄 Refresh OS</div>
      <div>📶</div>
      <div id="clock">12:00</div>
    </div>
  </div>

  <div class="desktop" id="desktop" onclick="closeLaunchpad()"></div>
  <div id="window-container"></div>
  
  <div class="dock-wrapper">
    <div class="dock-container" id="dock" onclick="event.stopPropagation()"></div>
  </div>

  <div class="launchpad-overlay" id="launchpad" onclick="closeLaunchpad()">
    <input type="text" class="launchpad-search" id="lpSearch" placeholder="Search Apps & Plugins" onclick="event.stopPropagation()">
    <div class="launchpad-grid" id="lpGrid" onclick="event.stopPropagation()"></div>
  </div>

  <div class="toast" id="toast">
    <div class="toast-title" id="toastTitle"></div>
    <div class="toast-msg" id="toastMsg"></div>
  </div>

<script>
  const rawItems = {items_json};
  const defaultDockItems = ["Terminal", "App Creator", "Help"]; 
  let savedDock = JSON.parse(localStorage.getItem('acornixDock')) || defaultDockItems;

  setInterval(() => {{ document.getElementById('clock').innerText = new Date().toLocaleTimeString([], {{hour: '2-digit', minute:'2-digit'}}); }}, 1000);

  const gradients = ['linear-gradient(135deg, #FF0080 0%, #FF8C00 100%)', 'linear-gradient(135deg, #00C9FF 0%, #92FE9D 100%)', 'linear-gradient(135deg, #654ea3 0%, #eaafc8 100%)', 'linear-gradient(135deg, #FC466B 0%, #3F5EFB 100%)', 'linear-gradient(135deg, #f12711 0%, #f5af19 100%)'];
  function getHashColor(str) {{ let hash = 0; for(let i=0; i<str.length; i++) hash = str.charCodeAt(i) + ((hash<<5)-hash); return gradients[Math.abs(hash) % gradients.length]; }}

  function setupLongPress(element, callback) {{
    let timer; let isLongPress = false;
    const start = (e) => {{ isLongPress = false; timer = setTimeout(() => {{ isLongPress = true; if(navigator.vibrate) navigator.vibrate(40); callback(); }}, 500); }};
    const cancel = () => clearTimeout(timer);
    element.addEventListener('touchstart', start, {{passive: true}}); element.addEventListener('touchend', cancel); element.addEventListener('touchmove', cancel);
    element.addEventListener('mousedown', start); element.addEventListener('mouseup', cancel); element.addEventListener('mouseleave', cancel);
    element._wasLongPress = () => {{ const wasLp = isLongPress; isLongPress = false; return wasLp; }};
  }}

  const dock = document.getElementById('dock');
  function renderDock() {{
    dock.innerHTML = '';
    const lpIcon = document.createElement('div'); lpIcon.className = 'dock-icon launchpad'; lpIcon.innerText = '🚀'; lpIcon.onclick = toggleLaunchpad; dock.appendChild(lpIcon);
    savedDock.forEach(name => {{
      const item = rawItems.find(i => i.name === name);
      if (!item) return; 
      const div = document.createElement('div'); div.className = 'dock-icon';
      let bg, letter;
      if (item.type === 'system_app') {{ bg = '#0d0d0d'; letter = item.icon; }}
      else if (item.type === 'plugin') {{ bg = '#1c1c1e'; letter = item.icon || '⚙️'; }}
      else if (item.type === 'python_app') {{ bg = '#2b2b2d'; letter = 'py'; }}
      else {{ bg = getHashColor(item.name); letter = item.name.charAt(0).toUpperCase(); }}
      div.style.background = bg; div.innerHTML = letter;
      if (item.type !== 'app') div.style.border = '1px solid rgba(255,255,255,0.2)';
      div.onclick = () => {{ if(div._wasLongPress && div._wasLongPress()) return; openAppWindow(item.name, item.url, item.type, item.entry_point, item.module_name); }};
      setupLongPress(div, () => {{ savedDock = savedDock.filter(n => n !== name); localStorage.setItem('acornixDock', JSON.stringify(savedDock)); renderDock(); showToast("Dock Updated", `'${{name}}' removed`); }});
      dock.appendChild(div);
    }});
  }}

  const lpGrid = document.getElementById('lpGrid');
  function renderLaunchpad(filter = "") {{
    lpGrid.innerHTML = '';
    rawItems.forEach(item => {{
      if(filter && !item.name.toLowerCase().includes(filter.toLowerCase())) return;
      const div = document.createElement('div'); div.className = 'lp-app';
      let bg, letter;
      if (item.type === 'system_app') {{ bg = '#0d0d0d'; letter = item.icon; }}
      else if (item.type === 'plugin') {{ bg = '#1c1c1e'; letter = item.icon || '⚙️'; }}
      else if (item.type === 'python_app') {{ bg = '#2b2b2d'; letter = 'py'; }}
      else {{ bg = getHashColor(item.name); letter = item.name.charAt(0).toUpperCase(); }}
      div.innerHTML = `<div class="lp-icon" style="background: ${{bg}}; border: ${{item.type !== 'app' ? '1px solid #444' : 'none'}};">${{letter}}</div><div class="lp-name">${{item.name}}</div>`;
      div.onclick = () => {{ if(div._wasLongPress && div._wasLongPress()) return; closeLaunchpad(); openAppWindow(item.name, item.url, item.type, item.entry_point, item.module_name); }};
      setupLongPress(div, () => {{ if (!savedDock.includes(item.name)) {{ savedDock.push(item.name); localStorage.setItem('acornixDock', JSON.stringify(savedDock)); renderDock(); showToast("Dock Updated", `'${{item.name}}' added`); }} else showToast("Info", "Already in Dock"); }});
      lpGrid.appendChild(div);
    }});
  }}
  
  renderDock(); renderLaunchpad();
  document.getElementById('lpSearch').addEventListener('input', (e) => renderLaunchpad(e.target.value));
  const launchpad = document.getElementById('launchpad');
  function toggleLaunchpad() {{ launchpad.classList.toggle('active'); if(launchpad.classList.contains('active')) document.getElementById('lpSearch').focus(); }}
  function closeLaunchpad() {{ launchpad.classList.remove('active'); document.getElementById('lpSearch').value = ''; renderLaunchpad(); }}

  let toastTimeout;
  function showToast(title, msg) {{
    const toast = document.getElementById('toast'); document.getElementById('toastTitle').innerText = title; document.getElementById('toastMsg').innerText = msg;
    toast.classList.add('show'); clearTimeout(toastTimeout); toastTimeout = setTimeout(() => toast.classList.remove('show'), 3000);
  }}

  // --- MULTI-WINDOW MANAGER ---
  let windowCount = 0;
  let zIndexBase = 1500;
  
  // Terminal state
  let activeTerminalWinId = null;
  let terminalPollInterval = null;

  function bringToFront(winEl) {{ zIndexBase++; winEl.style.zIndex = zIndexBase; }}

  // DRAG
  function makeDraggable(winEl, headerEl) {{
      let pos1=0, pos2=0, pos3=0, pos4=0;
      headerEl.onmousedown = dragStart; headerEl.ontouchstart = dragStart;
      function dragStart(e) {{
          bringToFront(winEl);
          if (winEl.classList.contains('maximized')) return;
          e = e || window.event;
          if(e.type === 'touchstart') {{ pos3 = e.touches[0].clientX; pos4 = e.touches[0].clientY; }}
          else {{ e.preventDefault(); pos3 = e.clientX; pos4 = e.clientY; }}
          document.onmouseup = dragEnd; document.ontouchend = dragEnd;
          document.onmousemove = dragMove; document.ontouchmove = dragMove;
          document.querySelectorAll('iframe').forEach(ifr => ifr.style.pointerEvents = 'none');
      }}
      function dragMove(e) {{
          e = e || window.event; let cx, cy;
          if(e.type === 'touchmove') {{ cx = e.touches[0].clientX; cy = e.touches[0].clientY; }}
          else {{ cx = e.clientX; cy = e.clientY; }}
          pos1 = pos3 - cx; pos2 = pos4 - cy; pos3 = cx; pos4 = cy;
          winEl.style.top = (winEl.offsetTop - pos2) + "px"; winEl.style.left = (winEl.offsetLeft - pos1) + "px";
      }}
      function dragEnd() {{
          document.onmouseup = null; document.ontouchend = null;
          document.onmousemove = null; document.ontouchmove = null;
          document.querySelectorAll('iframe').forEach(ifr => ifr.style.pointerEvents = 'auto');
      }}
  }}

  // RESIZE
  function makeResizable(winEl, handleEl) {{
      let startW, startH, startX, startY;
      handleEl.onmousedown = resizeStart; handleEl.ontouchstart = resizeStart;
      function resizeStart(e) {{
          bringToFront(winEl);
          if (winEl.classList.contains('maximized')) return;
          e.stopPropagation(); 
          startW = winEl.offsetWidth; startH = winEl.offsetHeight;
          if(e.type === 'touchstart') {{ startX = e.touches[0].clientX; startY = e.touches[0].clientY; }}
          else {{ e.preventDefault(); startX = e.clientX; startY = e.clientY; }}
          document.onmouseup = resizeEnd; document.ontouchend = resizeEnd;
          document.onmousemove = resizeMove; document.ontouchmove = resizeMove;
          document.querySelectorAll('iframe').forEach(ifr => ifr.style.pointerEvents = 'none');
      }}
      function resizeMove(e) {{
          let cx, cy;
          if(e.type === 'touchmove') {{ cx = e.touches[0].clientX; cy = e.touches[0].clientY; }}
          else {{ cx = e.clientX; cy = e.clientY; }}
          let nw = startW + (cx - startX); let nh = startH + (cy - startY);
          if(nw > 250) winEl.style.width = nw + 'px';
          if(nh > 200) winEl.style.height = nh + 'px';
      }}
      function resizeEnd() {{
          document.onmouseup = null; document.ontouchend = null;
          document.onmousemove = null; document.ontouchmove = null;
          document.querySelectorAll('iframe').forEach(ifr => ifr.style.pointerEvents = 'auto');
      }}
  }}

  function openAppWindow(title, url, type, entryPoint, moduleName) {{
      const isTerminalType = (type !== 'app');

      const winId = 'win_' + (windowCount++);
      const win = document.createElement('div');
      win.className = 'os-window'; win.id = winId;
      
      const topPct  = 5 + (windowCount % 5) * 4;
      const leftPct = 3 + (windowCount % 5) * 4;
      win.style.top    = topPct + '%';
      win.style.left   = leftPct + '%';
      win.style.width  = '88%';
      win.style.height = '72%';
      
      const contentHtml = (type === 'app')
          ? `<iframe class="window-content" src="${{url}}"></iframe>`
          : `<div class="terminal-container" id="${{winId}}_tc">
               <div class="terminal-output" id="${{winId}}_out"></div>
               <form class="terminal-input-wrapper hidden" id="${{winId}}_wrap" onsubmit="event.preventDefault(); sendTermInput('${{winId}}');">
                 <span style="color:#0f0;margin-right:8px;font-weight:bold;">></span>
                 <input type="text" class="terminal-input" id="${{winId}}_in" autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false" enterkeyhint="send">
               </form>
             </div>`;

      win.innerHTML = `
        <div class="window-header" id="${{winId}}_header">
          <div class="window-controls">
            <div class="win-btn win-close" onclick="closeAppWindow('${{winId}}')"></div>
            <div class="win-btn win-max" onclick="document.getElementById('${{winId}}').classList.toggle('maximized')"></div>
          </div>
          <div style="pointer-events:none;">${{title}}</div>
          <div style="width:44px;"></div>
        </div>
        ${{contentHtml}}
        <div class="resize-handle" id="${{winId}}_resize"></div>
      `;
      
      document.getElementById('window-container').appendChild(win);
      bringToFront(win);
      win.addEventListener('mousedown',  () => bringToFront(win));
      win.addEventListener('touchstart', () => bringToFront(win), {{passive: true}});
      makeDraggable(win, document.getElementById(winId + '_header'));
      makeResizable(win, document.getElementById(winId + '_resize'));
      setTimeout(() => win.classList.add('active'), 10);
      
      if (isTerminalType) {{
          activeTerminalWinId = winId;
          fetch('/api/terminal/run', {{
              method: 'POST',
              headers: {{'Content-Type': 'application/json'}},
              body: JSON.stringify({{entry_point: entryPoint, module_name: moduleName}})
          }});
          startTerminalPolling(winId);
      }}
  }}

  function closeAppWindow(winId) {{
      const win = document.getElementById(winId);
      if (!win) return;
      win.classList.remove('active');
      setTimeout(() => win.remove(), 250);
      
      if (activeTerminalWinId === winId) {{
          fetch('/api/terminal/kill');
          if (terminalPollInterval) {{ clearInterval(terminalPollInterval); terminalPollInterval = null; }}
          activeTerminalWinId = null;
      }}
  }}

  // POLLING
  function startTerminalPolling(winId) {{
      if (terminalPollInterval) {{ clearInterval(terminalPollInterval); terminalPollInterval = null; }}
      
      terminalPollInterval = setInterval(async () => {{
          if (!document.getElementById(winId)) {{
              clearInterval(terminalPollInterval); terminalPollInterval = null;
              activeTerminalWinId = null;
              return;
          }}
          
          try {{
              const res  = await fetch('/api/terminal/poll');
              const data = await res.json();
              
              const outEl  = document.getElementById(winId + '_out');
              const wrapEl = document.getElementById(winId + '_wrap');
              const inEl   = document.getElementById(winId + '_in');
              
              if (!outEl) return; 
              
              if (data.output) {{
                  if (data.output.includes('--- [CLEAR SCREEN] ---')) {{
                      outEl.textContent = '';
                      data.output = data.output.split('--- [CLEAR SCREEN] ---').pop();
                  }}
                  outEl.textContent += data.output;
                  outEl.scrollTop = outEl.scrollHeight;
              }}
              
              if (data.waiting_input) {{
                  wrapEl.classList.remove('hidden');
                 
              }} else {{
                  wrapEl.classList.add('hidden');
              }}
              
              if (!data.running && !data.waiting_input) {{
                  clearInterval(terminalPollInterval); terminalPollInterval = null;
              }}
          }} catch(e) {{
          }}
      }}, 300); 
  }}

  function sendTermInput(winId) {{
      const inEl   = document.getElementById(winId + '_in');
      const outEl  = document.getElementById(winId + '_out');
      const wrapEl = document.getElementById(winId + '_wrap');
      if (!inEl) return;
      
      const val = inEl.value;
      outEl.textContent += val + '\\n';
      inEl.value = '';
      wrapEl.classList.add('hidden');
      outEl.scrollTop = outEl.scrollHeight;
      
      fetch('/api/terminal/input', {{
          method: 'POST',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{text: val}})
      }});
  }}

  // --- PREVENT ACCIDENTAL EXIT ---
  window.addEventListener('beforeunload', function (e) {{
      // Show confirmation dialog before closing the tab or swiping back
      e.preventDefault();
      e.returnValue = 'Are you sure you want to close the session?';
  }});

</script>
</body>
</html>"""

# --- CUSTOM OS SERVER ---
class OSHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args): pass

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/api/terminal/poll':
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
            with web_term.lock:
                data = { "output": web_term.output_buffer, "waiting_input": web_term.is_waiting_input, "running": web_term.is_running }
                web_term.output_buffer = ""
            self.wfile.write(json.dumps(data).encode('utf-8'))
            return

        if path == '/api/terminal/kill':
            with web_term.lock: web_term.is_running = False
            self.send_response(200); self.end_headers()
            return

        if path in ('/', '/index.html'):
            html_content = _generate_desktop_html() 
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache"); self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
            return

        base_dir = _find_base_folder()
        clean_path = unquote(path).lstrip('/')
        if ".." in clean_path: self.send_error(403, "Forbidden"); return
            
        real_path = clean_path if clean_path.startswith(base_dir) else os.path.join(base_dir, clean_path)

        if os.path.exists(real_path) and os.path.isfile(real_path):
            ctype, _ = mimetypes.guess_type(real_path)
            self.send_response(200); self.send_header("Content-Type", ctype or "application/octet-stream"); self.end_headers()
            with open(real_path, "rb") as f: shutil.copyfileobj(f, self.wfile)
            return

        self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/terminal/input':
            content_length = int(self.headers.get('Content-Length', 0))
            try:
                data = json.loads(self.rfile.read(content_length).decode('utf-8'))
                with web_term.lock: web_term.input_queue.append(data.get("text", ""))
            except: pass
            self.send_response(200); self.end_headers()
            return
            
        if parsed.path == '/api/terminal/run':
            content_length = int(self.headers.get('Content-Length', 0))
            try:
                data = json.loads(self.rfile.read(content_length).decode('utf-8'))
                
                if web_term.is_running:
                    with web_term.lock: web_term.is_running = False
                    time.sleep(0.3)  
                
                with web_term.lock:
                    web_term.output_buffer = ""
                    web_term.input_queue = []
                    web_term.is_waiting_input = False
                    web_term.is_running = True  
                
                threading.Thread(
                    target=execute_plugin,
                    args=(data.get("entry_point"), data.get("module_name")),
                    daemon=True
                ).start()
            except Exception as e:
                print(f"Error starting terminal: {e}")
            self.send_response(200); self.end_headers()
            return

def _open_url(url):
    if not url: return False
    termux = shutil.which("termux-open-url")
    try:
        if termux: os.system(f'{termux} "{url}"'); return True
        else:
            import webbrowser; webbrowser.open(url); return True
    except:
        import webbrowser; webbrowser.open(url); return True

def run():
    os.system("clear")
    print("==========================================")
    print(" 🍏 BOOTING acornixOS MULTI-WINDOW ")
    print("==========================================\n")
    
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    httpd = socketserver.ThreadingTCPServer(("", PORT), OSHandler)
    url = f"http://localhost:{PORT}/"
    
    print(f"📡 acornixOS running on: {url}")
    _open_url(url)
        
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    print("\n" + "="*42)
    print(" 🟢 SYSTEM ONLINE - READY TO USE")
    print("="*42)
    input("\n👉 Press [ENTER] here to STOP acornixOS and EXIT... ")
    
    print("\nShutting down OS... Please wait.")
    httpd.shutdown()

if __name__ == "__main__":
    run()