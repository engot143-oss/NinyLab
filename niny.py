"""Niny's small local desktop home. Run with Python or Launch Niny.vbs."""

from pathlib import Path
import math
import json
import os
import tempfile
import time
import sys
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox


MOODS = ("Curious", "Happy", "Playful", "Excited", "Sleepy", "Focus")
NAP_AFTER_SECONDS = 120
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
    defaults = {"stay_on_top": False, "idle_motion": True, "compact": False,
                "idle_naps": True, "image_path": ""}
    try:
        saved = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return defaults
    if isinstance(saved, dict):
        for key in defaults:
            if type(saved.get(key)) is bool:
                defaults[key] = saved[key]
        defaults["image_path"] = saved.get("image_path", "") if isinstance(saved.get("image_path"), str) else ""
    return defaults


def read_portrait(path):
    from PIL import Image
    with Image.open(path) as source:
        return source.convert("RGBA")


def report_error(error_type, error, trace, parent=None, log_path=None):
    path = log_path if log_path is not None else preferences_path().with_name("last-error.log")
    details = "".join(traceback.format_exception(error_type, error, trace))
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(details, encoding="utf-8")
        location = f"Details saved to:\n{path}"
    except OSError:
        location = "Niny couldn't save an error log."
    text = f"Niny hit a problem: {error}\n\n{location}"
    try:
        messagebox.showerror("Niny needs a little help", text, parent=parent)
    except tk.TclError:
        if os.name == "nt":
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, text, "Niny needs a little help", 0x10)
        elif sys.stderr is not None:
            print(text, file=sys.stderr)


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
        self.image_path = settings["image_path"]
        self.choosing_image = False
        self.mood_index = 0
        self.last_interaction = time.monotonic()
        self.napping = False
        self.image = None
        self.portrait_source = None
        self.stage_height = 400
        self.idle_phase = 0
        self.heart_timer = None
        self.idle_timer = None
        self.drag_origin = None
        self.dragged = False
        root.title("Niny 💜")
        root.configure(bg="#f4edff")
        root.resizable(False, False)
        root.protocol("WM_DELETE_WINDOW", root.destroy)
        root.bind("<Destroy>", self.cleanup, add="+")

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
        self.controls = tk.Frame(root, bg="#f4edff")
        self.controls.pack()
        tk.Label(self.controls, textvariable=self.mood, bg="#f4edff", fg="#713ca2",
                 font=("Segoe UI", 13, "bold")).pack()
        self.message = tk.StringVar(value=MESSAGES[MOODS[0]])
        tk.Label(self.controls, textvariable=self.message, bg="#f4edff", fg="#49325e",
                 font=("Segoe UI", 11), wraplength=300, height=2).pack(padx=20, pady=8)
        tk.Button(self.controls, text="Pet Niny", command=self.pet,
                  font=("Segoe UI", 11), padx=20, pady=7).pack(pady=(0, 8))
        tk.Button(self.controls, text="Choose Niny image…", command=self.choose_image,
                  font=("Segoe UI", 10)).pack(pady=(0, 8))
        self.stay_on_top = tk.BooleanVar(value=settings["stay_on_top"])
        tk.Checkbutton(self.controls, text="Stay on top", variable=self.stay_on_top,
                       command=self.change_preferences, bg="#f4edff",
                       fg="#49325e", activebackground="#f4edff").pack()
        self.idle_motion = tk.BooleanVar(value=settings["idle_motion"])
        tk.Checkbutton(self.controls, text="Gentle idle motion", variable=self.idle_motion,
                       command=self.change_preferences, bg="#f4edff",
                       fg="#49325e", activebackground="#f4edff").pack()
        self.compact = tk.BooleanVar(value=settings["compact"])
        self.idle_naps = tk.BooleanVar(value=settings["idle_naps"])
        tk.Checkbutton(self.controls, text="Compact companion", variable=self.compact,
                       command=self.change_preferences, bg="#f4edff",
                       fg="#49325e", activebackground="#f4edff").pack()
        tk.Checkbutton(self.controls, text="Nap after two quiet minutes",
                       variable=self.idle_naps, command=self.change_preferences,
                       bg="#f4edff", fg="#49325e",
                       activebackground="#f4edff").pack()
        self.hint = tk.StringVar(value="Click to pet · Drag to move · Right-click for menu")
        tk.Label(self.controls, textvariable=self.hint,
                 bg="#f4edff", fg="#713ca2", font=("Segoe UI", 9)).pack(pady=(4, 12))
        self.menu = tk.Menu(root, tearoff=False)
        self.menu.add_command(label="Pet Niny 💜", command=self.pet)
        self.mood_menu = tk.Menu(self.menu, tearoff=False)
        for mood in MOODS:
            self.mood_menu.add_radiobutton(label=mood, variable=self.mood, value=mood,
                                           command=lambda chosen=mood: self.choose_mood(chosen))
        self.menu.add_cascade(label="Mood", menu=self.mood_menu)
        self.menu.add_command(label="Choose Niny image…", command=self.choose_image)
        self.menu.add_separator()
        self.menu.add_checkbutton(label="Compact companion", variable=self.compact,
                                  command=self.change_preferences)
        self.menu.add_checkbutton(label="Stay on top", variable=self.stay_on_top,
                                  command=self.change_preferences)
        self.menu.add_checkbutton(label="Gentle idle motion", variable=self.idle_motion,
                                  command=self.change_preferences)
        self.menu.add_checkbutton(label="Nap after two quiet minutes", variable=self.idle_naps,
                                  command=self.change_preferences)
        self.menu.add_separator()
        self.menu.add_command(label="Close Niny", command=root.destroy)
        for widget in (self.stage, self.portrait, self.glow, self.heart, self.sleepy):
            widget.bind("<Button-3>", self.show_menu)
        self.portrait.bind("<ButtonPress-1>", self.start_drag)
        self.portrait.bind("<B1-Motion>", self.move_drag)
        self.portrait.bind("<ButtonRelease-1>", self.finish_drag)
        self.set_stay_on_top()
        self.apply_compact()
        self.animate_idle()

    def cleanup(self, event):
        if event.widget is not self.root:
            return
        for timer in (self.idle_timer, self.heart_timer):
            if timer is not None:
                try:
                    self.root.after_cancel(timer)
                except tk.TclError:
                    pass
        self.idle_timer = None
        self.heart_timer = None

    def show_menu(self, event):
        self.last_interaction = time.monotonic()
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def choose_image(self):
        self.choosing_image = True
        try:
            selected = filedialog.askopenfilename(
                parent=self.root, title="Choose your approved Niny image",
                filetypes=[("PNG images", "*.png")])
            if not selected:
                return
            try:
                portrait = read_portrait(selected)
            except (ImportError, OSError, ValueError) as error:
                messagebox.showwarning("Niny's image", str(error), parent=self.root)
                return
            self.portrait_source = portrait
            self.image_path = str(Path(selected).resolve())
            self.portrait.configure(text="", width=0, height=0)
            self.change_preferences()
        finally:
            self.choosing_image = False
            self.last_interaction = time.monotonic()

    def apply_compact(self):
        compact = self.compact.get()
        width, self.stage_height = (260, 250) if compact else (408, 400)
        self.stage.configure(width=width, height=self.stage_height)
        self.glow.configure(width=width - 16, height=self.stage_height - 16)
        for item, inset in zip(self.glow.find_all(), (4, 12, 22)):
            self.glow.coords(item, inset, inset, width - 16 - inset,
                             self.stage_height - 16 - inset)
        if self.portrait_source is not None:
            from PIL import Image, ImageTk
            portrait = self.portrait_source.copy()
            size = 220 if compact else 360
            portrait.thumbnail((size, size), Image.Resampling.LANCZOS)
            self.image = ImageTk.PhotoImage(portrait, master=self.root)
            self.portrait.configure(image=self.image)
        else:
            self.portrait.configure(width=22 if compact else 28,
                                    height=8 if compact else 10,
                                    font=("Segoe UI", 10 if compact else 14))
        if compact:
            self.controls.pack_forget()
        else:
            self.controls.pack()
        self.portrait.place_configure(y=self.stage_height / 2)
        self.update_reaction(MOODS[self.mood_index])
        # Let Tk recompute size, preserving the current window position.
        self.root.geometry("")

    def change_preferences(self):
        self.last_interaction = time.monotonic()
        self.set_stay_on_top()
        self.apply_compact()
        try:
            save_preferences(self.preference_path, {
                "stay_on_top": self.stay_on_top.get(),
                "idle_motion": self.idle_motion.get(),
                "compact": self.compact.get(),
                "idle_naps": self.idle_naps.get(),
                "image_path": self.image_path,
            })
        except OSError:
            self.hint.set("Preferences work now, but couldn't be saved.")
        else:
            self.hint.set("Click to pet · Drag to move · Right-click for menu")

    def set_stay_on_top(self):
        self.root.attributes("-topmost", self.stay_on_top.get())

    def start_drag(self, event):
        self.last_interaction = time.monotonic()
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
        self.last_interaction = time.monotonic()
        if not self.dragged:
            self.pet()
        self.drag_origin = None

    def load_portrait(self):
        bundled = Path(__file__).resolve().with_name("niny.png")
        path = Path(self.image_path) if self.image_path else bundled
        if self.image_path and not path.is_file():
            self.image_path = ""
            path = bundled
        if not path.is_file():
            self.portrait.configure(
                text="💜\nNiny's image goes here\n\nChoose her image below\nor from the right-click menu",
                font=("Segoe UI", 14), width=28, height=10)
            return
        try:
            from PIL import Image, ImageTk
            portrait = read_portrait(path)
            self.portrait_source = portrait.copy()
            portrait.thumbnail((360, 360), Image.Resampling.LANCZOS)
            self.image = ImageTk.PhotoImage(portrait, master=self.root)
            self.portrait.configure(image=self.image)
        except (ImportError, OSError, ValueError) as error:
            self.portrait.configure(text="Niny couldn't load her image.",
                                    font=("Segoe UI", 13), width=28, height=8)
            messagebox.showwarning("Niny's image", str(error), parent=self.root)

    def pet(self, event=None):
        mood = "Happy" if self.napping else MOODS[(self.mood_index + 1) % len(MOODS)]
        self.choose_mood(mood)
        if self.heart_timer is not None:
            self.root.after_cancel(self.heart_timer)
        self.heart.place(relx=0.82, y=35, anchor="center")
        self.heart.lift()
        self.heart_timer = self.root.after(900, self.hide_heart)

    def choose_mood(self, mood):
        self.last_interaction = time.monotonic()
        self.napping = False
        self.set_mood(mood)

    def set_mood(self, mood):
        self.mood_index = MOODS.index(mood)
        self.mood.set(mood)
        self.message.set(MESSAGES[mood])
        self.root.title(f"Niny · {mood} 💜")
        self.update_reaction(mood)

    def check_idle(self):
        mood = MOODS[self.mood_index]
        if (self.idle_naps.get() and mood not in ("Focus", "Sleepy")
                and self.drag_origin is None
                and not self.choosing_image
                and time.monotonic() - self.last_interaction >= NAP_AFTER_SECONDS):
            self.napping = True
            self.set_mood("Sleepy")

    def update_reaction(self, mood):
        self.glow.place_forget()
        self.sleepy.place_forget()
        if mood == "Happy":
            self.glow.place(relx=0.5, y=self.stage_height / 2, anchor="center")
            self.portrait.lift()
        elif mood == "Sleepy":
            self.sleepy.place(relx=0.18, y=45, anchor="center")
            self.sleepy.lift()

    def hide_heart(self):
        self.heart.place_forget()
        self.heart_timer = None

    def animate_idle(self):
        self.check_idle()
        mood = MOODS[self.mood_index]
        self.idle_phase += 0.07 if mood == "Sleepy" else 0.14
        still = not self.idle_motion.get() or mood == "Focus" or self.drag_origin is not None
        offset = 0 if still else 3 * math.sin(self.idle_phase)
        self.portrait.place_configure(y=self.stage_height / 2 + offset)
        if mood == "Happy":
            self.glow.place_configure(y=self.stage_height / 2 + offset)
        self.idle_timer = self.root.after(100, self.animate_idle)


def main():
    root = None
    try:
        root = tk.Tk()
        root.report_callback_exception = lambda kind, error, trace: report_error(kind, error, trace, parent=root)
        Niny(root)
        root.mainloop()
    except Exception:
        report_error(*sys.exc_info(), parent=root)
        if root is not None:
            try:
                root.destroy()
            except tk.TclError:
                pass
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
