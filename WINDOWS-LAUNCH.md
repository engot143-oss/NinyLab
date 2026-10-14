# Launch Niny on Windows

Your uploaded v0.1 and v0.2 code is preserved byte-for-byte under `originals/`.
The current build keeps v0.2's dark-purple styling and original Happy message,
with the added companion behaviors. The upload named `niny.png.py` was Python
code, not an image; it is preserved as `originals/v0.1/niny.py`.

For this new prototype, use a separate folder such as
`C:\Users\enriq\NinyLab-next` to preserve your existing working app. Copy
`niny.py`, `Launch Niny.vbs`, and `Set up Niny.cmd` there. Add your approved
`niny.png`, then double-click `Launch Niny.vbs`. It automatically runs setup if
the virtual environment or dependencies are missing (requires installed Python
3 with tkinter). First-time setup shows installation progress in a console;
later launches run without a console. `Set up Niny.cmd` can also be run manually.
It uses `.venv\Scripts\pythonw.exe`, starts without a Command Prompt, and
sets the working directory so the existing image path continues to work.
Close Niny's own window to exit. You can create a desktop shortcut to the
launcher using Windows' **Send to > Desktop (create shortcut)** option.
Alternatively, double-click **Create Niny shortcut.vbs** to create one
automatically. It preserves existing shortcuts by choosing a new name. Keep
the extracted folder in place afterward; moving it breaks the shortcut.

You can also use **Choose Niny image…** in the window or right-click menu to
select your approved PNG anywhere on your PC. Niny remembers its location and
does not copy, overwrite, or edit the file. Cancelling or selecting an invalid
image keeps the current portrait. Keep the selected image at that location;
if it goes missing, Niny falls back to the bundled `niny.png` or a placeholder.

Without `niny.png`, this prototype shows a text placeholder. The first pet
changes Curious to Happy and displays **Niny is happy! 💜**. Further pets or
image clicks cycle Playful, Excited, Sleepy, Focus, then Curious. Mood changes
currently update text; they do not alter the approved image.
Petting also shows a brief purple heart. Niny gently floats while idle, slows
down when Sleepy, and stays still in Focus.
Happy adds a soft purple halo behind Niny; Sleepy adds a small **Zzz** nearby.
These decorations leave the image unchanged. Opaque image backgrounds can
cover the middle of the halo; a transparent approved PNG shows it best.
An illustrated tail-hug is still pending approved artwork.
Drag Niny's image to move her window; releasing after a drag does not pet her.
Enable **Stay on top** to keep her above other windows, or turn it off to let
other windows cover her. Turn **Gentle idle motion** off for a still companion.
Preferences are saved locally in
`%LOCALAPPDATA%\Niny\preferences.json` on Windows and restored next launch.
If saving is unavailable, Niny still works for the current session and tells
you in the footer. No account, network service, or database is involved.

Enable **Compact companion** for a smaller window with the controls hidden.
Right-click Niny to pet her, restore the full window, change settings, or close
her. The normal title bar and close button remain available. Compact mode is
also remembered next launch. The approved image is resized in memory only.

Niny settles into Sleepy after two minutes without petting, dragging, or menu
interaction. Petting wakes an automatic nap into Happy. **Focus** stays quiet
until you change it. Turn **Nap after two quiet minutes** off to disable naps;
this preference is remembered too. Right-click **Mood** to choose any state
directly. Idle detection observes only interactions with Niny, not other apps.

This launcher does not modify the existing app or image. Before future app
changes, copy `niny.py` and `niny.png` into a separate `rollback-v0.2` folder
and keep that copy unchanged.

Check on Windows: launch by double-clicking, confirm the purple image appears,
click **Pet Niny** and confirm **Niny is happy! 💜**, then close Niny's window.
Window startup, button and image clicks, all six moods, image loading with a
synthetic fixture, and closing were checked on Linux with Python 3.12 and Tk 9.
The Windows launcher and setup script have not been run on Windows; Python
3.14 and the approved Niny image still need a check on your PC.
If nothing appears, run `.venv\Scripts\python.exe niny.py` from NinyLab in a
Command Prompt to see the application's error. If Windows reports that Windows
Script Host is disabled, report that message rather than changing security policy.
Application startup and callback errors also display a dialog and save the
latest traceback to `%LOCALAPPDATA%\Niny\last-error.log` when writable.
