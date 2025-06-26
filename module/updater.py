import requests
import zipfile
import io
import os
import shutil
import sys
from module.logger import Log

GITHUB_API_URL = "https://api.github.com/repos/haruyq/ncdl_v5/releases/latest"

class AutoUpdater:
    @staticmethod
    def check_and_update(curr_version: str):
        try:
            Log.Info("Checking for updates...")
            response = requests.get(GITHUB_API_URL)
            response.raise_for_status()

            latest_release = response.json()
            latest_version = latest_release.get("tag_name", "v0.0.0").lstrip('v')

            Log.Info(f"Current version: {curr_version}, Latest version: {latest_version}")

            if tuple(map(int, curr_version.split('.'))) >= tuple(map(int, latest_version.split('.'))):
                return

            Log.Info("New version found. Starting update...")
            
            assets = latest_release.get("assets", [])
            if not assets:
                Log.Error("No assets found in the latest release.")
                return
            download_url = assets[0].get("browser_download_url")

            Log.Info(f"Downloading update from: {download_url}")
            zip_response = requests.get(download_url, stream=True)
            zip_response.raise_for_status()

            temp_extract_path = "temp_update"
            if os.path.exists(temp_extract_path):
                shutil.rmtree(temp_extract_path)
            
            Log.Info("Extracting update file...")
            with zipfile.ZipFile(io.BytesIO(zip_response.content)) as z:
                z.extractall(temp_extract_path)

            source_path = temp_extract_path
            extracted_items = os.listdir(temp_extract_path)
            if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_extract_path, extracted_items[0])):
                source_path = os.path.join(temp_extract_path, extracted_items[0])
                Log.Info(f"Detected nested folder. Using source: {source_path}")

            Log.Info(f"Copying files from: {source_path}")
            for item in os.listdir(source_path):
                s = os.path.join(source_path, item)
                d = os.path.join(os.getcwd(), item)
                
                if os.path.isdir(s):
                    if os.path.exists(d):
                        shutil.rmtree(d)
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)
            
            shutil.rmtree(temp_extract_path)
            Log.Info("Files updated successfully.")

            if os.path.exists("requirements.txt"):
                Log.Info("Updating requirements...")
                os.system(f'"{sys.executable}" -m pip install --upgrade -r requirements.txt')

            Log.Info("Update complete. Restarting application...")
            os.execv(sys.executable, ['python'] + sys.argv)
        
        except requests.exceptions.RequestException as e:
            Log.Error(f"Update check failed (network error): {e}")
        except Exception as e:
            Log.Error(f"An unexpected error occurred during the update process: {e}", exc_info=True)
            input("Press Enter to continue...")