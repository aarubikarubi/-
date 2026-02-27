import sys
import os
import time
import shutil
import psutil
import subprocess
import argparse
from PyQt6.QtWidgets import QApplication, QProgressDialog
from PyQt6.QtCore import Qt, QTimer

def main():
    parser = argparse.ArgumentParser(description="日課ツール Updater")
    parser.add_argument("--pid", type=int, required=True, help="Process ID of the main application to wait for")
    parser.add_argument("--src", type=str, required=True, help="Path to the downloaded new executable")
    parser.add_argument("--dst", type=str, required=True, help="Path to the current executable to overwrite")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    
    # シンプルなプログレスダイアログの表示
    progress = QProgressDialog("アップデートを適用中...", None, 0, 0)
    progress.setWindowTitle("日課ツール")
    progress.setWindowModality(Qt.WindowModality.WindowModal)
    progress.setCancelButton(None)
    progress.show()

    def process_update():
        try:
            # 1. メインプロセスの終了を待機
            try:
                proc = psutil.Process(args.pid)
                # 最大20秒待機
                proc.wait(timeout=20)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                pass
            
            # 安全のため追加で少し待つ（ファイルハンドルの解放待ち）
            time.sleep(1.5)

            # 2. ファイルを上書きコピー
            if os.path.exists(args.src):
                # バックアップファイルを残すオプションもあるが、今回はシンプルに上書き
                shutil.copy2(args.src, args.dst)
                
                # 一時ファイルを削除
                try:
                    os.remove(args.src)
                except Exception:
                    pass
                
            # 3. 新しい実行ファイルを起動
            subprocess.Popen([args.dst])
            
        except Exception as e:
            # エラー時はログを残す
            log_path = os.path.join(os.path.dirname(args.dst), "update_error.log")
            try:
                with open(log_path, "w", encoding="utf-8") as f:
                    f.write(f"Update failed: {e}")
            except:
                pass
        
        finally:
            app.quit()

    # UIを表示した直後にアップデート処理を開始
    QTimer.singleShot(100, process_update)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
