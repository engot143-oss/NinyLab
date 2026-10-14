Option Explicit

Dim files, shell, folder, launcher, shortcut
Set files = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
folder = files.GetParentFolderName(WScript.ScriptFullName)
launcher = files.BuildPath(folder, "Launch Niny.vbs")

If Not files.FileExists(launcher) Then
    MsgBox "Extract the whole Niny ZIP first, then run this file from the extracted folder.", vbExclamation, "Niny shortcut"
    WScript.Quit 1
End If

Dim destination, number
destination = files.BuildPath(shell.SpecialFolders("Desktop"), "Niny.lnk")
number = 2
' Keep existing shortcuts safe; choose a new name instead of replacing one.
Do While files.FileExists(destination)
    destination = files.BuildPath(shell.SpecialFolders("Desktop"), "Niny (" & number & ").lnk")
    number = number + 1
Loop

Set shortcut = shell.CreateShortcut(destination)
shortcut.TargetPath = files.BuildPath(files.GetSpecialFolder(0), "System32\wscript.exe")
shortcut.Arguments = Chr(34) & launcher & Chr(34)
shortcut.WorkingDirectory = folder
shortcut.Description = "Launch your local Niny desktop companion"
shortcut.Save
MsgBox "Niny's shortcut is on your desktop. Keep this extracted folder where it is so the shortcut keeps working.", vbInformation, "Niny shortcut"
