from flask import Flask, render_template, request, jsonify, send_from_directory
import yt_dlp
import os
import json
import re
from datetime import datetime
import threading
import subprocess
import requests
from packaging import version
import logging
from logging.handlers import RotatingFileHandler
import traceback

app = Flask(__name__)

# Configure logging
LOG_DIR = '/app/logs'
os.makedirs(LOG_DIR, exist_ok=True)

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            os.path.join(LOG_DIR, 'ytdlp-web.log'),
            maxBytes=10485760,  # 10MB
            backupCount=5
        ),
        logging.StreamHandler()  # Also log to console
    ]
)
logger = logging.getLogger(__name__)
logger.info("yt-dlp web app starting up")

# Configuration
# Base directory for browsing - defaults to /media but can be overridden
BASE_DIR = os.environ.get('BASE_DIR', '/media')

# Create a default downloads directory if nothing is mounted
DEFAULT_DOWNLOAD_DIR = '/downloads'
os.makedirs(DEFAULT_DOWNLOAD_DIR, exist_ok=True)

# Store download progress
download_status = {}
# Track downloads that should be cancelled
cancelled_downloads = set()

class ProgressLogger:
    def __init__(self, download_id):
        self.download_id = download_id

    def debug(self, msg):
        # Log yt-dlp debug messages at INFO level so they appear in logs
        # Filter out some noisy debug messages
        if msg and not msg.startswith('[debug]'):
            logger.info(f"[{self.download_id}] {msg}")

    def warning(self, msg):
        logger.warning(f"[{self.download_id}] {msg}")
        download_status[self.download_id]['warning'] = msg

    def error(self, msg):
        logger.error(f"[{self.download_id}] {msg}")
        download_status[self.download_id]['error'] = msg
        download_status[self.download_id]['status'] = 'error'

def progress_hook(d, download_id):
    """Hook to track download progress"""
    # Check if this download was cancelled
    if download_id in cancelled_downloads:
        raise Exception('Download cancelled by user')

    if d['status'] == 'downloading':
        download_status[download_id].update({
            'status': 'downloading',
            'percent': d.get('_percent_str', 'N/A'),
            'speed': d.get('_speed_str', 'N/A'),
            'eta': d.get('_eta_str', 'N/A'),
            'downloaded': d.get('_downloaded_bytes_str', 'N/A'),
            'total': d.get('_total_bytes_str', 'N/A')
        })
    elif d['status'] == 'finished':
        download_status[download_id].update({
            'status': 'processing',
            'message': 'Processing download...'
        })

def download_video(url, options, download_id, download_dir):
    """Background task to download video"""
    try:
        logger.info(f"[{download_id}] Starting download of {url} to {download_dir}")
        logger.info(f"[{download_id}] Options: {json.dumps(options, indent=2)}")
        
        ydl_opts = {
            'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
            'logger': ProgressLogger(download_id),
            'verbose': True,  # Enable verbose logging for yt-dlp
        }
        
        # Merge user options
        ydl_opts.update(options)
        
        logger.info(f"[{download_id}] Final yt-dlp options: {json.dumps(ydl_opts, indent=2, default=str)}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"[{download_id}] Extracting info from URL...")
            info = ydl.extract_info(url, download=True)
            
            # Get the actual downloaded filename
            filename = ydl.prepare_filename(info)
            
            # For audio files, the extension might be different
            if options.get('postprocessors'):
                # Check if MP3 conversion was requested
                for pp in options['postprocessors']:
                    if pp.get('key') == 'FFmpegExtractAudio':
                        # Replace extension with the actual audio format
                        base_name = os.path.splitext(filename)[0]
                        audio_ext = pp.get('preferredcodec', 'mp3')
                        filename = f"{base_name}.{audio_ext}"
                        logger.info(f"[{download_id}] Audio file expected at: {filename}")
            
            # Check if file actually exists
            if not os.path.exists(filename):
                logger.warning(f"[{download_id}] Expected file not found at {filename}, checking directory...")
                # List all files in the directory to help debug
                if os.path.exists(download_dir):
                    files = os.listdir(download_dir)
                    logger.info(f"[{download_id}] Files in {download_dir}: {files}")
            
            logger.info(f"[{download_id}] Download completed successfully: {filename}")
            
            download_status[download_id].update({
                'status': 'completed',
                'message': f'Download completed: {os.path.basename(filename)}',
                'filename': os.path.basename(filename),
                'full_path': filename
            })
            
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        logger.error(f"[{download_id}] Download failed: {error_msg}")
        logger.error(f"[{download_id}] Traceback: {error_trace}")
        
        download_status[download_id].update({
            'status': 'error',
            'error': error_msg,
            'traceback': error_trace
        })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/options')
def options():
    return render_template('all_ytdlp_options.html')

@app.route('/browse')
def browse_directory():
    """Browse directories for selecting download location"""
    path = request.args.get('path', '/')
    
    # Security: ensure path doesn't escape the container
    safe_path = os.path.abspath(path)
    if not safe_path.startswith('/'):
        safe_path = '/'
    
    try:
        entries = []
        
        # List all entries in the directory
        if os.path.exists(safe_path) and os.path.isdir(safe_path):
            for entry in sorted(os.listdir(safe_path)):
                entry_path = os.path.join(safe_path, entry)
                if os.path.isdir(entry_path):
                    # Check if writable
                    writable = os.access(entry_path, os.W_OK)
                    entries.append({
                        'name': entry,
                        'path': entry_path,
                        'type': 'directory',
                        'writable': writable
                    })
        
        # Add parent directory option if not at root
        if safe_path != '/':
            parent = os.path.dirname(safe_path)
            entries.insert(0, {
                'name': '..',
                'path': parent,
                'type': 'parent',
                'writable': False
            })
            
        return jsonify({
            'current_path': safe_path,
            'entries': entries,
            'writable': os.access(safe_path, os.W_OK)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/create-folder', methods=['POST'])
def create_folder():
    """Create a new folder in the specified directory"""
    data = request.json
    parent_path = data.get('parent_path', '/')
    folder_name = data.get('folder_name', '').strip()

    # Validate folder name
    if not folder_name:
        return jsonify({'success': False, 'error': 'Folder name cannot be empty'}), 400

    # Security: prevent path traversal
    if '/' in folder_name or '\\' in folder_name or folder_name in ['.', '..']:
        return jsonify({'success': False, 'error': 'Invalid folder name'}), 400

    # Security: ensure parent path is safe
    safe_parent = os.path.abspath(parent_path)
    if not safe_parent.startswith('/'):
        safe_parent = '/'

    new_folder_path = os.path.join(safe_parent, folder_name)

    try:
        # Check if parent directory is writable
        if not os.access(safe_parent, os.W_OK):
            return jsonify({'success': False, 'error': 'Parent directory is not writable'}), 403

        # Check if folder already exists
        if os.path.exists(new_folder_path):
            return jsonify({'success': False, 'error': 'Folder already exists'}), 400

        # Create the folder
        os.makedirs(new_folder_path, exist_ok=False)
        logger.info(f"Created new folder: {new_folder_path}")

        return jsonify({'success': True, 'path': new_folder_path})
    except PermissionError:
        return jsonify({'success': False, 'error': 'Permission denied'}), 403
    except Exception as e:
        logger.error(f"Error creating folder: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/extract-playlist', methods=['POST'])
def extract_playlist():
    """Extract playlist info without downloading"""
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        logger.info(f"Extracting playlist info from: {url}")

        ydl_opts = {
            'extract_flat': 'in_playlist',  # Don't download, just get info
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if info is None:
                return jsonify({'error': 'Could not extract info from URL'}), 400

            # Check if it's actually a playlist
            if info.get('_type') == 'playlist' or 'entries' in info:
                entries = list(info.get('entries', []))
                videos = []

                for i, entry in enumerate(entries):
                    if entry is None:
                        continue
                    videos.append({
                        'index': i + 1,
                        'id': entry.get('id', ''),
                        'title': entry.get('title', f'Video {i + 1}'),
                        'url': entry.get('url') or entry.get('webpage_url') or f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                        'duration': entry.get('duration'),
                        'uploader': entry.get('uploader', ''),
                    })

                logger.info(f"Extracted playlist with {len(videos)} videos")

                return jsonify({
                    'is_playlist': True,
                    'title': info.get('title', 'Playlist'),
                    'uploader': info.get('uploader', ''),
                    'video_count': len(videos),
                    'videos': videos
                })
            else:
                # Single video, not a playlist
                return jsonify({
                    'is_playlist': False,
                    'title': info.get('title', 'Video'),
                    'video_count': 1,
                    'videos': [{
                        'index': 1,
                        'id': info.get('id', ''),
                        'title': info.get('title', 'Video'),
                        'url': url,
                        'duration': info.get('duration'),
                        'uploader': info.get('uploader', ''),
                    }]
                })

    except Exception as e:
        logger.error(f"Error extracting playlist: {str(e)}")
        return jsonify({'error': str(e), 'fallback': True}), 500


@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    # Get the selected download path
    download_path = data.get('downloadPath', DEFAULT_DOWNLOAD_DIR)
    
    # Security: ensure path is absolute and within container
    download_dir = os.path.abspath(download_path)
    
    # Check if directory exists and is writable
    if not os.path.exists(download_dir):
        try:
            os.makedirs(download_dir, exist_ok=True)
        except Exception as e:
            return jsonify({'error': f'Cannot create directory: {str(e)}'}), 400
    
    if not os.access(download_dir, os.W_OK):
        return jsonify({'error': 'Directory is not writable'}), 400
    
    # Generate unique download ID
    download_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    
    # Initialize status
    download_status[download_id] = {
        'status': 'starting',
        'url': url,
        'directory': download_dir,
        'started': datetime.now().isoformat()
    }
    
    # Parse options
    options = {}
    
    # Playlist handling - by default, only download single video
    if not data.get('downloadPlaylist', False):
        options['noplaylist'] = True
        logger.info(f"[{download_id}] Single video mode enabled (noplaylist: true)")
    else:
        logger.info(f"[{download_id}] Playlist mode enabled")
    
    # Format selection
    format_option = data.get('format', 'best')
    if format_option != 'best':
        options['format'] = format_option
    
    # Audio only
    if data.get('audioOnly', False):
        options['format'] = 'bestaudio/best'
        options['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    
    # Subtitle options
    if data.get('subtitles', False):
        options['writesubtitles'] = True
        options['writeautomaticsub'] = True
    
    # Custom output template
    if data.get('outputTemplate'):
        options['outtmpl'] = os.path.join(download_dir, data['outputTemplate'])
    
    # Playlist handling
    if data.get('playlistStart'):
        options['playliststart'] = int(data['playlistStart'])
    if data.get('playlistEnd'):
        options['playlistend'] = int(data['playlistEnd'])
    
    # Custom flags (advanced) - handle all possible yt-dlp options
    custom_flags = data.get('customFlags', {})
    if custom_flags:
        # Process the comprehensive options from UI
        for key, value in custom_flags.items():
            if value is not None and value != '' and value != False:
                # Convert camelCase from JS to snake_case for yt-dlp
                snake_key = re.sub('([A-Z])', r'_\1', key).lower()
                
                # Handle special cases
                if snake_key in ['ignore_errors', 'no_warnings', 'quiet', 'verbose']:
                    options[snake_key] = value
                elif snake_key == 'limit_rate':
                    options['ratelimit'] = value
                elif snake_key == 'write_subs':
                    options['writesubtitles'] = value
                elif snake_key == 'write_auto_subs':
                    options['writeautomaticsub'] = value
                else:
                    # Direct mapping for most options
                    options[snake_key] = value
        
        logger.info(f"[{download_id}] Advanced options applied: {len(custom_flags)} settings")
    
    # Start download in background thread
    thread = threading.Thread(target=download_video, args=(url, options, download_id, download_dir))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'download_id': download_id,
        'message': 'Download started'
    })

@app.route('/status/<download_id>')
def status(download_id):
    if download_id in download_status:
        return jsonify(download_status[download_id])
    return jsonify({'error': 'Download not found'}), 404


@app.route('/cancel/<download_id>', methods=['POST'])
def cancel_download(download_id):
    """Cancel an active download"""
    if download_id not in download_status:
        return jsonify({'error': 'Download not found'}), 404

    current_status = download_status[download_id].get('status')
    if current_status in ['completed', 'error', 'cancelled']:
        return jsonify({'error': f'Download already {current_status}'}), 400

    # Mark for cancellation
    cancelled_downloads.add(download_id)
    download_status[download_id].update({
        'status': 'cancelled',
        'message': 'Cancelled by user'
    })

    logger.info(f"[{download_id}] Download cancelled by user")
    return jsonify({'success': True, 'message': 'Download cancelled'})

@app.route('/downloads')
def list_downloads():
    """List recent downloaded files from tracked downloads"""
    try:
        all_files = []
        checked_paths = set()
        
        # Get files from recent download locations
        for dl_id, dl_info in download_status.items():
            if dl_info.get('status') == 'completed':
                dir_path = dl_info.get('directory', '')
                if dir_path and dir_path not in checked_paths and os.path.exists(dir_path):
                    checked_paths.add(dir_path)
                    try:
                        for filename in os.listdir(dir_path):
                            filepath = os.path.join(dir_path, filename)
                            if os.path.isfile(filepath):
                                # Only show files modified in last 7 days
                                mtime = os.path.getmtime(filepath)
                                if (datetime.now() - datetime.fromtimestamp(mtime)).days <= 7:
                                    all_files.append({
                                        'name': filename,
                                        'size': os.path.getsize(filepath),
                                        'modified': datetime.fromtimestamp(mtime).isoformat(),
                                        'directory': dir_path,
                                        'path': filepath
                                    })
                    except:
                        pass
        
        # Also check default download directory
        if DEFAULT_DOWNLOAD_DIR not in checked_paths and os.path.exists(DEFAULT_DOWNLOAD_DIR):
            for filename in os.listdir(DEFAULT_DOWNLOAD_DIR):
                filepath = os.path.join(DEFAULT_DOWNLOAD_DIR, filename)
                if os.path.isfile(filepath):
                    all_files.append({
                        'name': filename,
                        'size': os.path.getsize(filepath),
                        'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
                        'directory': DEFAULT_DOWNLOAD_DIR,
                        'path': filepath
                    })
        
        # Sort by modification time, newest first
        all_files.sort(key=lambda x: x['modified'], reverse=True)
        # Limit to 50 most recent files
        return jsonify({'files': all_files[:50]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download-file')
def download_file():
    """Serve downloaded files from their actual path"""
    try:
        filepath = request.args.get('path')
        if not filepath:
            return jsonify({'error': 'No file path provided'}), 400
        
        # Security check - ensure file exists and is within the container
        safe_path = os.path.abspath(filepath)
        
        if os.path.exists(safe_path) and os.path.isfile(safe_path):
            directory = os.path.dirname(safe_path)
            filename = os.path.basename(safe_path)
            return send_from_directory(directory, filename, as_attachment=True)
        
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/delete-file', methods=['POST'])
def delete_file():
    """Delete a downloaded file"""
    try:
        filepath = request.json.get('path')
        if not filepath:
            return jsonify({'error': 'No file path provided'}), 400
        
        # Security check - ensure file exists and is within the container
        safe_path = os.path.abspath(filepath)
        
        if not os.path.exists(safe_path):
            return jsonify({'error': 'File not found'}), 404
        
        if not os.path.isfile(safe_path):
            return jsonify({'error': 'Not a file'}), 400
        
        # Delete the file
        os.remove(safe_path)
        logger.info(f"Deleted file: {safe_path}")
        
        return jsonify({
            'success': True,
            'message': f'File deleted: {os.path.basename(safe_path)}'
        })
    except PermissionError:
        logger.error(f"Permission denied deleting file: {filepath}")
        return jsonify({'error': 'Permission denied'}), 403
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/logs')
def get_logs():
    """Get recent log entries, filtering out HTTP request noise"""
    try:
        log_file = os.path.join(LOG_DIR, 'ytdlp-web.log')
        lines = request.args.get('lines', 100, type=int)

        if not os.path.exists(log_file):
            return jsonify({'logs': 'No logs available yet'})

        # Read log file and filter out werkzeug HTTP request logs
        with open(log_file, 'r') as f:
            all_lines = f.readlines()

        # Filter out werkzeug HTTP request lines (GET/POST requests)
        filtered_lines = [
            line for line in all_lines
            if '- werkzeug -' not in line and 'HTTP/1.1"' not in line
        ]

        recent_lines = filtered_lines[-lines:] if len(filtered_lines) > lines else filtered_lines

        return jsonify({
            'logs': ''.join(recent_lines) if recent_lines else 'No download logs yet. Start a download to see logs here.',
            'total_lines': len(filtered_lines)
        })
    except Exception as e:
        logger.error(f"Error reading logs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/version')
def check_version():
    """Check current and latest yt-dlp version"""
    try:
        # Get current version
        current_version = yt_dlp.version.__version__
        
        # Check latest version from GitHub API
        try:
            response = requests.get(
                'https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest',
                timeout=5
            )
            if response.status_code == 200:
                latest_version = response.json()['tag_name']
                # Remove 'v' prefix if present
                if latest_version.startswith('v'):
                    latest_version = latest_version[1:]
                
                # Compare versions
                update_available = version.parse(latest_version) > version.parse(current_version)
                
                return jsonify({
                    'current': current_version,
                    'latest': latest_version,
                    'update_available': update_available
                })
            else:
                return jsonify({
                    'current': current_version,
                    'latest': 'unknown',
                    'update_available': False,
                    'error': 'Could not fetch latest version'
                })
        except Exception as e:
            return jsonify({
                'current': current_version,
                'latest': 'unknown',
                'update_available': False,
                'error': str(e)
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update', methods=['POST'])
def update_ytdlp():
    """Update yt-dlp to the latest version"""
    try:
        # Run pip upgrade command
        result = subprocess.run(
            ['pip', 'install', '--upgrade', 'yt-dlp'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # Get new version
            import importlib
            importlib.reload(yt_dlp.version)
            new_version = yt_dlp.version.__version__
            
            return jsonify({
                'success': True,
                'message': f'Successfully updated to version {new_version}',
                'version': new_version
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr or 'Update failed'
            }), 500
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Update timed out'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
