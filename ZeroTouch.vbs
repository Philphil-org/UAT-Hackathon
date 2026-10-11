Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strDir = fso.GetParentFolderName(WScript.ScriptFullName)

' If virtual environment doesn't exist yet, run Start_Aero.bat in a visible setup window
If Not fso.FolderExists(strDir & "\venv") Then
    WshShell.Run """" & strDir & "\Start_Aero.bat""", 1, True
Else
    ' Launch ZeroTouch using pythonw.exe completely silently (0 cmd windows)
    If fso.FileExists(strDir & "\venv\Scripts\pythonw.exe") Then
        WshShell.CurrentDirectory = strDir
        WshShell.Run """" & strDir & "\venv\Scripts\pythonw.exe"" launcher.py", 0, False
    Else
        WshShell.CurrentDirectory = strDir
        WshShell.Run "pythonw.exe launcher.py", 0, False
    End If
End If
