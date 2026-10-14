import tkinter as tk

root = tk.Tk()
root.title("Niny v0.1")
root.geometry("360x420")
root.configure(bg="#241334")

title = tk.Label(
    root,
    text="Niny 💜",
    font=("Segoe UI", 24, "bold"),
    fg="#D9A7FF",
    bg="#241334"
)
title.pack(pady=35)

face = tk.Label(
    root,
    text="🦊",
    font=("Segoe UI Emoji", 100),
    bg="#241334"
)
face.pack()

mood = tk.Label(
    root,
    text="Niny is curious...",
    font=("Segoe UI", 14),
    fg="white",
    bg="#241334"
)
mood.pack(pady=20)

def niny_clicked():
    mood.config(text="Niny is happy! 💜")

button = tk.Button(
    root,
    text="Pet Niny",
    font=("Segoe UI", 12),
    command=niny_clicked
)
button.pack(pady=15)

root.mainloop()