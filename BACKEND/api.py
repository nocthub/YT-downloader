from flask import Flask, request, jsonify
import yt_dlp
import threading
import uuid
import os
from flask_cors import CORS # Added for safety across networks

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# NOTE: Must match the volume mount in docker-compose.yml
DOWNLOAD_FOLDER = '/app/downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

TASK_STATUS = {}

# --- HELPER: PROGRESS HOOK ---
def progress_hook(d, task_id):
    if d['status'] == 'downloading':
        try:
            progress = float(d.get('_percent_str', '0%').replace('%', ''))
        except:
            progress = 0

        current = TASK_STATUS.get(task_id, {})
        current.update({
            "progress": progress,
            "status": "downloading",
            "speed": d.get('_speed_str', 'N/A')
        })
        TASK_STATUS[task_id] = current

    elif d['status'] == 'finished':
        TASK_STATUS[task_id].update({"progress": 100, "status": "finished", "speed": "Done"})

    elif d['status'] == 'error':
        TASK_STATUS[task_id] = {"progress": 0, "status": "error", "speed": "N/A"}

# --- DOWNLOAD THREAD ---
def start_download_thread(url, type_mode, quality, task_id):
    TASK_STATUS[task_id] = {"progress": 0, "status": "starting", "speed": "N/A", "title": "Processing..."}

    if type_mode == 'video':
        # The best format string for muxing video/audio
        if quality == 'max': fmt = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        elif quality == '1080p': fmt = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]/best'
        elif quality == '720p': fmt = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]/best'
        else: fmt = 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360]/best'
    else: # Audio
        fmt = 'bestaudio/best'

    # Filename template
    out_tmpl = f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s'

    ydl_opts = {
        'outtmpl': out_tmpl,
        'format': fmt,
        'progress_hooks': [lambda d: progress_hook(d, task_id)],
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        'source_address': '0.0.0.0',
        'overwrites': True,
    }

    if type_mode == 'audio':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320' if quality == '320k' else '128',
        }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # We don't need to call extract_info separately here, as it's not needed by the progress
            ydl.download([url])
    except Exception as e:
        TASK_STATUS[task_id] = {"progress": 0, "status": f"error: {str(e)}", "speed": "N/A"}

# --- ROUTES ---

@app.route('/info', methods=['POST'])
def get_video_info():
    """REQUIRED: Fetches video metadata for the frontend card."""
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"status": "error", "message": "No URL provided"}), 400

    try:
        ydl_opts = {'quiet': True, 'noprogress': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration_string') or f"{info.get('duration', 0)} seconds"
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/download', methods=['POST'])
def handle_download():
    """Starts the download process in a background thread."""
    data = request.json
    url = data.get('url')
    type_mode = data.get('type')
    quality = data.get('quality')

    if not all([url, type_mode, quality]):
        return jsonify({"status": "error", "message": "Missing download parameters"}), 400

    task_id = str(uuid.uuid4())
    thread = threading.Thread(target=start_download_thread, args=(url, type_mode, quality, task_id))
    thread.start()
    return jsonify({"status": "processing", "task_id": task_id}), 202

@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    """Returns the current progress status of a task."""
    return jsonify(TASK_STATUS.get(task_id, {"status": "pending", "progress": 0, "speed": "N/A"}))

@app.route('/files', methods=['GET'])
def list_files():
    """Returns a list of files in the downloads folder with metadata."""
    try:
        files_list = []
        if os.path.exists(DOWNLOAD_FOLDER):
            for filename in os.listdir(DOWNLOAD_FOLDER):
                filepath = os.path.join(DOWNLOAD_FOLDER, filename)
                if os.path.isfile(filepath):
                    stat_info = os.stat(filepath)
                    file_size = stat_info.st_size
                    
                    # Format file size to human-readable format
                    if file_size < 1024:
                        size_str = f"{file_size} B"
                    elif file_size < 1024 * 1024:
                        size_str = f"{file_size / 1024:.1f} KB"
                    elif file_size < 1024 * 1024 * 1024:
                        size_str = f"{file_size / (1024 * 1024):.1f} MB"
                    else:
                        size_str = f"{file_size / (1024 * 1024 * 1024):.2f} GB"
                    
                    files_list.append({
                        "name": filename,
                        "size": size_str,
                        "size_bytes": file_size,
                        "modified": stat_info.st_mtime,
                        "extension": os.path.splitext(filename)[1].lower()
                    })
            
            # Sort by modification time (newest first)
            files_list.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({"files": files_list})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    """Serve files as downloadable attachments."""
    try:
        # Prevent path traversal attacks
        safe_filename = os.path.basename(filename)
        filepath = os.path.join(DOWNLOAD_FOLDER, safe_filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            return jsonify({"status": "error", "message": "File not found"}), 404
        
        from flask import send_file
        return send_file(filepath, as_attachment=True, download_name=safe_filename)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/delete/<path:filename>', methods=['DELETE'])
def delete_file(filename):
    """Delete a file from the downloads folder."""
    try:
        # Prevent path traversal attacks
        safe_filename = os.path.basename(filename)
        filepath = os.path.join(DOWNLOAD_FOLDER, safe_filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            return jsonify({"status": "error", "message": "File not found"}), 404
        
        # Delete the file
        os.remove(filepath)
        return jsonify({"status": "success", "message": f"File {safe_filename} deleted successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
