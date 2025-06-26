from module.logger import Log
from module.extension import Extension
from module.downloader import Downloader
from module.updater import AutoUpdater

try:
    import os
    import json
    import yt_dlp
    Log.Info("Module loaded!")
except ModuleNotFoundError:
    import os
    import sys
    os.system('pip install yt-dlp')
    os.system('pip install spotdl')
    Log.Info("Module installed! Restarting...")
    os.execv(sys.executable, ['python'] + sys.argv)

__version__ = "0.2.0"

def main():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            _config = json.load(f)
            _auto_update = _config.get("auto_update", False)
    except (FileNotFoundError, json.JSONDecodeError):
        _auto_update = False

    if _auto_update:
        try:
            success = AutoUpdater.check_updates(__version__)
            if success:
                AutoUpdater.update()
        except Exception as e:
            Log.Error(f"Error: {str(e)}")

    Extension.clear_screen()
    print("""\033[36m                                                               
                                                               
 ###  ##  #######  ######   ##                ##   ##  ####### 
 #### ##                ##  ##                ##   ##  ##      
 ## ####  ##       ##   ##  ##                ##   ##  ####### 
 ##  ###  ##       ##   ##  ##   ##            ## ##        ## 
 ##   ##  #######  ######   #######             ###    ####### 
                                                               
    1: Youtube Downloader   3: Spotify Downloader  5: Converter
    2: Niconico Downloader  4: Twitter Downloader  6: Exit
\033[0m""")
    
    try:
        mode = str(input("Mode >> "))

        ############################################
        if mode not in ["1", "2", "3", "4", "5", "6", "exit"]:
            Extension.clear_screen()
            Log.Error("Invalid mode!")
            input("Press Enter to continue...")
            main()
        ############################################

        if mode == "exit" or mode == "6":
            exit()

        Extension.clear_screen()

        if mode == "1":
            mode = input("Mode(mp3 or mp4) >> ")

            if mode != "mp3" and mode != "mp4":
                Extension.clear_screen()
                Log.Error("Invalid mode! Please enter mp3 or mp4")
                input("Press Enter to continue...")
                main()

            if mode == "mp3":
                url = input("URL >> ")

                if not ("youtube.com" in url or "youtu.be" in url):
                    Log.Error("Invalid URL!")
                    input("Press Enter to continue...")
                    main()

                save_dir = os.getcwd() + R"/Downloads"
                v_info = Downloader.video_info(str(url))
                
                with open(v_info, "r", encoding="utf-8") as json_f:
                    data = json.load(json_f)
                    Extension.clear_screen()

                    Log.Info(f"Video info Scraped!\n\n")
                    Log.Info(f"Video Title: {data['video_title']}\n")
                    Log.Info("Downloading...")
                    try:
                        Downloader.mp3_dl(url, save_dir)
                    except yt_dlp.DownloadError as e:
                        Log.Error(f"Error: {str(e)}")
                        input("Press Enter to continue...")
                        main()

                    Log.Info("Download completed!")
                    input("Press Enter to continue...")
                    json_f.close()
                    os.remove(v_info)
                    main()

            if mode == "mp4":
                url = input("URL >> ")

                if not ("youtube.com" in url or "youtu.be" in url):
                    Log.Error("Invalid URL!")
                    input("Press Enter to continue...")
                    main()

                save_dir = os.getcwd() + R"/Downloads"
                v_info = Downloader.video_info(str(url))
                
                with open(v_info, "r", encoding="utf-8") as json_f:
                    data = json.load(json_f)
                    Extension.clear_screen()

                    Log.Info(f"Video info Scraped!\n\n")
                    Log.Info(f"Video Title: {data['video_title']}\n")
                    Log.Info("Available Formats:")

                    for i, f in enumerate(data['formats']):
                        Log.Info(f"{i+1}: {f['ext']} - {f['resolution']} - {f['note']}")
                    
                    format_num = int(input("Format id >> "))
                    format_id = data['formats'][format_num-1]['format_id']

                    try:
                        Downloader.mp4_dl(url, format_id, save_dir)
                    except yt_dlp.DownloadError as e:
                        Log.Error(f"Error: {str(e)}")
                        input("Press Enter to continue...")
                        main()

                    Log.Info("Download completed!")
                    input("Press Enter to continue...")
                    json_f.close()
                    os.remove(v_info)
                    main()

        if mode == "2":
            mode = input("Mode(mp3 or mp4) >> ")

            if mode != "mp3" and mode != "mp4":
                Extension.clear_screen()
                Log.Error("Invalid mode! Please enter mp3 or mp4")
                input("Press Enter to continue...")
                main()

            if mode == "mp3":
                url = input("URL >> ")

                if not ("nicovideo.jp" in url):
                    Log.Error("Invalid URL!")
                    input("Press Enter to continue...")
                    main()

                save_dir = os.getcwd() + R"/Downloads"
                v_info = Downloader.video_info(str(url))
                
                with open(v_info, "r", encoding="utf-8") as json_f:
                    data = json.load(json_f)
                    Extension.clear_screen()

                    Log.Info(f"Video info Scraped!\n\n")
                    Log.Info(f"Video Title: {data['video_title']}\n")
                    Log.Info("Downloading...")

                    Downloader.mp3_dl(url, save_dir)

                    Log.Info("Download completed!")
                    input("Press Enter to continue...")
                    json_f.close()
                    os.remove(v_info)
                    main()

            if mode == "mp4":
                url = input("URL >> ")

                if not ("nicovideo.jp" in url):
                    Log.Error("Invalid URL!")
                    input("Press Enter to continue...")
                    main()

                save_dir = os.getcwd() + R"/Downloads"
                v_info = Downloader.video_info(str(url))
                
                with open(v_info, "r", encoding="utf-8") as json_f:
                    data = json.load(json_f)
                    Extension.clear_screen()

                    Log.Info(f"Video info Scraped!\n\n")
                    Log.Info(f"Video Title: {data['video_title']}\n")
                    Log.Info("Available Formats:")

                    for i, f in enumerate(data['formats']):
                        Log.Info(f"{i+1}: {f['ext']} - {f['resolution']} - {f['note']}")
                    
                    format_num = int(input("Format id >> "))
                    format_id = data['formats'][format_num-1]['format_id']

                    Downloader.mp4_dl(url, format_id, save_dir)

                    Log.Info("Download completed!")
                    input("Press Enter to continue...")
                    json_f.close()
                    os.remove(v_info)
                    main()
        
        if mode == "3":
            url = input("URL >> ")

            if not ("spotify.com" in url):
                Log.Error("Invalid URL!")
                input("Press Enter to continue...")
                main()
            
            save_dir = os.getcwd() + R"/Downloads"

            Extension.clear_screen()

            Log.Info("Downloading...")

            Downloader.spotify(url, save_dir)

            Log.Info("Download completed!")
            input("Press Enter to continue...")
            main()

        if mode == "4":
            url = input("Tweet URL >> ")

            if not ("twimg.com" in url or "twitter.com" in url or "x.com" in url):
                Log.Error("Invalid URL!")
                input("Press Enter to continue...")
                main()
            
            save_dir = os.getcwd() + R"/Downloads"

            Extension.clear_screen()

            Log.Info("Downloading...")

            Downloader.twitter(url, save_dir)

            Log.Info("Download completed!")
            input("Press Enter to continue...")
            main()
        
        if mode == "5":
            confirm = input("Are you sure you want to convert? (y/n) >> ").lower()

            if confirm != "y":
                Extension.clear_screen()
                Log.Info("Conversion cancelled!")
                input("Press Enter to continue...")
                main()
            
            ext = input("Enter the extension of the converted file (e.g. mp3, wav, aac) >> ").strip().lower()
            if not ext.isalnum():
                Log.Error("invaild extension! Please enter a valid alphanumeric extension.")
                input("Press Enter to continue...")
                main()
            
            Extension.clear_screen()

            Log.Info(f"Converting to .{ext} ...")

            try:
                convert_dir = os.path.join(os.getcwd(), "convert")
                if not os.path.exists(convert_dir):
                    Log.Error(f"Convert folder not found: {convert_dir}")
                    input("Press Enter to continue...")
                    main()
                    
                files = [f for f in os.listdir(convert_dir) if os.path.isfile(os.path.join(convert_dir, f))]

                if not files:
                    Log.Error("No files found in convert folder!")
                    input("Press Enter to continue...")
                    main()

                for file in files:
                    input_file = os.path.join(convert_dir, file)
                    base, _ = os.path.splitext(file)
                    output_file = os.path.join(convert_dir, base + f".{ext}")
                    Extension.convert(input_file, output_file, codec=ext, bitrate="192k")

                    os.remove(input_file)
                    os.replace(output_file, os.path.join(os.getcwd(), "converted", base + f".{ext}"))

                    Log.Info(f"Converted: {file} -> {base + '.' + ext}")

                Log.Info("All files converted!")
                input("Press Enter to continue...")
                main()
                
            except Exception as e:
                Log.Error(f"Error: {str(e)}")
                input("Press Enter to continue...")
                main()

    except Exception as e:
        Log.Error(f"Error: {str(e)}")
        input("Press Enter to continue...")
        main()

if __name__ == "__main__":
    main()