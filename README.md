![Obscure USB](/src/obscure-usb-header.png)

# Obscure-USB

Establish a reverse shell between a Linux machine and Windows victim via a BadUSB. Tested on Debian13 with Seytonic's Malduino 3. Uses [pinggy.io](https://pinggy.io/)'s tunneling service as a middleman to connect the two devices, and [dpaste](https://dpaste.com/) to host the custom scripts online.

## 🌐 Installation

To install ObscureUSB, run the following. `init.sh` will install any other needed dependencies.
```bash
git clone https://github.com/antiweevil/obscure-usb.git
cd obscure-usb
bash init.sh
```

## 🛠️ Configuration

Finally, edit `obscure_config.txt`. If you have a BadUSB, insert it in setup mode. Then, store the path of your payload file (the one that will run on the victim) inside `obscure_config.txt`. For example:
```bash
echo "/media/jane/A87B-A154/1.txt" > obscure_config.txt
```

Otherwise, if you do not have a BadUSB, place the configuration in MANUAL mode.
```bash
echo "MANUAL" > obscure_config.txt
```

Both methods should produce the same results.

## 🪡 Usage

Once everything has been configured, you may run the program with the following.
```bash
python3 obscure.py
```

Once the USB has been configured by Obscure, or a custom script has been produced, run the payload on the target machine.

A message confirming a received connection should display.

Keep in mind the connection is temporary, and will timeout after 60 minutes, as [stated on the tunneling website](https://pinggy.io/).

## 🔗 Reverse shell commands

Once a connection has been established, there are multiple commands that you can execute on the target's device.

+ **Create a pop-up**
    + Displays a pop-up on the target's machine with a custom message.

+ **Type to keyboard**
    + Presses certain keys to spell out a message or run a Windows shortcut. For example, `{ENTER}` returns to the next line and `^{w}` closes the current tab. Learn more [here](https://learn.microsoft.com/en-us/dotnet/api/system.windows.forms.sendkeys).

+ **Jitter cursor rapidly**
    + Move the target's cursor randomly and uncontrollably for a few seconds. Stops automatically after a short time frame.

+ **Manage files**
    + Lock or unlock the target's filesystem by temporarily altering File Explorer. Disables many functions of the computer while locked, such as pressing the Windows key.

+ **Capture screenshot**
    + Use another TCP listener to retrieve a snapshot of the target's screen. The resulting image is saved to `out/` as a `.png` and is displayed as a thumbnail on the attacker's device. May take a few seconds to receive fully.

+ **Configure malware**
    + Install, run, or stop various malware, including Salinewin, Memz, and ButterflyOnDesktop. These malware may cause irreversible damage to the target's machine—especially Memz. Use with caution.

+ **Open camera**
    + Start the Windows camera application. May be combined with the capture screenshot functionality to receive a picture of the target and/or the target's room.

+ **Wipe machine**
    + Irreversibly destroy most contents on the target's hard drive. Use with caution.

+ **Shut down machine**
    + Immediately break the connection to the target, removing any remaining Obscure files, and shut down the target's computer.

+ **Run custom command**
    + Execute a command directly to the reverse shell established between the attacker and target. A brief output of the reverse shell is shown after running.

+ **Break connection**
    + Immediately break the connection to the target, and remove any Obscure files remaining on the target's machine.

## 🔌 Reconnecting

If at any time you exited, you can return to the session by simply running the program again.
```bash
python3 obscure.py
```

## 👋 Credits

+ **tylerdotrar**: Powershell reverse shell
    + Available at [rgbwiki.com](https://rgbwiki.com/Red%20Cell/07.%20Payloads/PowerShell%20Reverse%20Shells/).
+ **CaliNux**: Script obfuscation
    + Available at [powershellgallery.com](https://www.powershellgallery.com/packages/Invoke-Obfuscation/).
    + Lowers the risk of AMSI detection when run on the target machine.
+ **setiawanap**: Duck icon in the header
    + Available at [flaticon.com](https://www.flaticon.com/free-icon/duck_6023094).

## ⚠️ Disclaimer

Never use this program or any of its components on machines you do not own or have explicit permission to use. I am not responsible for any damages.