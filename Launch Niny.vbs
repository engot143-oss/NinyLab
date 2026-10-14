Option Explicit

Dim files, shell, folder, python, consolePython, app, setup, needsSetup, result
Set files = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
folder = files.GetParentFolderName(WScript.ScriptFullName)
python = files.BuildPath(folder, ".venv\Scripts\pythonw.exe")
app = files.BuildPath(folder, "niny.py")
consolePython = files.BuildPath(folder, ".venv\Scripts\python.exe")
setup = files.BuildPath(folder, "Set up Niny.cmd")

If Not files.FileExists(app) Then
    MsgBox "niny.py is missing. Put this launcher beside your working niny.py.", vbExclamation, "Launch Niny"
    WScript.Quit 1
End If

shell.CurrentDirectory = folder
needsSetup = Not files.FileExists(python) Or Not files.FileExists(consolePython)
If Not needsSetup Then
    result = shell.Run(Chr(34) & consolePython & Chr(34) & " -c " & Chr(34) & "import tkinter; import PIL" & Chr(34), 0, True)
    needsSetup = (result <> 0)
End If
If needsSetup Then
    If Not files.FileExists(setup) Then
        MsgBox "Set up Niny.cmd is missing. Extract all files from the Niny preview into the same folder.", vbExclamation, "Launch Niny"
        WScript.Quit 1
    End If
    ' Only first-time setup shows a console, so installation errors stay visible.
    result = shell.Run(Chr(34) & shell.ExpandEnvironmentStrings("%ComSpec%") & Chr(34) & " /d /s /c " & Chr(34) & Chr(34) & setup & Chr(34) & " --auto" & Chr(34), 1, True)
    If result <> 0 Or Not files.FileExists(python) Then
        MsgBox "Niny's setup didn't finish. Check the setup error and try again.", vbExclamation, "Launch Niny"
        WScript.Quit 1
    End If
End If
' pythonw starts without a console; Niny runs independently of this launcher.
shell.Run Chr(34) & python & Chr(34) & " " & Chr(34) & app & Chr(34), 0, False
