"""Niny's small local desktop home. Run with Python or Launch Niny.vbs."""

from pathlib import Path
import math
import json
import os
import tempfile
import tkinter as tk
from tkinter import messagebox


MOODS = ("Curious", "Happy", "Playful", "Excited", "Sleepy", "Focus")
MESSAGES = {
    "Curious": "What's that? Niny is curious!",
    "Happy": "Niny is happy! 💜",
    "Playful": "Niny wants to play! 💜",
    "Excited": "Niny is excited to see you! 💜",
    "Sleepy": "Niny curls up in a fluffy tail-hug. 💜",
    "Focus": "Niny quietly keeps you company. 💜",
}


def preferences_path():
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return base / "Niny" / "preferences.json"


def load_preferences(path):
    defaults = {"stay_on_top": False, "idle_motion": True}
    try:
        saved = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return defaults
    if isinstance(saved, dict):
        for key in defaults:
            if type(saved.get(key)) is bool:
                defaults[key] = saved[key]
    return defaults


def save_preferences(path, settings):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                         dir=path.parent, delete=False) as file:
            temporary = Path(file.name)
            json.dump(settings, file, indent=2)
            file.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


class Niny:
    def __init__(self, root, preference_path=None):
        self.root = root
        self.preference_path = preference_path if preference_path is not None else preferences_path()
        settings = load_preferences(self.preference_path)
        self.mood_index = 0
        self.image = None
        self.idle_phase = 0
        self.heart_timer = None
        self.drag_origin = None
        self.dragged = False
        root.title("Niny 💜")
        root.configure(bg="#f4edff")
        root.resizable(False, False)
        root.protocol("WM_DELETE_WINDOW", root.destroy)

        self.stage = tk.Frame(root, bg="#f4edff", width=408, height=400)
        self.stage.pack(padx=8, pady=(8, 0))
        self.stage.pack_propagate(False)
        self.glow = tk.Canvas(self.stage, width=392, height=384,
                              bg="#f4edff", highlightthickness=0)
        for inset, color in ((4, "#eee1ff"), (12, "#e7d4fc"), (22, "#dfc5f8")):
            self.glow.create_oval(inset, inset, 392 - inset, 384 - inset,
                                  fill=color, outline=color)
        self.portrait = tk.Label(self.stage, bg="#f4edff", fg="#713ca2")
        self.portrait.place(relx=0.5, y=200, anchor="center")
        self.load_portrait()
        self.heart = tk.Label(self.stage, text="💜", bg="#f4edff",
                              fg="#9751cb", font=("Segoe UI", 24))
        self.sleepy = tk.Label(self.stage, text="Zzz", bg="#f4edff",
                               fg="#9751cb", font=("Segoe UI", 18, "italic"))
        self.mood = tk.StringVar(value=MOODS[0])
        tk.Label(root, textvariable=self.mood, bg="#f4edff", fg="#713ca2",
                 font=("Segoe UI", 13, "bold")).pack()
        self.message = tk.StringVar(value=MESSAGES[MOODS[0]])
        tk.Label(root, textvariable=self.message, bg="#f4edff", fg="#49325e",
                 font=("Segoe UI", 11), wraplength=300, height=2).pack(padx=20, pady=8)
        tk.Button(root, text="Pet Niny", command=self.pet,
                  font=("Segoe UI", 11), padx=20, pady=7).pack(pady=(0, 8))
        self.stay_on_top = tk.BooleanVar(value=settings["stay_on_top"])
        tk.Checkbutton(root, text="Stay on top", variable=self.stay_on_top,
                       command=self.change_preferences, bg="#f4edff",
                       fg="#49325e", activebackground="#f4edff").pack()
        self.idle_motion = tk.BooleanVar(value=settings["idle_motion"])
        tk.Checkbutton(root, text="Gentle idle motion", variable=self.idle_motion,
                       command=self.change_preferences, bg="#f4edff",
                       fg="#49325e", activebackground="#f4edff").pack()
        self.hint = tk.StringVar(value="Click Niny to pet · Drag Niny to move")
        tk.Label(root, textvariable=self.hint,
                 bg="#f4edff", fg="#713ca2", font=("Segoe UI", 9)).pack(pady=(4, 12))
        self.portrait.bind("<ButtonPress-1>", self.start_drag)
        self.portrait.bind("<B1-Motion>", self.move_drag)
        self.portrait.bind("<ButtonRelease-1>", self.finish_drag)
        self.set_stay_on_top()
        self.animate_idle()

    def change_preferences(self):
        self.set_stay_on_top()
        try:
            save_preferences(self.preference_path, {
                "stay_on_top": self.stay_on_top.get(),
                "idle_motion": self.idle_motion.get(),
            })
        except OSError:
            self.hint.set("Preferences work now, but couldn't be saved.")
        else:
            self.hint.set("Click Niny to pet · Drag Niny to move")

    def set_stay_on_top(self):
        self.root.attributes("-topmost", self.stay_on_top.get())

    def start_drag(self, event):
        self.drag_origin = (event.x_root, event.y_root,
                            self.root.winfo_x(), self.root.winfo_y())
        self.dragged = False

    def move_drag(self, event):
        if self.drag_origin is None:
            return
        pointer_x, pointer_y, window_x, window_y = self.drag_origin
        dx, dy = event.x_root - pointer_x, event.y_root - pointer_y
        if not self.dragged and max(abs(dx), abs(dy)) < 5:
            return
        self.dragged = True
        self.root.geometry(f"{window_x + dx:+d}{window_y + dy:+d}")

    def finish_drag(self, event):
        if self.drag_origin is None:
            return
        self.move_drag(event)
        if not self.dragged:
            self.pet()
        self.drag_origin = None

    def load_portrait(self):
        path = Path(__file__).resolve().with_name("niny.png")
        if not path.is_file():
            self.portrait.configure(
                text="💜\nNiny's image goes here\n\nAdd niny.png beside niny.py",
                font=("Segoe UI", 14), width=28, height=10)
            return
        try:
            from PIL import Image, ImageTk
            with Image.open(path) as source:
                portrait = source.convert("RGBA")
            portrait.thumbnail((360, 360), Image.Resampling.LANCZOS)
            self.image = ImageTk.PhotoImage(portrait, master=self.root)
            self.portrait.configure(image=self.image)
        except (ImportError, OSError, ValueError) as error:
            self.portrait.configure(text="Niny couldn't load her image.",
                                    font=("Segoe UI", 13), width=28, height=8)
            messagebox.showwarning("Niny's image", str(error), parent=self.root)

    def pet(self, event=None):
        self.mood_index = (self.mood_index + 1) % len(MOODS)
        mood = MOODS[self.mood_index]
        self.mood.set(mood)
        self.message.set(MESSAGES[mood])
        self.update_reaction(mood)
        if self.heart_timer is not None:
            self.root.after_cancel(self.heart_timer)
        self.heart.place(relx=0.82, y=35, anchor="center")
        self.heart.lift()
        self.heart_timer = self.root.after(900, self.hide_heart)

    def update_reaction(self, mood):
        self.glow.place_forget()
        self.sleepy.place_forget()
        if mood == "Happy":
            self.glow.place(relx=0.5, y=200, anchor="center")
            self.portrait.lift()
        elif mood == "Sleepy":
            self.sleepy.place(relx=0.18, y=45, anchor="center")
            self.sleepy.lift()

    def hide_heart(self):
        self.heart.place_forget()
        self.heart_timer = None

    def animate_idle(self):
        mood = MOODS[self.mood_index]
        self.idle_phase += 0.07 if mood == "Sleepy" else 0.14
        still = not self.idle_motion.get() or mood == "Focus" or self.drag_origin is not None
        offset = 0 if still else 3 * math.sin(self.idle_phase)
        self.portrait.place_configure(y=200 + offset)
        if mood == "Happy":
            self.glow.place_configure(y=200 + offset)
        self.root.after(100, self.animate_idle)


def main():
    root = tk.Tk()
    Niny(root)
    root.mainloop()


if __name__ == "__main__":
    main()
