from get_dependencies import install_or_update_pyboy
from settings_ui import SettingsWindow
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import font
import subprocess
from pathlib import Path
import json
import os
from config import KEYBINDS


class GameBoyLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Boy ROM Launcher")
        self.root.geometry("1000x700")
        self.root.configure(bg='#C5C1C2')
        self.rom_directory = Path("roms")
        self.keybinds = KEYBINDS.copy()
        self.remapped_keys = {}
        self.open_windows = {}

        self.style = ttk.Style()
        self.style.configure('Hacker.TFrame', background='#C5C1C2')
        self.style.configure('Hacker.TButton',
                             background='#00FF00',
                             foreground='#C5C1C2',
                             font=('Courier', 12, 'bold'),
                             padding=10)
        self.style.configure('Hacker.TLabel',
                             background='#C5C1C2',
                             foreground='#21298C',
                             font=('Courier', 12))

        main_frame = ttk.Frame(root, padding="20", style='Hacker.TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        title_font = font.Font(family='Courier', size=24, weight='bold')
        title = tk.Label(main_frame,
                         text="GAME BOY LAUNCHER v1.0",
                         font=title_font,
                         fg='#21298C',
                         bg='#C5C1C2')
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        search_frame = ttk.Frame(main_frame, style='Hacker.TFrame')
        search_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        search_label = ttk.Label(search_frame, text="SEARCH:", style='Hacker.TLabel')
        search_label.pack(side=tk.LEFT, padx=(0, 10))

        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self.filter_games)
        search_entry = tk.Entry(search_frame,
                                textvariable=self.search_var,
                                font=('Courier', 12),
                                bg='#5D5A61',
                                fg='#C5C1C2',
                                insertbackground='#21298C',
                                relief=tk.FLAT,
                                width=50)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.stats_frame = ttk.Frame(main_frame, style='Hacker.TFrame')
        self.stats_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.stats_label = ttk.Label(self.stats_frame,
                                     text="LOADING ROMS...",
                                     style='Hacker.TLabel')
        self.stats_label.pack(side=tk.LEFT)

        self.listbox = tk.Listbox(main_frame,
                                  width=70,
                                  height=20,
                                  font=('Courier', 14, 'bold'),
                                  bg='#596708',
                                  fg='#21298C',
                                  selectmode=tk.SINGLE,
                                  selectbackground='#005500',
                                  selectforeground='#596708',
                                  relief=tk.FLAT)

        self.listbox.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        control_frame = ttk.Frame(main_frame, style='Hacker.TFrame')
        control_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)

        launch_button = tk.Button(control_frame,
                                  text=f"LAUNCH\nGAME",
                                  command=self.launch_game,
                                  font=('Courier', 14, 'bold'),
                                  bg='#a61257',
                                  fg='#000000',
                                  activebackground='#008800',
                                  activeforeground='#FFFFFF',
                                  relief=tk.RAISED,
                                  width=6,
                                  height=3,
                                  bd=5,
                                  highlightthickness=0)
        launch_button.pack(side=tk.RIGHT, padx=10)

        center_buttons_frame = tk.Frame(control_frame, bg='#C5C1C2')
        center_buttons_frame.pack(expand=True, padx=(80, 0))

        settings_frame = tk.Frame(center_buttons_frame, bg='#C5C1C2')
        settings_frame.pack(side=tk.LEFT, padx=10)

        power_button_frame = tk.Frame(center_buttons_frame, bg='#C5C1C2')
        power_button_frame.pack(side=tk.LEFT, padx=10)

        settings_button = tk.Button(settings_frame,
                                    width=10,
                                    height=1,
                                    font=('Courier', 8, 'bold'),
                                    relief=tk.RAISED,
                                    bg="grey",
                                    fg="#21298C",
                                    command=self.open_settings_window)
        settings_button.pack()

        settings_label = tk.Label(settings_frame,
                                  text="Settings",
                                  font=('Courier', 8, 'bold'),
                                  bg='#C5C1C2',
                                  fg="#21298C")
        settings_label.pack(pady=(5, 0))

        power_button = tk.Button(power_button_frame,
                                 width=10,
                                 height=1,
                                 font=('Courier', 8, 'bold'),
                                 relief=tk.RAISED,
                                 bg="grey",
                                 fg="#21298C",
                                 command=self.close_window)
        power_button.pack()

        power_label = tk.Label(power_button_frame,
                               text="Exit",
                               font=('Courier', 8, 'bold'),
                               bg='#C5C1C2',
                               fg="#21298C")
        power_label.pack(pady=(5, 0))

        self.status_var = tk.StringVar()
        self.status_var.set("SYSTEM READY")
        status_label = ttk.Label(main_frame,
                                 textvariable=self.status_var,
                                 style='Hacker.TLabel')
        status_label.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        self.listbox.bind('<Double-Button-1>', lambda e: self.launch_game())

        self.games = []
        self.load_games()

    def close_window(self):
        self.root.destroy()

    def open_settings_window(self):
        # Check if the settings window is already open
        if "settings" not in self.open_windows or not self.open_windows["settings"].top.winfo_exists():
            settings_window = SettingsWindow(self)
            self.open_windows["settings"] = settings_window  # Store the window

            # When the window is closed, remove it from open_windows
            def on_close():
                settings_window.top.destroy()
                if "settings" in self.open_windows:
                    del self.open_windows["settings"]

            settings_window.top.protocol("WM_DELETE_WINDOW", on_close)
        else:
            # Focus the existing window
            self.open_windows["settings"].top.lift()

    def load_games(self):
        self.games.clear()
        roms_dir = self.rom_directory
        if roms_dir.exists():
            for file in roms_dir.glob("*.gb"):
                self.games.append(file.name)
            self.games.sort()
            self.update_listbox()
            self.update_stats()

    def update_stats(self):
        self.stats_label.configure(text=f"AVAILABLE ROMS: {len(self.games)}")

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for game in self.games:
            game = game.replace('.gb', '')
            self.listbox.insert(tk.END, f" {game}")
        self.update_stats()

    def filter_games(self, *args):
        search_term = self.search_var.get().lower()
        self.listbox.delete(0, tk.END)
        for game in self.games:
            if search_term in game.lower():
                self.listbox.insert(tk.END, f" {game}")
        self.update_stats()

    def launch_game(self):
        """Launch the selected game with PyBoy"""
        selection = self.listbox.curselection()
        if selection:
            game = self.listbox.get(selection[0]).strip()
            # Remove .gb extension if it exists in the game name
            game = game.replace('.gb', '')
            rom_path = f"roms/{game}.gb"
            print(f"Attempting to launch game with path: {rom_path}")

            # Check if the ROM file exists
            if not os.path.exists(rom_path):
                print(f"Error: ROM file not found: {rom_path}")
                self.status_var.set("ROM NOT FOUND")
                return

            self.status_var.set(f"LAUNCHING {game.upper()}...")
            self.root.update()
            keybinds = json.dumps(self.keybinds)
            try:
                subprocess.Popen(["python", "-m", "pyboy", rom_path])
                # subprocess.Popen(["python", "-m", "pyboy", f"roms/{game}.gb", "-k", keybinds])
                self.status_var.set("SYSTEM READY")
            except Exception as e:
                print(f"Error launching game: {e}")
                self.status_var.set("LAUNCH FAILED")


if __name__ == "__main__":

    install_or_update_pyboy()
    root = tk.Tk()
    app = GameBoyLauncher(root)
    root.mainloop()


# some code snippets added by ai
