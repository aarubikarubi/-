import urllib.request
import json
import os
import sys
import tempfile
import subprocess
from PyQt6.QtWidgets import QMessageBox

CURRENT_VERSION = "v2.1.0"
GITHUB_REPO = "aarubikarubi/DailyGameLauncher"

def check_and_apply_updates(parent_widget=None):
    """GitHub APIをチェックしてアップデートがあればプロンプトし、適用する"""
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(url, headers={'User-Agent': 'DailyGameLauncher-Updater'})
        
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                latest_version = data.get("tag_name", "")
                
                # バージョンが異なる場合はアップデートがあるとみなす
                if latest_version and latest_version != CURRENT_VERSION:
                    assets = data.get("assets", [])
                    download_url = None
                    for asset in assets:
                        if asset["name"].endswith(".exe") and "updater" not in asset["name"].lower():
                            download_url = asset["browser_download_url"]
                            break
                            
                    if download_url:
                        prompt_update(latest_version, download_url, parent_widget)
    except Exception as e:
        print(f"Update check failed: {e}")

def prompt_update(latest_version, download_url, parent_widget):
    reply = QMessageBox.question(
        parent_widget,
        "アップデート通知",
        f"新しいバージョン ({latest_version}) が利用可能です。\n今すぐアップデートしますか？",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.Yes
    )
    
    if reply == QMessageBox.StandardButton.Yes:
        perform_update(download_url, parent_widget)

def perform_update(download_url, parent_widget):
    QMessageBox.information(
        parent_widget,
        "ダウンロード開始",
        "アップデートファイルのダウンロードを開始します...\n完了するまでしばらくお待ちください。"
    )
    
    try:
        # ダウンロード先の一時ファイル
        temp_dir = tempfile.gettempdir()
        temp_exe = os.path.join(temp_dir, "DailyGameLauncher_update.exe")
        
        # ダウンロード実行
        urllib.request.urlretrieve(download_url, temp_exe)
        
        # updaterの起動準備
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        if getattr(sys, 'frozen', False):
            # PyInstallerでビルドされた本番環境
            current_exe = sys.executable
            updater_exe = os.path.join(base_dir, "updater.exe")
            cmd = [updater_exe]
        else:
            # 開発環境
            current_exe = os.path.abspath(sys.argv[0])
            updater_py = os.path.join(base_dir, "updater.py")
            cmd = [sys.executable, updater_py]
            
        current_pid = os.getpid()
        
        # 引数組み立て: updater.exe --pid <PID> --src <TEMP> --dst <CURRENT>
        cmd.extend([
            "--pid", str(current_pid),
            "--src", temp_exe,
            "--dst", current_exe
        ])
        
        print(f"Starting updater: {cmd}")
        subprocess.Popen(cmd)
        
        # メインアプリを即座に終了
        sys.exit(0)
        
    except Exception as e:
        QMessageBox.critical(
            parent_widget,
            "エラー",
            f"アップデートのダウンロード中にエラーが発生しました:\n{e}"
        )
