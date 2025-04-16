import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from keybinds_window import KeybindsConfig


class SettingsWindow:
    def __init__(self, launcher, opt_to_func=None):
        self.launcher = launcher
        self.top = tk.Toplevel(launcher.root)
        self.top.title("Settings")
        self.top.configure(bg='#C5C1C2')

        title = tk.Label(self.top,
                         text="Settings",
                         font=("Courier", 16, "bold"),
                         bg='#C5C1C2',
                         fg="#21298C")
        title.pack(pady=20)

        options = [
            "Change Keybindings",
            "Change ROM Directory",
            # "Toggle Screen Recording",
        ]

        # Get the position of the parent window
        parent_x = self.launcher.root.winfo_x()
        parent_y = self.launcher.root.winfo_y()

        # Adjust the window position based on the parent window's position
        offset_x = 30  # Offset from the parent window's left edge
        offset_y = 30  # Offset from the parent window's top edge

        # Set the size and position of the SettingsWindow relative to the parent window
        window_height = 100 + len(options) * 50
        self.top.geometry(f"400x{window_height}+{parent_x + offset_x}+{parent_y + offset_y}")

        # Create buttons and pack them
        for opt in options:
            opt_to_func = opt.lower().replace(" ", "_")
            opt_btn = tk.Button(self.top,
                                text=opt,
                                font=("Courier", 10, "bold"),
                                bg="grey",
                                fg="black",
                                width=30,
                                height=2,
                                command=lambda opt_to_func=opt_to_func: getattr(self, opt_to_func)())
            opt_btn.pack(pady=5)

    def change_keybindings(self):
        if "keybinds" not in self.launcher.open_windows or not self.launcher.open_windows["keybinds"].top.winfo_exists():
            keybinds_window = KeybindsConfig(self.launcher.root, self.launcher.keybinds)
            self.launcher.open_windows["keybinds"] = keybinds_window

            def on_close():
                keybinds_window.top.destroy()
                if "keybinds" in self.launcher.open_windows:
                    del self.launcher.open_windows["keybinds"]

            keybinds_window.top.protocol("WM_DELETE_WINDOW", on_close)
        else:
            self.launcher.open_windows["keybinds"].top.lift()

    def change_rom_directory(self):
        directory = filedialog.askdirectory(title="Select a Directory")
        if directory:
            self.launcher.rom_directory = Path(directory)
            self.launcher.load_games()
