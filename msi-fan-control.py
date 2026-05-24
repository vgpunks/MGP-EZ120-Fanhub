#!/usr/bin/env python3
"""
MSI MPG EZ120 ARGB Fan Hub - Silent Mode Control
Sends USB HID control transfers to set quiet fan profile on boot.
Vendor: 0x0db0  Product: 0x1f1e

Reverse engineered from MSI Center USB traffic capture.
Setup packet: bmRequestType=0x21, bRequest=0x09, wValue=0x0309, wIndex=0x0001
"""

import usb.core
import time
import sys

VENDOR_ID  = 0x0db0
PRODUCT_ID = 0x1f1e

# Silent fan profile - curve value 0x1c = 28%
# Captured from MSI Center Wireshark trace
CMD_FAN_SPEED = bytes([
    0x09, 0x02, 0x0f, 0x1c, 0x1c, 0x1c, 0x1c, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
])

CMD_COMMIT = bytes([
    0x09, 0x05, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
])

def apply_silent_profile():
    print("MSI MPG EZ120 ARGB - Applying silent fan profile...")

    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if dev is None:
        print("ERROR: Hub not found. Is it plugged in?")
        sys.exit(1)

    print(f"Found hub: {dev.product}")

    # Detach kernel driver from HID interface if active
    if dev.is_kernel_driver_active(1):
        dev.detach_kernel_driver(1)
        print("Detached kernel driver from interface 1")

    try:
        for i in range(2):
            dev.ctrl_transfer(0x21, 0x09, 0x0309, 0x0001, CMD_FAN_SPEED)
            print("  Sent: fan speed curve (silent)")
            time.sleep(0.15)
            dev.ctrl_transfer(0x21, 0x09, 0x0309, 0x0001, CMD_COMMIT)
            print("  Sent: commit")
            time.sleep(0.15)

        print("Done! Silent fan profile applied.")

    finally:
        # Re-attach kernel driver
        try:
            dev.attach_kernel_driver(1)
        except Exception:
            pass

if __name__ == "__main__":
    apply_silent_profile()
