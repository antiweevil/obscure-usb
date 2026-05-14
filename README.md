# obscure-usb

Establish a reverse shell between a Linux machine and Windows victim via a BadUSB. Tested on Debian13 with Seytonic's Malduino 3.

## Prerequisites

First, ensure you have ngrok. It can be installed via the following.
```bash
sudo apt update && sudo apt install ngrok
```

Next, create an account at [ngrok.com](https://ngrok.com) and copy your Authtoken from [the dashboard](https://dashboard.ngrok.com/get-started/your-authtoken).

Save your Authtoken in ngrok's configuration.
```bash
ngrok config add-authtoken YOUR_AUTHTOKEN
```

## Installation

To install ObscureUSB, run the following. `init.sh` will install any other needed dependencies.
```bash
git clone https://github.com/antiweevil/obscure-usb.git
cd obscure-usb
bash init.sh
```

## Configuration

Finally, edit `config_usb.txt`. If you have a BadUSB, insert it in setup mode. Then, store the location of your payload file (the one that will run on the victim) inside `config_usb.txt`. For example:
```bash
echo "/media/antiweevil/A87B-A154/1.txt" > config_usb.txt
```

Otherwise, if you do not have a BadUSB, place the configuration in MANUAL mode.
```bash
echo "MANUAL" > config_usb.txt
```

Both methods should produce the same results.

## Usage

Once everything has been configured, you may run the program with the following.
```bash
python3 obscure.py
```

Follow and respond to the guided steps and questions. Once your USB has been configured by Obscure, or a custom script has been produced, run the payload on the target machine.

If everything works correctly, a message stating a received connection should display.

## Reverse shell commands

Once a connection has been established, there are multiple commands that you can execute on the target's device.

+ **Create a pop-up**: Displays a pop-up on the target's machine with a custom message.

+ **Type to keyboard**: Presses certain keys to spell out a message or run a Windows shortcut. For example, `{ENTER}` returns to the next line and `^{w}` closes the current tab. Learn more [here](https://learn.microsoft.com/en-us/dotnet/api/system.windows.forms.sendkeys).

+ **Jitter cursor rapidly**: Move the target's cursor randomly and uncontrollably for a few seconds. Stops automatically after a certain time frame.

+ **Manage files**: Lock or unlock the target's filesystem by exploiting a vulnerability in File Explorer. Disables many functions of the computer while locked, such as pressing the Windows key.

+ **Capture screenshot**: Use another TCP listener to retrieve a snapshot of the target's screen. The resulting image is saved to `out/capture.png` and is displayed as a thumbnail on the attacker's device. May take a few seconds to receive fully.

+ **Configure malware**: Run or stop various malware, including Salinewin, Memz, and ButterflyOnDesktop. These malware may cause irreversibly damage to the target's machine, especially Memz. Use with caution.

+ **Open camera**: Start the Windows camera application. May be combined with the capture screenshot functionality to receive a picture of the target's room.

+ **Wipe machine**: Irreversibly destroy most contents on the target's hard drive. Use with caution.

+ **Shut down machine**: Immediately breaks the connection to the target, removing any remaining Obscure files, and shuts down the target's computer.

+ **Run custom command**: Execute a command directly to the reverse shell established between the attacker and target. A brief output of the reverse shell is shown after running.

+ **Break connection**: Immediately breaks the connection to the target, and removes any Obscure files on the target's machine.

## Reconnecting

If at any time you exited, you can return to the session by simply running the program again.
```bash
python3 obscure.py
```

## Disclaimer

Never use this program or any of its components on machines you do not own or have explicit permission to use. I am not responsible for any damages.
