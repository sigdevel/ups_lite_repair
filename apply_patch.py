#!/usr/bin/env python3
from pathlib import Path
import hashlib
import sys


DEFAULT_TARGET = "/usr/local/lib/python3.7/dist-packages/pwnagotchi/plugins/default/ups_lite.py"

ORIGINAL = """# Based on UPS Lite v1.1 from https://github.com/xenDE
#
# functions for get UPS status - needs enable "i2c" in raspi-config
#
# https://github.com/linshuqin329/UPS-Lite
#
# For Raspberry Pi Zero Ups Power Expansion Board with Integrated Serial Port S3U4
# https://www.ebay.de/itm/For-Raspberry-Pi-Zero-Ups-Power-Expansion-Board-with-Integrated-Serial-Port-S3U4/323873804310
# https://www.aliexpress.com/item/32888533624.html
#
# To display external power supply status you need to bridge the necessary pins on the UPS-Lite board. See instructions in the UPS-Lite repo.
import logging
import struct

import RPi.GPIO as GPIO

import pwnagotchi
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK


# TODO: add enable switch in config.yml an cleanup all to the best place
class UPS:
    def __init__(self):
        # only import when the module is loaded and enabled
        import smbus
        # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
        self._bus = smbus.SMBus(1)

    def voltage(self):
        try:
            address = 0x36
            read = self._bus.read_word_data(address, 2)
            swapped = struct.unpack("<H", struct.pack(">H", read))[0]
            return swapped * 1.25 / 1000 / 16
        except:
            return 0.0

    def capacity(self):
        try:
            address = 0x36
            read = self._bus.read_word_data(address, 4)
            swapped = struct.unpack("<H", struct.pack(">H", read))[0]
            return swapped / 256
        except:
            return 0.0

    def charging(self):
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(4, GPIO.IN)
            return '+' if GPIO.input(4) == GPIO.HIGH else '-'
        except:
            return '-'


class UPSLite(plugins.Plugin):
    __author__ = 'evilsocket@gmail.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'A plugin that will add a voltage indicator for the UPS Lite v1.1'

    def __init__(self):
        self.ups = None

    def on_loaded(self):
        self.ups = UPS()

    def on_ui_setup(self, ui):
        ui.add_element('ups', LabeledValue(color=BLACK, label='UPS', value='0%/0V', position=(ui.width() / 2 + 15, 0),
                                           label_font=fonts.Bold, text_font=fonts.Medium))

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('ups')

    def on_ui_update(self, ui):
        capacity = self.ups.capacity()
        charging = self.ups.charging()
        ui.set('ups', "%2i%s" % (capacity, charging))

        if capacity <= self.options['shutdown']:
            logging.info('[ups_lite] Empty battery (<= %s%%): shuting down' % self.options['shutdown'])
            ui.update(force=True, new_data={'status': 'Battery exhausted, bye ...'})
            pwnagotchi.shutdown()
"""

PATCHED = """# Based on UPS Lite v1.1 from https://github.com/xenDE
#
# functions for get UPS status - needs enable "i2c" in raspi-config
#
# https://github.com/linshuqin329/UPS-Lite
#
# For Raspberry Pi Zero Ups Power Expansion Board with Integrated Serial Port S3U4
# https://www.ebay.de/itm/For-Raspberry-Pi-Zero-Ups-Power-Expansion-Board-with-Integrated-Serial-Port-S3U4/323873804310
# https://www.aliexpress.com/item/32888533624.html
#
# To display external power supply status you need to bridge the necessary pins on the UPS-Lite board. See instructions in the UPS-Lite repo.
import logging
import struct

import RPi.GPIO as GPIO

import pwnagotchi
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK


# TODO: add enable switch in config.yml an cleanup all to the best place
class UPS:
    def __init__(self):
        # only import when the module is loaded and enabled
        import smbus
        # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
        self._bus = smbus.SMBus(1)
        self._address = None
        self._chip = None
        self._detect_device()

    def _detect_device(self):
        # Older UPS-Lite boards expose MAX17040-compatible registers on 0x36.
        # Newer XiaoJ/ACE revisions commonly expose a CW2015-compatible chip on 0x62.
        for address in (0x62, 0x36):
            try:
                self._bus.read_byte(address)
                self._address = address
                self._chip = 'cw2015' if address == 0x62 else 'max17040'
                logging.info('[ups_lite] detected battery gauge at 0x%02x (%s)', address, self._chip)
                if self._chip == 'cw2015':
                    # Recommended mode write for CW2015-based boards.
                    self._bus.write_word_data(self._address, 0x0A, 0x30)
                return
            except Exception:
                continue
        logging.warning('[ups_lite] no supported UPS battery gauge found on i2c bus')

    def voltage(self):
        try:
            if self._address is None:
                return 0.0
            if self._chip == 'cw2015':
                read = self._bus.read_word_data(self._address, 2)
                swapped = struct.unpack("<H", struct.pack(">H", read))[0]
                return swapped * 0.305 / 1000
            read = self._bus.read_word_data(self._address, 2)
            swapped = struct.unpack("<H", struct.pack(">H", read))[0]
            return swapped * 1.25 / 1000 / 16
        except:
            return 0.0

    def capacity(self):
        try:
            if self._address is None:
                return 0.0
            if self._chip == 'cw2015':
                return self._bus.read_byte_data(self._address, 0x04)
            read = self._bus.read_word_data(self._address, 4)
            swapped = struct.unpack("<H", struct.pack(">H", read))[0]
            return swapped / 256
        except:
            return 0.0

    def charging(self):
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(4, GPIO.IN)
            return '+' if GPIO.input(4) == GPIO.HIGH else '-'
        except:
            return '-'

    def has_valid_reading(self):
        capacity = self.capacity()
        voltage = self.voltage()
        return not (capacity == 0 and voltage == 0.0)


class UPSLite(plugins.Plugin):
    __author__ = 'evilsocket@gmail.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'A plugin that will add a voltage indicator for the UPS Lite v1.1'

    def __init__(self):
        self.ups = None

    def on_loaded(self):
        self.ups = UPS()

    def on_ui_setup(self, ui):
        ui.add_element('ups', LabeledValue(color=BLACK, label='UPS', value='0%/0V', position=(ui.width() / 2 + 15, 0),
                                           label_font=fonts.Bold, text_font=fonts.Medium))

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('ups')

    def on_ui_update(self, ui):
        capacity = self.ups.capacity()
        charging = self.ups.charging()
        if self.ups.has_valid_reading():
            ui.set('ups', "%2i%s" % (capacity, charging))
        else:
            ui.set('ups', "--?")
            logging.warning('[ups_lite] invalid battery reading from %s, skipping shutdown logic', self.ups._chip or 'unknown gauge')
            return

        if self.ups._address is not None and capacity <= self.options['shutdown']:
            logging.info('[ups_lite] Empty battery (<= %s%%): shuting down' % self.options['shutdown'])
            ui.update(force=True, new_data={'status': 'Battery exhausted, bye ...'})
            pwnagotchi.shutdown()
"""


def normalize(text):
    return text.replace("\r\n", "\n").replace("\r", "\n")


def digest(text):
    return hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(DEFAULT_TARGET)
    if not target.exists():
        print(f"target not found: {target}")
        return 1

    current = target.read_text(encoding="utf-8")
    current_norm = normalize(current)
    original_norm = normalize(ORIGINAL)
    patched_norm = normalize(PATCHED)

    if current_norm == patched_norm:
        print(f"already patched: {target}")
        return 0

    if current_norm != original_norm:
        print(f"unexpected file content: {target}")
        print(f"current sha256 : {digest(current)}")
        print(f"original sha256: {digest(ORIGINAL)}")
        print(f"patched sha256 : {digest(PATCHED)}")
        return 2

    backup = target.with_suffix(target.suffix + ".bak")
    backup.write_text(current, encoding="utf-8")
    target.write_text(PATCHED, encoding="utf-8")
    print(f"backup written: {backup}")
    print(f"patched file : {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
