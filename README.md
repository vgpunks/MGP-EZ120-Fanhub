MSI MPG EZ120 ARGB Fan Hub - Linux Control
A Python script and systemd service to control the MSI MPG EZ120 ARGB fan hub on Linux, replacing the need to boot into Windows to apply fan settings via MSI Center.
Background
The EZ120 fan hub connects to the motherboard via a USB 2.0 header (micro-USB cable). On Linux, the hub boots into a full-speed default state with no fan curve applied, resulting in fans running at full blast. MSI Center (Windows only) sends USB HID control transfers to configure the fan speed profile, and the hub retains these settings until power is removed.
This script replicates those USB commands at boot, allowing CachyOS (or any Linux distro) to apply the silent fan profile without ever touching Windows.
Hardware

Fan Hub: MSI MPG EZ120 ARGB (USB VID:PID 0db0:1f1e)
Connection: Micro-USB → motherboard USB 2.0 header (JUSB)
Tested on: CachyOS, kernel 7.0.9, MSI MS-7E75 motherboard

Protocol
Reverse engineered by capturing USB traffic with Wireshark + USBPcap on Windows while MSI Center applied fan settings, then replaying the commands on Linux.
USB Control Transfer Parameters
FieldValuebmRequestType0x21 (HID, Interface, Host-to-Device)bRequest0x09 (SET_REPORT)wValue0x0309 (Report Type: Feature, Report ID: 9)wIndex0x0001 (Interface 1)wLength0x0020 (32 bytes)
Command Payloads (32 bytes each)
Command A — Set fan speed curve:
09 02 0f 1c 1c 1c 1c 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
Command B — Commit / apply settings:
09 05 01 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
Key Payload Bytes (Command A)
ByteValueMeaning00x09Report ID10x02Command: set fan speed20x0fMinimum fan speed (15%)3–60x1cFan curve target speed (28%) — adjust to taste7+0x00Padding
Speed value reference (bytes 3–6):
ValueDecimalApprox. Speed0x1c28Silent0x3856Medium0x3a58Medium-High0x3c60High
MSI Center sends Command A followed by Command B twice in succession for reliability.
Device Interfaces
The hub exposes two USB interfaces:

Interface 0 — Vendor Specific (0xff) — no endpoints, does not accept control transfers
Interface 1 — HID (0x03) — single Interrupt IN endpoint 0x82, 32 bytes — this is where fan commands are sent

On Linux the hub appears as /dev/hidraw0 (verify with ls /sys/class/hidraw/).
Requirements
bashsudo pip install pyusb --break-system-packages
Or via your package manager:
bashsudo pacman -S python-pyusb   # Arch/CachyOS
sudo apt install python3-usb  # Debian/Ubuntu
Installation
bash# Copy script
sudo cp msi-fan-control.py /usr/local/bin/msi-fan-control.py

# Copy systemd service
sudo cp msi-fan-control.service /etc/systemd/system/msi-fan-control.service

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable msi-fan-control.service
sudo systemctl start msi-fan-control.service
Manual Usage
bashsudo python3 /usr/local/bin/msi-fan-control.py
Customizing Fan Speed
Edit msi-fan-control.py and change the four 0x1c bytes in CMD_FAN_SPEED to your desired value. Higher = faster. Tested range: 0x1c (quiet) to 0x3c (loud).
Future Work

GUI with slider / preset profiles (Silent / Balanced / Performance)
Temperature-based dynamic curves using lm-sensors
Expose as standard hwmon device for compatibility with fancontrol and other tools
Submit to OpenRGB for combined fan + ARGB control

How the Capture Was Done

Connected hub to Windows machine
Installed Wireshark with USBPcap on Windows
Started capture on all USBPcap interfaces
Opened MSI Center, applied silent profile, then cranked fans to max, then back to silent
Saved .pcapng capture
Analyzed with tshark on Linux to identify 0db0:1f1e device traffic
Decoded USBPcap headers to extract raw HID control transfer setup packets and payloads
Replayed with pyusb on Linux

Notes

The hub does not persist settings across a full power cycle (not just reboot — actual power off). The systemd service re-applies them at every boot.
The AIO cooler (0db0:0076, Mystic Light) appears to persist its own settings and does not require this workaround.
Running as root is required for USB device access. A udev rule could allow non-root access if desired.
