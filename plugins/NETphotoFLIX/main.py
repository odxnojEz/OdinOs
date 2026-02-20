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
from datetime import datetime
from urllib.parse import quote, unquote, urlparse, parse_qs

config = {"label": "NETphotoFLIX", "icon": "📅"}

PORT = 8082
MAX_FILES = 8000  
MAX_ROW_ITEMS = 100  

MEDIA_EXTS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".mkv", ".mov", ".webm")

DEFAULT_PATHS = [
    "/sdcard/DCIM",
    "/storage/emulated/0/DCIM",
    "/sdcard/Pictures",
    "/storage/emulated/0/Pictures",
    "/sdcard/Download",
    "/storage/emulated/0/Download",
    "/sdcard/Movies",
    "/storage/emulated/0/Movies",
    os.path.expanduser("~/DCIM"),
    os.path.expanduser("~/Pictures")
]

def is_video(filename):
    return filename.lower().endswith((".mp4", ".mkv", ".mov", ".webm"))

def find_media_paths(extra_paths=None, limit=MAX_FILES):
    paths = []
    seen = set()
    search_dirs = []
    if extra_paths:
        if isinstance(extra_paths, (list, tuple)):
            search_dirs.extend(extra_paths)
        else:
            search_dirs.append(extra_paths)
    search_dirs.extend(DEFAULT_PATHS)
    clean_dirs = []
    for d in search_dirs:
        if not d: continue
        d = os.path.expanduser(d)
        if d not in clean_dirs and os.path.isdir(d):
            clean_dirs.append(d)

    for root in clean_dirs:
        for dirpath, _, files in os.walk(root):
            for f in files:
                if f.lower().endswith(MEDIA_EXTS):
                    full = os.path.join(dirpath, f)
                    real_full = os.path.realpath(full)
                    if real_full not in seen:
                        seen.add(real_full)
                        paths.append(real_full)
                        if len(paths) >= limit:
                            return paths
    return paths

def build_mapping(paths):
    mapping = {}
    ordered = []
    for i, p in enumerate(paths):
        if not os.path.exists(p) or os.path.getsize(p) == 0:
            continue
            
        key = f"m_{i}"
        mapping[key] = p
        ordered.append(key)
    return ordered, mapping

def _group_items_by_date(ordered, mapping, items_per_month=MAX_ROW_ITEMS):
    groups = {}
    for key in ordered:
        path = mapping.get(key)
        if not path: continue
        try:
            ts = os.path.getmtime(path)
            dt = datetime.fromtimestamp(ts)
        except Exception:
            continue
            
        sort_key = dt.strftime("%Y-%m") 
        title = dt.strftime("%B %Y")    

        if sort_key not in groups:
            groups[sort_key] = {"title": title, "items": []}

        groups[sort_key]["items"].append({
            "ts": ts,
            "key": key,
            "isVideo": is_video(path)
        })

    sorted_group_keys = sorted(groups.keys(), reverse=True)

    out = []
    for sk in sorted_group_keys:
        g = groups[sk]
        g["items"].sort(key=lambda x: x["ts"], reverse=True)
        clean_items = [{"key": it["key"], "isVideo": it["isVideo"]} for it in g["items"][:items_per_month]]
        out.append((g["title"], clean_items))
    return out


def generate_gallery_html(items_by_row, title="NETphotoFLIX"):
    escaped_title = html.escape(title)
    
    template = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"/>
<title>__TITLE__</title>
<style>
  :root {
    --bg-color: #141414;
    --text-color: #e5e5e5;
    --hover-scale: 1.15;
    --transition-speed: 0.3s;
  }
  
  * { box-sizing: border-box; }
  
  body {
    margin: 0; padding: 0;
    background-color: var(--bg-color); color: var(--text-color);
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    overflow-x: hidden;
  }

  header {
    position: fixed; top: 0; width: 100%; padding: 20px 4%;
    background: linear-gradient(to bottom, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0) 100%);
    z-index: 100; display: flex; align-items: center;
    transition: background 0.5s ease;
  }
  header.scrolled { background: rgba(20, 20, 20, 0.95); }
  .logo { color: #E50914; font-size: 28px; font-weight: 900; letter-spacing: 2px; }

  .hero {
    height: 60vh; position: relative; background-size: cover; background-position: center; margin-bottom: 20px;
  }
  .hero-vignette {
    position: absolute; bottom: 0; width: 100%; height: 60%;
    background: linear-gradient(to top, var(--bg-color) 0%, transparent 100%);
  }
  .hero-content {
    position: absolute; bottom: 20%; left: 4%; width: 50%;
  }
  .hero-title { font-size: 3rem; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); margin: 0; }
  
  .slider-container {
    padding: 0 4%; margin-top: -3vw; position: relative; z-index: 10;
  }
  .row-section { margin-bottom: 30px; }
  .row-title {
    font-size: 20px; font-weight: bold; margin: 0 0 10px 0; color: #fff; text-transform: capitalize;
  }
  .carousel {
    display: flex; gap: 8px; overflow-x: auto; overflow-y: hidden; padding: 20px 0;
    scroll-behavior: smooth; scrollbar-width: none;
  }
  .carousel::-webkit-scrollbar { display: none; }
  
  .card {
    flex: 0 0 250px; height: 140px; border-radius: 4px; position: relative; cursor: pointer;
    transition: transform var(--transition-speed) ease, box-shadow var(--transition-speed) ease;
    background: #222;
  }
  .card img, .card video {
    width: 100%; height: 100%; object-fit: cover; border-radius: 4px;
  }
  .card:hover {
    transform: scale(var(--hover-scale)); z-index: 20; box-shadow: 0 10px 20px rgba(0,0,0,0.8);
  }
  
  .play-icon {
    position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
    font-size: 30px; opacity: 0.8; text-shadow: 0 0 10px black; pointer-events: none;
  }

  #modal {
    display: none; position: fixed; z-index: 999; left: 0; top: 0; width: 100%; height: 100%;
    background-color: rgba(0,0,0,0.95); align-items: center; justify-content: center;
  }
  #modal-container { max-width: 95%; max-height: 95%; display: flex; align-items: center; justify-content: center;}
  #modal-close {
    position: absolute; top: 20px; right: 40px; color: white; font-size: 40px; font-weight: bold; cursor: pointer; z-index: 1000;
  }
  
  .loader-wrapper { text-align: center; padding: 40px; color: #666; font-weight: bold; }

  @media (max-width: 768px) {
    .card { flex: 0 0 160px; height: 90px; }
    .hero { height: 40vh; }
    .row-title { font-size: 16px; }
  }
</style>
</head>
<body>
  <header id="nav">
    <div class="logo">NETphotoFLIX</div>
  </header>

  __HERO_HTML__

  <div class="slider-container" id="rows-container">
  </div>
  
  <div id="scroll-sentinel" class="loader-wrapper">Loading timeline...</div>

  <div id="modal">
    <span id="modal-close">&times;</span>
    <div id="modal-container"></div>
  </div>

  __JSON_BLOB__

<script>
window.addEventListener('scroll', () => {
    const nav = document.getElementById('nav');
    if (window.scrollY > 50) nav.classList.add('scrolled');
    else nav.classList.remove('scrolled');
});

function openModal(url, isVideo) {
    const modal = document.getElementById('modal');
    const container = document.getElementById('modal-container');
    container.innerHTML = ''; 
    
    if (isVideo) {
        const video = document.createElement('video');
        video.src = url; video.controls = true; video.autoplay = true;
        video.style.maxWidth = '100%'; video.style.maxHeight = '90vh';
        container.appendChild(video);
    } else {
        const img = document.createElement('img');
        img.src = url; img.style.maxWidth = '100%'; img.style.maxHeight = '90vh';
        container.appendChild(img);
    }
    modal.style.display = 'flex';
}

document.getElementById('modal-close').onclick = function() {
    document.getElementById('modal').style.display = 'none';
    document.getElementById('modal-container').innerHTML = '';
};

function createCardElement(item) {
  const card = document.createElement('div');
  card.className = 'card';
  // Append a timestamp to the media URL to bust the browser cache for images
  const mediaUrl = '/media/' + encodeURIComponent(item.key) + '?v=' + new Date().getTime();
  
  let thumbnail;
  if (item.isVideo) {
      thumbnail = document.createElement('video');
      thumbnail.setAttribute('data-src', mediaUrl + '#t=0.001');
      thumbnail.muted = true;
      thumbnail.playsInline = true;
      thumbnail.preload = "metadata";
      thumbnail.onerror = function() { card.style.display = 'none'; };
  } else {
      thumbnail = document.createElement('img');
      thumbnail.setAttribute('data-src', mediaUrl);
      thumbnail.onerror = function() { card.style.display = 'none'; };
  }
  
  thumbnail.className = 'lazy-thumb';
  card.appendChild(thumbnail);
  
  if(item.isVideo) {
      const playIcon = document.createElement('div');
      playIcon.className = 'play-icon';
      playIcon.innerHTML = '▶';
      card.appendChild(playIcon);
  }
  
  card.onclick = () => openModal(mediaUrl, item.isVideo);
  return {card, thumbnail};
}

const mediaObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      const mediaEl = e.target;
      const src = mediaEl.getAttribute('data-src');
      if (src && !mediaEl.src) {
          mediaEl.src = src;
          if (mediaEl.tagName === 'VIDEO') {
              mediaEl.load();
          }
      }
      mediaObserver.unobserve(mediaEl);
    }
  });
}, {rootMargin: "300px", threshold: 0.01});

(function(){
  try {
    const el = document.getElementById('embedded_rows_json');
    if (!el) {
        document.getElementById('scroll-sentinel').innerHTML = "No data found.";
        return;
    }
    const rowsData = JSON.parse(el.textContent);
    
    const container = document.getElementById('rows-container');
    const sentinel = document.getElementById('scroll-sentinel');
    
    let currentRowIndex = 0;
    const ROWS_PER_LOAD = 6; 

    function renderNextRows() {
        if(currentRowIndex >= rowsData.length) return;
        
        const end = Math.min(currentRowIndex + ROWS_PER_LOAD, rowsData.length);
        
        for(let i = currentRowIndex; i < end; i++) {
            const row = rowsData[i];
            const section = document.createElement('div');
            section.className = 'row-section';
            section.innerHTML = `<h2 class="row-title">${row.title}</h2><div class="carousel" id="row_${row.id}"></div>`;
            container.appendChild(section);
            
            const carousel = section.querySelector('.carousel');
            row.items.forEach(it => {
                const {card, thumbnail} = createCardElement(it);
                carousel.appendChild(card);
                mediaObserver.observe(thumbnail); 
            });
        }
        
        currentRowIndex = end;
        
        if(currentRowIndex >= rowsData.length) {
            sentinel.innerHTML = "End of Timeline";
            if (window.sentinelObserver) window.sentinelObserver.disconnect();
        }
    }

    renderNextRows();

    window.sentinelObserver = new IntersectionObserver((entries) => {
        if(entries[0].isIntersecting) renderNextRows();
    }, {rootMargin: "800px"});
    
    window.sentinelObserver.observe(sentinel);
    
  } catch (err) { console.error("Render Error:", err); }
})();
</script>
</body>
</html>
"""

    hero_html = ""
    rows_data = []
    
    if items_by_row:
        first_row_title, first_items = items_by_row[0]
        first_img = first_items[0] if first_items else None
        
        if first_img:
            hero_key = first_img["key"]
            hero_html = f"""
            <div class="hero" style="background-image: url('/media/{quote(hero_key)}');">
                <div class="hero-vignette"></div>
                <div class="hero-content">
                    <h1 class="hero-title">Latest Memories</h1>
                </div>
            </div>
            """

        for ridx, (rtitle, items) in enumerate(items_by_row):
            rows_data.append({
                "id": f"r{ridx}",
                "title": rtitle,
                "items": [{"key": it["key"], "isVideo": it["isVideo"]} for it in items]
            })

    safe_json = json.dumps(rows_data, ensure_ascii=False).replace("</", "<\\/")
    json_blob = f'<script id="embedded_rows_json" type="application/json">{safe_json}</script>'

    final_html = template.replace("__TITLE__", escaped_title).replace("__HERO_HTML__", hero_html).replace("__JSON_BLOB__", json_blob)
    return final_html


class GalleryHandler(http.server.SimpleHTTPRequestHandler):
    mapping = {}
    ordered = []
    items_by_row = []

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ('/', '/index.html'):
            try:
                page = generate_gallery_html(self.items_by_row, title="NETphotoFLIX")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                
                # FORCE BROWSER TO NOT CACHE THE HTML (Fixes ghost files)
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.send_header("Pragma", "no-cache")
                self.send_header("Expires", "0")
                
                self.end_headers()
                self.wfile.write(page.encode('utf-8'))
            except Exception as e:
                self.send_error(500, str(e))
            return

        if path.startswith('/media/'):
            key = unquote(path[len('/media/'):])
            real_path = self.mapping.get(key)
            if not real_path or not os.path.exists(real_path):
                self.send_error(404, "Not found")
                return
            try:
                ctype, _ = mimetypes.guess_type(real_path)
                if not ctype:
                    ctype = "application/octet-stream"
                fs = os.path.getsize(real_path)
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(fs))
                self.send_header("Accept-Ranges", "bytes")
                
                # Reduced cache time for media files to avoid stale thumbnails
                self.send_header("Cache-Control", "public, max-age=3600")
                self.end_headers()
                with open(real_path, "rb") as f:
                    shutil.copyfileobj(f, self.wfile)
            except Exception:
                pass
            return

        super().do_GET()


def run():
    os.system("clear")
    print("==========================================")
    print(" 🎬 NETphotoFLIX TIMELINE GALLERY ")
    print("==========================================\n")
    extras = []
    print("Scanning photos and extracting dates...")
    image_paths = find_media_paths(extra_paths=extras, limit=MAX_FILES)

    if not image_paths:
        print("\nNo media found.")
        return

    ordered, mapping = build_mapping(image_paths)
    items_by_row = _group_items_by_date(ordered, mapping, items_per_month=MAX_ROW_ITEMS)

    GalleryHandler.mapping = mapping
    GalleryHandler.ordered = ordered
    GalleryHandler.items_by_row = items_by_row

    print(f"\nTimeline generated with {len(items_by_row)} months of memories.")
    print(f"Starting server on port {PORT}...")
    
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    httpd = socketserver.ThreadingTCPServer(("", PORT), GalleryHandler)
    url = f"http://localhost:{PORT}/"
    
    try:
        os.system(f'termux-open-url "{url}"')
    except:
        pass
    print(f"Open in browser: {url}")
    
    # RUN SERVER IN BACKGROUND THREAD
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()

    # WAIT FOR ENTER KEY TO STOP
    print("\n" + "="*42)
    print(" 🟢 SERVER RUNNING - READY TO USE")
    print("="*42)
    input("\n👉 Press [ENTER] here to STOP the server and EXIT... ")
    
    print("\nStopping server... Please wait.")
    httpd.shutdown()
    print("Server stopped. Goodbye! 👋")


if __name__ == "__main__":
    run()