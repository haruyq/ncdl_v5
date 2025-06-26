import requests
import zipfile
import io
import os
import shutil
import sys
from module.logger import Log

LATEST = "https://api.github.com/repos/haruyq/ncdl_v5/releases/latest"

class AutoUpdater:
    @staticmethod
    def check_updates(curr_version: str) -> tuple:
        """
        GithubのAPIから最新バージョンがあるか確認する関数
        """
        try:
            response = requests.get(LATEST)
            response.raise_for_status()
            if response.status_code == 200:
                github_data = response.json()
                latest_version = github_data["tag_name"]
                if str(latest_version).lstrip('v') != curr_version:
                    return True
                else:
                    return False
            
            else:
                return
        
        except Exception as e:
            Log.Error("Update Error: \n" + e)
    
    @staticmethod
    def update():
        """
        自動アップデートを行う関数
        """
        try:
            response = requests.get(LATEST)
            response.raise_for_status()
            if response.status_code == 200:
                latest_release = response.json()
                download_url = latest_release["assets"][0]["browser_download_url"]

                Log.Info("Update Download: " + download_url)
                zip_response = requests.get(download_url, stream=True)
                zip_response.raise_for_status()

                with zipfile.ZipFile(io.BytesIO(zip_response.content)) as z:
                    root_dir = z.namelist()[0]
                    temp_extract_path = "temp_update"
                    z.extractall(temp_extract_path)

                source_path = os.path.join(temp_extract_path, root_dir)
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

                if os.path.exists("requirements.txt"):
                    Log.Info("Update: requirements.txt")
                    os.system(f"{sys.executable} -m pip install --upgrade --force-reinstall -r requirements.txt")

                Log.Info("Update completed. restarting...")
                os.execv(sys.executable, ['python'] + sys.argv)
            else:
                return False
            
        except Exception as e:
            Log.Error("Update Error: \n" + e)
            return False