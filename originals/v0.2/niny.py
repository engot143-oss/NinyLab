import tkinter as tk
from PIL import Image, ImageTk

root = tk.Tk()
root.title("Niny v0.2")
root.geometry("420x520")
root.configure(bg="#241334")

title = tk.Label(
    root,
    text="Niny 💜",
    font=("Segoe UI", 24, "bold"),
    fg="#D9A7FF",
    bg="#241334"
)
title.pack(pady=(20, 10))

# Load the real Niny
image = Image.open("niny.png")
image.thumbnail((320, 320))

niny_image = ImageTk.PhotoImage(image)

niny = tk.Label(
    root,
    image=niny_image,
    bg="#241334"
)
niny.pack(pady=5)

mood = tk.Label(
    root,
    text="Niny is curious...",
    font=("Segoe UI", 14),
    fg="white",
    bg="#241334"
)
mood.pack(pady=10)

def niny_clicked():
    mood.config(text="Niny is happy! 💜")

button = tk.Button(
    root,
    text="Pet Niny",
    font=("Segoe UI", 12),
    command=niny_clicked
)
button.pack(pady=10)

root.mainloop()