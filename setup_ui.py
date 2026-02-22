import customtkinter as ctk
from tkinter import filedialog, messagebox
import json
import os
import sys
import winreg

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class GameSetupApp(ctk.CTk):
    def __init__(self, config_path="config.json", on_close_callback=None, monitor=None):
        super().__init__()
        self.config_path = config_path
        self.on_close_callback = on_close_callback
        self.monitor = monitor
        
        self.title("日課連鎖ランチャー 登録設定")
        self.geometry("900x600")
        self.minsize(700, 500)
        
        self.games = []
        self.launch_interval = 5
        self.kill_targets = []
        self.run_on_startup = False
        
        self.current_selected_index = None # None means App Settings is selected
        self.load_config()
        
        self.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.create_sidebar()
        self.create_main_frame()
        self.refresh_sidebar_list()
        self.select_app_settings()

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.games = config.get("games", [])
                    self.launch_interval = config.get("launch_interval", 5)
                    loaded_kills = config.get("kill_targets", [])
                    # pad to 3 items
                    self.kill_targets = (loaded_kills + ["なし", "なし", "なし"])[:3]
                    self.run_on_startup = config.get("run_on_startup", False)
                self.auto_exit = config.get("auto_exit_after_completion", False)
                if self.monitor:
                    self.monitor.auto_exit_after_completion = self.auto_exit
            except Exception as e:
                print(f"Failed to load config: {e}")

    def set_run_on_startup(self, enable):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "DailyGameLauncher"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
            if enable:
                exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{exe_path}" --startup')
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Failed to set startup registry: {e}")

    def save_config(self):
        try:
            # save app settings
            try:
                self.launch_interval = int(self.interval_var.get())
            except ValueError:
                self.launch_interval = 5
            
            self.kill_targets = [
                self.kill_combo_1.get(),
                self.kill_combo_2.get(),
                self.kill_combo_3.get()
            ]
            self.run_on_startup = bool(self.startup_var.get())
            self.auto_exit = bool(self.auto_exit_var.get())
            
            config_data = {
                "games": self.games,
                "launch_interval": self.launch_interval,
                "kill_targets": self.kill_targets,
                "run_on_startup": self.run_on_startup,
                "auto_exit_after_completion": self.auto_exit
            }
            
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            if self.monitor:
                self.monitor.auto_exit_after_completion = self.auto_exit
                
            self.set_run_on_startup(self.run_on_startup)
            return True
        except Exception as e:
            messagebox.showerror("エラー", f"設定の保存に失敗しました: {e}")
            return False

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(3, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="設定メニュー", font=ctk.CTkFont(size=18, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # App Settings Button
        self.app_settings_btn = ctk.CTkButton(self.sidebar_frame, text="⚙ アプリ全体設定", fg_color="transparent", 
                                              text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                              anchor="w", command=self.select_app_settings)
        self.app_settings_btn.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        # Game List Label
        self.games_label = ctk.CTkLabel(self.sidebar_frame, text="ゲームプロファイル", text_color="gray", font=ctk.CTkFont(size=12))
        self.games_label.grid(row=2, column=0, padx=20, pady=(15, 0), sticky="w")
        
        self.game_list_frame = ctk.CTkScrollableFrame(self.sidebar_frame, fg_color="transparent")
        self.game_list_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)
        
        self.sidebar_btn_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.sidebar_btn_frame.grid(row=4, column=0, padx=20, pady=20, sticky="s")
        
        self.add_new_btn = ctk.CTkButton(self.sidebar_btn_frame, text="+ 追加", width=100, command=self.add_new_profile)
        self.add_new_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.delete_btn = ctk.CTkButton(self.sidebar_btn_frame, text="🗑 削除", width=100, fg_color="#d32f2f", hover_color="#b71c1c", command=self.delete_current_profile)
        self.delete_btn.grid(row=0, column=1, padx=(5, 0))

    def create_main_frame(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)
        
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        self.profile_title = ctk.CTkLabel(self.header_frame, text="アプリ全体設定", font=ctk.CTkFont(size=24, weight="bold"))
        self.profile_title.grid(row=0, column=0, sticky="w")
        
        self.save_btn = ctk.CTkButton(self.header_frame, text="保存して適用", command=self.save_and_close)
        self.save_btn.grid(row=0, column=1, sticky="e")

        # Container for Profile and App Settings views
        self.content_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_container.grid(row=1, column=0, sticky="nsew")
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)
        
        self.create_app_settings_view()
        self.create_profile_view()

    def create_app_settings_view(self):
        self.app_settings_view = ctk.CTkFrame(self.content_container, corner_radius=15)
        self.app_settings_view.grid(row=0, column=0, sticky="nsew")
        self.app_settings_view.grid_columnconfigure(1, weight=1)
        
        # Interval
        lbl = ctk.CTkLabel(self.app_settings_view, text="次のゲームを開くまでの待ち時間 (秒):\n※PCのカクつきを防ぐための準備時間です", font=ctk.CTkFont(weight="bold"))
        lbl.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        self.interval_var = ctk.StringVar(value=str(self.launch_interval))
        entry = ctk.CTkEntry(self.app_settings_view, textvariable=self.interval_var, width=100)
        entry.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="w")
        
        # Kill targets
        lbl2 = ctk.CTkLabel(self.app_settings_view, text="一緒に閉じる裏方アプリ\n(ゲーム終了に合わせて閉じます):", font=ctk.CTkFont(weight="bold"))
        lbl2.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.kill_targets_frame = ctk.CTkFrame(self.app_settings_view, fg_color="transparent")
        self.kill_targets_frame.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        
        kill_options = ["なし", "HoYoPlay (hoyoplay.exe)", "Steam (steam.exe)", "Epic Games (EpicGamesLauncher.exe)"]
        
        self.kill_combo_1 = ctk.CTkComboBox(self.kill_targets_frame, values=kill_options, width=250)
        self.kill_combo_1.grid(row=0, column=0, pady=5)
        self.kill_combo_1.set(self.kill_targets[0] if len(self.kill_targets) > 0 else "なし")
        
        self.kill_combo_2 = ctk.CTkComboBox(self.kill_targets_frame, values=kill_options, width=250)
        self.kill_combo_2.grid(row=1, column=0, pady=5)
        self.kill_combo_2.set(self.kill_targets[1] if len(self.kill_targets) > 1 else "なし")
        
        self.kill_combo_3 = ctk.CTkComboBox(self.kill_targets_frame, values=kill_options, width=250)
        self.kill_combo_3.grid(row=2, column=0, pady=5)
        self.kill_combo_3.set(self.kill_targets[2] if len(self.kill_targets) > 2 else "なし")
        
        # Startup option
        self.startup_var = ctk.CTkLabel(self.app_settings_view, text="スタートアップ設定:", font=ctk.CTkFont(weight="bold", size=16)) # This was a mistake in my thought, let me fix properly.
        # Let's just fix the indentation of the previously messy block.
        self.startup_var = ctk.BooleanVar(value=self.run_on_startup)
        chk = ctk.CTkSwitch(self.app_settings_view, text="PC起動時に自動で開始する", variable=self.startup_var)
        chk.grid(row=3, column=0, columnspan=2, padx=40, pady=5, sticky="w")
        
        # Auto-Exit option
        self.auto_exit_var = ctk.BooleanVar(value=getattr(self, 'auto_exit', False))
        chk2 = ctk.CTkSwitch(self.app_settings_view, text="日課完了後にこのツールを自動終了する", variable=self.auto_exit_var)
        chk2.grid(row=4, column=0, columnspan=2, padx=40, pady=5, sticky="w")
        
        # Start Routine Button
        self.start_routine_btn = ctk.CTkButton(self.app_settings_view, text="▶ 日課を開始 (1番目のゲームを起動)", 
                                               font=ctk.CTkFont(weight="bold"), fg_color="#1976d2", hover_color="#1565c0",
                                               command=self.action_start_routine)
        self.start_routine_btn.grid(row=5, column=0, columnspan=2, padx=40, pady=(20, 10), sticky="w")
        
        # Reset Profiles Button
        self.reset_all_btn = ctk.CTkButton(self.app_settings_view, text="❌ すべてのゲームをリセット", 
                                           font=ctk.CTkFont(weight="bold"), fg_color="#c62828", hover_color="#b71c1c",
                                           command=self.action_reset_all)
        self.reset_all_btn.grid(row=6, column=0, columnspan=2, padx=40, pady=10, sticky="w")

    def create_profile_view(self):
        self.profile_view = ctk.CTkFrame(self.content_container, corner_radius=15)
        self.profile_view.grid(row=0, column=0, sticky="nsew")
        self.profile_view.grid_columnconfigure(1, weight=1)
        
        # Header with Step Number
        self.header_row = ctk.CTkFrame(self.profile_view, fg_color="transparent")
        self.header_row.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 5), sticky="ew")
        self.header_row.grid_columnconfigure(0, weight=1)
        
        self.step_label = ctk.CTkLabel(self.header_row, text="No. 1", font=ctk.CTkFont(size=14, weight="bold"), 
                                       fg_color="#1a73e8", text_color="white", corner_radius=10, width=80)
        self.step_label.grid(row=0, column=0, sticky="w")
        
        # Name Input
        self.name_label = ctk.CTkLabel(self.profile_view, text="ゲーム表示名:", font=ctk.CTkFont(weight="bold"))
        self.name_label.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")
        
        self.name_input_frame = ctk.CTkFrame(self.profile_view, fg_color="transparent")
        self.name_input_frame.grid(row=1, column=1, padx=20, pady=(10, 5), sticky="w")
        
        self.name_var = ctk.StringVar()
        self.name_entry = ctk.CTkEntry(self.name_input_frame, textvariable=self.name_var, width=200)
        self.name_entry.grid(row=0, column=0, sticky="w")
        self.name_entry.bind("<KeyRelease>", self.on_entry_change)
        
        def preset_selected(choice):
            if choice != "プリセット...":
                self.name_var.set(choice)
                self.on_entry_change()
                self.preset_menu.set("プリセット...")
                
        self.preset_menu = ctk.CTkOptionMenu(self.name_input_frame, values=["プリセット...", "原神", "崩壊：スターレイル", "鳴潮"], 
                                             command=preset_selected, width=110, fg_color="#37474f", button_color="#37474f")
        self.preset_menu.grid(row=0, column=1, padx=(10, 0))
        
        # Process Input
        self.process_label = ctk.CTkLabel(self.profile_view, text="プロセス名 (例: Game.exe):", font=ctk.CTkFont(weight="bold"))
        self.process_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        self.process_var = ctk.StringVar()
        self.process_entry = ctk.CTkEntry(self.profile_view, textvariable=self.process_var, width=300)
        self.process_entry.grid(row=2, column=1, padx=20, pady=5, sticky="w")
        self.process_entry.bind("<KeyRelease>", self.on_entry_change)
        
        # Path Input
        self.path_label = ctk.CTkLabel(self.profile_view, text="実行ファイルパス:", font=ctk.CTkFont(weight="bold"))
        self.path_label.grid(row=3, column=0, padx=20, pady=(10, 15), sticky="w")
        
        self.path_var = ctk.StringVar()
        self.path_entry_frame = ctk.CTkFrame(self.profile_view, fg_color="transparent")
        self.path_entry_frame.grid(row=3, column=1, padx=20, pady=(10, 15), sticky="ew")
        self.path_entry_frame.grid_columnconfigure(0, weight=1)
        
        self.path_entry = ctk.CTkEntry(self.path_entry_frame, textvariable=self.path_var)
        self.path_entry.grid(row=0, column=0, sticky="ew")
        self.path_entry.bind("<KeyRelease>", self.on_entry_change)
        
        self.browse_btn = ctk.CTkButton(self.path_entry_frame, text="参照...", width=60, command=self.browse_file)
        self.browse_btn.grid(row=0, column=1, padx=(10, 5))
        
        self.detect_btn = ctk.CTkButton(self.path_entry_frame, text="✨自動検出", width=80, fg_color="#fbc02d", text_color="black", hover_color="#f9a825", command=self.auto_detect_path)
        self.detect_btn.grid(row=0, column=2)

        # Order Control Buttons (Up/Down)
        self.order_frame = ctk.CTkFrame(self.profile_view, fg_color="transparent")
        self.order_frame.grid(row=4, column=0, columnspan=2, padx=20, pady=(10, 15), sticky="w")
        
        self.up_btn = ctk.CTkButton(self.order_frame, text="↑ 順番を上げる", width=120, fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"), command=self.move_up)
        self.up_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.down_btn = ctk.CTkButton(self.order_frame, text="↓ 順番を下げる", width=120, fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"), command=self.move_down)
        self.down_btn.grid(row=0, column=1)

        # Separator Line for better spacing
        self.sep = ctk.CTkFrame(self.profile_view, height=2, fg_color=("gray85", "gray30"))
        self.sep.grid(row=5, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

        # Single Launch Controls
        self.launch_ctrl_frame = ctk.CTkFrame(self.profile_view, fg_color="transparent")
        self.launch_ctrl_frame.grid(row=6, column=0, columnspan=2, padx=20, pady=5, sticky="w")
        
        self.launch_btn = ctk.CTkButton(self.launch_ctrl_frame, text="▶ このゲームを起動", fg_color="#2e7d32", hover_color="#1b5e20", font=ctk.CTkFont(weight="bold"), command=self.action_launch_current)
        self.launch_btn.grid(row=0, column=0, padx=(0, 20))
        
        self.chain_launch_var = ctk.BooleanVar(value=True)
        self.chain_launch_chk = ctk.CTkSwitch(self.launch_ctrl_frame, text="連続プレイモード (終了後に次のゲームへ)", variable=self.chain_launch_var)
        self.chain_launch_chk.grid(row=0, column=1)

    def refresh_sidebar_list(self):
        for widget in self.game_list_frame.winfo_children():
            widget.destroy()
            
        self.sidebar_buttons = []
        for i, game in enumerate(self.games):
            name = game.get("name", "New Game") or "無題のゲーム"
            btn_text = f"{i+1}. {name}"
            btn = ctk.CTkButton(self.game_list_frame, text=btn_text, fg_color="transparent", 
                                text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                anchor="w", command=lambda idx=i: self.select_profile(idx))
            btn.pack(fill="x", pady=2)
            self.sidebar_buttons.append(btn)
            
        self.highlight_selected_button()

    def highlight_selected_button(self):
        if self.current_selected_index is None:
            self.app_settings_btn.configure(fg_color=("gray60", "gray25"))
            for btn in self.sidebar_buttons:
                btn.configure(fg_color="transparent")
            return
            
        self.app_settings_btn.configure(fg_color="transparent")
        
        for i, btn in enumerate(self.sidebar_buttons):
            if i == self.current_selected_index:
                btn.configure(fg_color=("gray60", "gray25"))
            else:
                btn.configure(fg_color="transparent")

    def select_app_settings(self):
        self.current_selected_index = None
        self.highlight_selected_button()
        self.profile_title.configure(text="アプリ全体設定")
        self.profile_view.grid_remove()
        self.app_settings_view.grid()
        self.delete_btn.configure(state="disabled")

    def select_profile(self, index):
        self.current_selected_index = index
        self.highlight_selected_button()
        
        game = self.games[index]
        self.name_var.set(game.get("name", ""))
        self.process_var.set(game.get("process_name", ""))
        self.path_var.set(game.get("path", ""))
        
        self.step_label.configure(text=f"No. {index + 1}")
        
        self.profile_title.configure(text=f"プロファイル: {game.get('name', '新規プロファイル')}")
        self.app_settings_view.grid_remove()
        self.profile_view.grid()
        self.delete_btn.configure(state="normal")

    def add_new_profile(self):
        new_game = {
            "name": "新規プロファイル",
            "process_name": "",
            "path": ""
        }
        self.games.append(new_game)
        self.refresh_sidebar_list()
        self.select_profile(len(self.games) - 1)

    def delete_current_profile(self):
        if self.current_selected_index is not None:
            del self.games[self.current_selected_index]
            self.refresh_sidebar_list()
            self.select_app_settings()

    def on_entry_change(self, event=None):
        if self.current_selected_index is not None:
            self.games[self.current_selected_index]["name"] = self.name_var.get()
            self.games[self.current_selected_index]["process_name"] = self.process_var.get()
            self.games[self.current_selected_index]["path"] = self.path_var.get()
            
            new_title = self.name_var.get() or "無題のゲーム"
            self.profile_title.configure(text=f"プロファイル: {new_title}")
            if self.current_selected_index < len(self.sidebar_buttons):
                self.sidebar_buttons[self.current_selected_index].configure(text=f"{self.current_selected_index+1}. {new_title}")

    def auto_detect_path(self):
        if self.current_selected_index is None: return
        
        current_name = self.name_var.get().strip()
        if not current_name or current_name == "新規プロファイル" or current_name == "無題のゲーム":
            messagebox.showwarning("エラー", "ゲーム表示名を入力するか、プリセットから選んでから「自動検出」を押してください。")
            return
            
        # Keyword Aliasing
        target_keywords = []
        target_exe = ""
        
        if "スターレイル" in current_name or "star rail" in current_name.lower():
            target_keywords = ["Star Rail", "スターレイル", "崩壊：スターレイル"]
            target_exe = "StarRail.exe"
        elif "原神" in current_name or "genshin" in current_name.lower():
            target_keywords = ["Genshin", "原神"]
            target_exe = "GenshinImpact.exe"
        elif "鳴潮" in current_name or "wuthering" in current_name.lower() or "wuwa" in current_name.lower():
            target_keywords = ["Wuthering", "鳴潮", "Wuthering Waves"]
            target_exe = "Wuthering Waves.exe"
        else:
            # If the user typed something else, we try to use it as a generic keyword
            target_keywords = [current_name]
            target_exe = current_name + ".exe"

        found_path = None
        
        # Search common registry uninstall locations (Exclude HKCU to save time based on user feedback)
        reg_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall")
        ]
        
        try:
            for root, key_path in reg_paths:
                try:
                    with winreg.OpenKey(root, key_path) as uninstall_key:
                        num_subkeys = winreg.QueryInfoKey(uninstall_key)[0]
                        for i in range(num_subkeys):
                            try:
                                subkey_name = winreg.EnumKey(uninstall_key, i)
                                with winreg.OpenKey(uninstall_key, subkey_name) as app_key:
                                    try:
                                        display_name = winreg.QueryValueEx(app_key, "DisplayName")[0]
                                        if any(keyword.lower() in display_name.lower() for keyword in target_keywords):
                                            # found a match
                                            install_loc = winreg.QueryValueEx(app_key, "InstallLocation")[0]
                                            
                                            # Depth-limited Search
                                            def find_exe_in_dir(base_dir, target_exe, max_depth=3):
                                                if not os.path.exists(base_dir): return None
                                                base_dir = os.path.abspath(base_dir)
                                                
                                                for root_dir, dirs, files in os.walk(base_dir):
                                                    # Calculate current depth relative to base_dir
                                                    rel_path = os.path.relpath(root_dir, base_dir)
                                                    current_depth = len(rel_path.split(os.sep)) if rel_path != '.' else 0
                                                    
                                                    if current_depth > max_depth:
                                                        dirs.clear() # Stop digging deeper for this branch
                                                        continue
                                                        
                                                    # optimize: skip cache/logs/temp to speed up
                                                    dirs[:] = [d for d in dirs if d.lower() not in ["cache", "logs", "temp", "plugins"]]
                                                    
                                                    # Perform case-insensitive check
                                                    for f in files:
                                                        if f.lower() == target_exe.lower():
                                                            return os.path.join(root_dir, f)
                                                return None

                                            found_path = find_exe_in_dir(install_loc, target_exe)
                                            
                                            # Fallback: if user specified a random game, look for any .exe
                                            if not found_path and target_exe == current_name + ".exe":
                                                if os.path.exists(install_loc):
                                                    for file_name in os.listdir(install_loc):
                                                        if file_name.endswith(".exe") and "unins" not in file_name.lower():
                                                            found_path = os.path.join(install_loc, file_name)
                                                            break
                                                
                                            if found_path and os.path.exists(found_path):
                                                break
                                    except OSError:
                                        continue
                            except OSError:
                                continue
                except OSError:
                    continue
                if found_path: break
        except Exception as e:
            print(f"Registry search error: {e}")
            
        # Fallback: Check Cognosphere specific registry keys
        if not found_path or not os.path.exists(found_path):
            if "StarRail.exe" in target_exe or "GenshinImpact.exe" in target_exe:
                cg_reg_paths = [
                    (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Cognosphere\Star Rail"),
                    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Cognosphere\Star Rail"),
                    (winreg.HKEY_CURRENT_USER, r"SOFTWARE\miHoYo\Genshin Impact"),
                    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\miHoYo\Genshin Impact")
                ]
                try:
                    for root, key_path in cg_reg_paths:
                        try:
                            with winreg.OpenKey(root, key_path) as app_key:
                                # We try to extract info from arbitrary values just in case
                                num_values = winreg.QueryInfoKey(app_key)[1]
                                for i in range(num_values):
                                    val_name, val_data, val_type = winreg.EnumValue(app_key, i)
                                    if type(val_data) == bytes:
                                        val_data = val_data.decode('utf-8', errors='ignore')
                                    if type(val_data) == str and (target_exe.lower() in val_data.lower() or "star rail" in val_data.lower() or "genshin impact" in val_data.lower()):
                                        # found a hint of path in registry. Try to build it out
                                        if "://" not in val_data: # exclude URLs
                                            # Simple heuristic to extract drive path
                                            idx = val_data.find(":\\")
                                            if idx > 0:
                                                possible_path = val_data[idx-1:]
                                                # trim nulls and extras
                                                possible_path = possible_path.split('\x00')[0]
                                                if os.path.isdir(possible_path):
                                                    if os.path.exists(os.path.join(possible_path, target_exe)):
                                                        found_path = os.path.join(possible_path, target_exe)
                                                        break
                                        if found_path: break
                        except OSError:
                            continue
                        if found_path: break
                except Exception as e:
                    print(f"Cognosphere registry search error: {e}")
            
        # Fallback: Static Common Paths List
        if not found_path or not os.path.exists(found_path):
            common_static_paths = [
                rf"C:\Program Files\{target_exe.replace('.exe', '')}\Games\{target_exe}",
                rf"C:\Program Files\HoYoPlay\games\{target_exe.replace('.exe', '')}\Games\{target_exe}",
                rf"D:\Program Files\{target_exe.replace('.exe', '')}\Games\{target_exe}",
                rf"D:\Program Files\HoYoPlay\games\{target_exe.replace('.exe', '')}\Games\{target_exe}",
                rf"D:\{target_exe.replace('.exe', '')} Games\{target_exe}",
                rf"D:\HoYoPlay\games\{target_exe.replace('.exe', '')}\Games\{target_exe}",
                rf"C:\Program Files\Genshin Impact\Genshin Impact game\GenshinImpact.exe",
                rf"D:\Genshin Impact\Genshin Impact game\GenshinImpact.exe",
                rf"C:\Program Files\Wuthering Waves\Wuthering Waves Game\Wuthering Waves.exe",
                rf"D:\Wuthering Waves\Wuthering Waves Game\Wuthering Waves.exe",
            ]
            
            # Specific alias fix for Star Rail common path names
            if "StarRail.exe" in target_exe:
                common_static_paths.extend([
                    r"C:\Program Files\Star Rail\Games\StarRail.exe",
                    r"D:\Star Rail\Games\StarRail.exe",
                    r"C:\Star Rail\Games\StarRail.exe",
                    r"D:\Star Rail Games\StarRail.exe",
                    r"C:\Star Rail Games\StarRail.exe",
                    r"D:\HoYoPlay\games\Star Rail game\Games\StarRail.exe",
                    r"C:\Program Files\HoYoPlay\games\Star Rail game\Games\StarRail.exe"
                ])
                
            for static_path in common_static_paths:
                if os.path.exists(static_path) and target_exe.lower() in static_path.lower():
                    found_path = static_path
                    break

        if not found_path or not os.path.exists(found_path):
            messagebox.showinfo("検出失敗", f"「{current_name}」の一般的なインストール先が見つかりませんでした。\n手動で「参照...」から選択してください。")
            return
            
        # Update UI
        self.path_var.set(found_path.replace("/", "\\"))
        self.process_var.set(os.path.basename(found_path))
        self.on_entry_change()
        messagebox.showinfo("検出成功", f"「{current_name}」のファイルロケーションを自動検出しました！")

    def browse_file(self):
        if self.current_selected_index is None: return
        
        filename = filedialog.askopenfilename(
            title="実行ファイルを選択",
            filetypes=(("Executable files", "*.exe"), ("All files", "*.*"))
        )
        if filename:
            filename = filename.replace("/", "\\")
            self.path_var.set(filename)
            
            basename = os.path.basename(filename)
            self.process_var.set(basename)
            
            if not self.name_var.get() or self.name_var.get() == "新規プロファイル":
                name = os.path.splitext(basename)[0]
                self.name_var.set(name)
                
            self.on_entry_change()

    def move_up(self):
        idx = self.current_selected_index
        if idx is not None and idx > 0:
            self.games[idx-1], self.games[idx] = self.games[idx], self.games[idx-1]
            self.current_selected_index = idx - 1
            self.refresh_sidebar_list()
            self.select_profile(self.current_selected_index)

    def move_down(self):
        idx = self.current_selected_index
        if idx is not None and idx < len(self.games) - 1:
            self.games[idx+1], self.games[idx] = self.games[idx], self.games[idx+1]
            self.current_selected_index = idx + 1
            self.refresh_sidebar_list()
            self.select_profile(self.current_selected_index)

    def save_and_close(self):
        for game in self.games:
            if not game.get("name") or not game.get("process_name") or not game.get("path"):
                messagebox.showwarning("入力エラー", "未入力の項目があるプロファイルが存在します。\nすべて入力するか削除してください。")
                return
                
        if self.save_config():
            if self.on_close_callback:
                self.on_close_callback()
            self.hide_window()

    def hide_window(self):
        self.withdraw()

    def action_start_routine(self):
        if self.monitor and self.games:
            self.monitor.start_specific_game(0, chain_launch=True)
            self.hide_window()
        elif not self.games:
            messagebox.showwarning("エラー", "ゲームが登録されていません。")
            
    def action_reset_all(self):
        if not self.games:
            messagebox.showinfo("情報", "すでにゲームプロファイルは登録されていません。")
            return
            
        confirm = messagebox.askyesno("リセットの確認", "すべてのゲームプロファイルを削除して初期状態に戻します。\n本当によろしいですか？")
        if confirm:
            self.games = []
            self.refresh_sidebar_list()
            self.select_app_settings()
            self.save_config()
            messagebox.showinfo("完了", "すべてのプロファイルをリセットしました。")

    def action_launch_current(self):
        if self.current_selected_index is not None and self.monitor:
            path = self.games[self.current_selected_index].get("path")
            if not path or not os.path.exists(path):
                messagebox.showerror("エラー", "正しい実行ファイルパスが設定されていません。\n手動で「参照...」または「自動検出」から設定してください。")
                return
            
            chain = self.chain_launch_var.get()
            success, msg = self.monitor.start_specific_game(self.current_selected_index, chain_launch=chain)
            
            if success:
                self.hide_window()
            else:
                messagebox.showerror("起動失敗", f"ゲームの起動に失敗しました:\n{msg}")

    def show_window(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def quit_app(self):
        self.destroy()

if __name__ == "__main__":
    app = GameSetupApp("config.json", None)
    app.mainloop()
