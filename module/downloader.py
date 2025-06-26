from module.logger import Log

try:
    import yt_dlp
    import spotdl
except ModuleNotFoundError:
    import os
    import sys
    os.system('pip install -U yt-dlp')
    os.system('pip install -U spotdl')
    Log.Info("Module installed! Restarting...")
    os.execv(sys.executable, ['python'] + sys.argv)

import os
import json
import random
import subprocess

class Downloader:
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            _config = json.load(f)
        _use_cookie = _config.get("login", False)
    except (FileNotFoundError, json.JSONDecodeError):
        _use_cookie = False

    _cookie_file = os.path.join(os.getcwd(), "cookie", "cookies.txt")

    @staticmethod
    def video_info(url: str) -> str:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'noplaylist': True
        }
        
        if Downloader._use_cookie and ("youtube.com" in url or "youtu.be" in url):
            if os.path.exists(Downloader._cookie_file):
                ydl_opts['cookiefile'] = Downloader._cookie_file
            else:
                Log.Info(f"Cookie file not found: {Downloader._cookie_file}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            v_info = ydl.extract_info(url, download=False)
            title = v_info.get('title', 'Unknown Title')
            formats = v_info.get('formats', [])
            
            format_data = {
                "video_title": title,
                "video_url": url,
                "is_playlist": bool('entries' in v_info),
                "formats": []
            }
            
            if "nicovideo.jp" in url:
                available_formats = []
                for f in formats:
                    format_id = f.get('format_id', '')
                    ext = f.get('ext', 'unknown')
                    height = f.get('height')
                    width = f.get('width')
                    
                    if ext != 'mp4':
                        continue
                    
                    if height is None or width is None:
                        continue
                    
                    resolution = f"{width}x{height}"
                    note = f"{height}p"
                    
                    available_formats.append({
                        "format_id": format_id,
                        "ext": ext,
                        "resolution": resolution,
                        "note": note
                    })
                
                format_data["formats"] = available_formats
            else:
                resolution_map = {}
                for f in formats:
                    format_id = f.get('format_id')
                    ext = f.get('ext', 'unknown')
                    height = f.get('height')
                    width = f.get('width')
                    vcodec = f.get('vcodec', 'none')
                    acodec = f.get('acodec', 'none')
                    filesize = f.get('filesize', 0)
                    
                    if ext != 'mp4' or height is None or width is None:
                        continue
                    
                    resolution = f"{width}x{height}"
                    note = f"{height}p"
                    
                    current_size = resolution_map.get(resolution, {}).get('filesize', float('inf'))
                    if resolution not in resolution_map or (filesize and filesize < current_size):
                        resolution_map[resolution] = {
                            "format_id": format_id,
                            "ext": ext,
                            "resolution": resolution,
                            "note": note,
                            "vcodec": vcodec,
                            "acodec": acodec,
                            "filesize": filesize
                        }
                
                format_data["formats"] = list(resolution_map.values())
            
            def safe_sort_key(fmt):
                try:
                    return int(fmt["note"].replace("p", ""))
                except (ValueError, KeyError, AttributeError):
                    return 0
            
            if format_data["formats"]:
                format_data["formats"].sort(key=safe_sort_key)
            
            random_id = random.randint(100000, 999999)
            json_path = os.path.join(os.getcwd(), "Temp", f"{random_id}.json")
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(format_data, f, indent=4, ensure_ascii=False)
            
            return json_path

    @staticmethod
    def mp4_dl(url: str, format_id: str, save_dir: str) -> None:
        ffmpeg_path = os.path.join(os.getcwd(), "FFmpeg", "bin", "ffmpeg.exe")
        
        if "nicovideo.jp" in url:
            ydl_opts = {
                'format': f"{format_id}+bestaudio/best",
                'outtmpl': os.path.join(save_dir, '%(title)s.%(ext)s'),
                "noplaylist": True,
                "ffmpeg_location": ffmpeg_path,
                "prefer_ffmpeg": True,
                "quiet": True,
                "no_warnings": True,
                "extract_flat": False
            }
        else:
            ydl_opts = {
                'format': f'{format_id}+bestaudio[ext=m4a]/best',
                'outtmpl': os.path.join(save_dir, '%(title)s.%(ext)s'),
                "noplaylist": True,
                "ffmpeg_location": ffmpeg_path,
                "prefer_ffmpeg": True,
                "quiet": True,
                "no_warnings": True,
                "extract_flat": False
            }
        
        if Downloader._use_cookie and ("youtube.com" in url or "youtu.be" in url):
            if os.path.exists(Downloader._cookie_file):
                ydl_opts['cookiefile'] = Downloader._cookie_file
            else:
                Log.Info(f"Cookie file not found: {Downloader._cookie_file}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
            except Exception as e:
                Log.Error(f"Download failed: {str(e)}")
    
    @staticmethod
    def mp3_dl(url: str, save_dir: str) -> None:
        ffmpeg_path = os.path.join(os.getcwd(), "FFmpeg", "bin", "ffmpeg.exe")
            
        ydl_opts = {
            "format": "bestaudio/best",
            'outtmpl': os.path.join(save_dir, '%(title)s.%(ext)s'),
            "noplaylist": True,
            "ffmpeg_location": ffmpeg_path,
            "quiet": True,
            "no_warnings": True,
            "postprocessors": [
                {"key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"},
                {"key": "FFmpegMetadata"},
            ],
        }
        
        if Downloader._use_cookie and ("youtube.com" in url or "youtu.be" in url):
            if os.path.exists(Downloader._cookie_file):
                ydl_opts['cookiefile'] = Downloader._cookie_file
            else:
                Log.Info(f"Cookie file not found: {Downloader._cookie_file}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
            except Exception as e:
                Log.Error(f"Download failed: {str(e)}")

    @staticmethod
    def spotify(url: str, save_dir: str) -> None:
        subprocess.run(f"spotdl download {url}", stdout=subprocess.PIPE, cwd=os.path.expanduser(f'{save_dir}'))
    
    @staticmethod
    def twitter(url: str, save_dir: str) -> None:
        ydl_opts = {
            'outtmpl': os.path.join(save_dir, '%(title)s.%(ext)s'),
            'quiet': True,    
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
            except Exception as e:
                Log.Error(f"Download failed: {str(e)}")