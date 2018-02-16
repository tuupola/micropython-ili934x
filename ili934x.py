
# This file is part of MicroPython ILI934X driver
# Copyright (c) 2016 - 2017 Radomir Dopieralski, Mika Tuupola
#
# Licensed under the MIT license:
#   http://www.opensource.org/licenses/mit-license.php
#
# Project home:
#   https://github.com/tuupola/micropython-ili934x

# pylint: disable=import-error
import utime as time
import ustruct
import framebuf
from micropython import const
# pylint: enable=import-error

#_NOP = const(0x00)
#_SWRESET = const(0x01)
#_RDDIDIF = const(0x04)
#_RDDST = const(0x09)
#_RDDPM = const(0x0a)
#_RDDMADCTL = const(0x0b)
#_RDDCOLMOD = const(0x0c)
#_RDDIM = const(0x0d)
#_RDDSM = const(0x0e)
_RDDSDR = const(0x0f) # Read Display Self-Diagnostic Result
#_SLPIN = const(0x10)
_SLPOUT = const(0x11) # Sleep Out
#_PTLON = const(0x12)
#_NORON = const(0x13)
#_DINVOFF = const(0x20)
#_DINVON = const(0x21)
_GAMSET = const(0x26) # Gamma Set
_DISPOFF = const(0x28) # Display Off
_DISPON = const(0x29) # Display On
_CASET = const(0x2a) # Column Address Set
_PASET = const(0x2b) # Page Address Set
_RAMWR = const(0x2c) # Memory Write
_RAMRD = const(0x2e) # Memory Read
#_PLTAR = const(0x30)
#_VSCRDEF = const(0x33)
#_TEOFF = const(0x34)
#_TEON = const(0x35)
_MADCTL = const(0x36) # Memory Access Control
_VSCRSADD = const(0x37) # Vertical Scrolling Start Address
#_IDMOFF = const(0x38)
#_IDMON = const(0x39)
_PIXSET = const(0x3a) # Pixel Format Set
#_WRMEMC = const(0x3c)
#_RDMEMC = const(0x3e)
#_STS = const(0x44)
#_GTS = const(0x45)
#_WRDISBV = const(0x51)
#_RDDISBV = const(0x52)
#_WRCTRLD = const(0x53)
#_RDCTRLD = const(0x54)
#_WRCABC = const(0x55)
_PWCTRLA = const(0xcb) # Power Control A
_PWCRTLB = const(0xcf) # Power Control B
_DTCTRLA = const(0xe8) # Driver Timing Control A
_DTCTRLB = const(0xea) # Driver Timing Control B
_PWRONCTRL = const(0xed) # Power on Sequence Control
_PRCTRL = const(0xf7) # Pump Ratio Control
_PWCTRL1 = const(0xc0) # Power Control 1
_PWCTRL2 = const(0xc1) # Power Control 2
_VMCTRL1 = const(0xc5) # VCOM Control 1
_VMCTRL2 = const(0xc7) # VCOM Control 2
_FRMCTR1 = const(0xb1) # Frame Rate Control 1
_DISCTRL = const(0xb6) # Display Function Control
_ENA3G = const(0xf2) # Enable 3G
_PGAMCTRL = const(0xe0) # Positive Gamma Control
_NGAMCTRL = const(0xe1) # Negative Gamma Control

def color565(r, g, b):
    return (r & 0xf8) << 8 | (g & 0xfc) << 3 | b >> 3

class ILI9341:
    """
    A simple driver for the ILI9341/ILI9340-based displays.


    >>> import ili9341
    >>> from machine import Pin, SPI
    >>> spi = SPI(miso=Pin(12), mosi=Pin(13, Pin.OUT), sck=Pin(14, Pin.OUT))
    >>> display = ili9341.ILI9341(spi, cs=Pin(0), dc=Pin(5), rst=Pin(4))
    >>> display.fill(ili9341.color565(0xff, 0x11, 0x22))
    >>> display.pixel(120, 160, 0)
    """

    width = 320
    height = 240

    def __init__(self, spi, cs, dc, rst):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=0)
        self.reset()
        self.init()
        self._scroll = 0

    def init(self):
        for command, data in (
            (_RDDSDR, b"\x03\x80\x02"),
            (_PWCRTLB, b"\x00\xc1\x30"),
            (_PWRONCTRL, b"\x64\x03\x12\x81"),
            (_DTCTRLA, b"\x85\x00\x78"),
            (_PWCTRLA, b"\x39\x2c\x00\x34\x02"),
            (_PRCTRL, b"\x20"),
            (_DTCTRLB, b"\x00\x00"),
            (_PWCTRL1, b"\x23"),
            (_PWCTRL2, b"\x10"),
            (_VMCTRL1, b"\x3e\x28"),
            (_VMCTRL2, b"\x86"),
            #(_MADCTL, b"\x48"),
            (_MADCTL, b"\x08"),
            (_PIXSET, b"\x55"),
            (_FRMCTR1, b"\x00\x18"),
            (_DISCTRL, b"\x08\x82\x27"),
            (_ENA3G, b"\x00"),
            (_GAMSET, b"\x01"),
            (_PGAMCTRL, b"\x0f\x31\x2b\x0c\x0e\x08\x4e\xf1\x37\x07\x10\x03\x0e\x09\x00"),
            (_NGAMCTRL, b"\x00\x0e\x14\x03\x11\x07\x31\xc1\x48\x08\x0f\x0c\x31\x36\x0f")):
            self._write(command, data)
        self._write(_SLPOUT)
        time.sleep_ms(120)
        self._write(_DISPON)

    def reset(self):
        self.rst(0)
        time.sleep_ms(50)
        self.rst(1)
        time.sleep_ms(50)

    def _write(self, command, data=None):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([command]))
        self.cs(1)
        if data is not None:
            self._data(data)

    def _data(self, data):
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)

    def _block(self, x0, y0, x1, y1, data=None):
        self._write(_CASET, ustruct.pack(">HH", x0, x1))
        self._write(_PASET, ustruct.pack(">HH", y0, y1))
        if data is None:
            return self._read(_RAMRD, (x1 - x0 + 1) * (y1 - y0 + 1) * 3)
        self._write(_RAMWR, data)

    def _read(self, command, count):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([command]))
        data = self.spi.read(count)
        self.cs(1)
        return data

    def pixel(self, x, y, color=None):
        if color is None:
            r, b, g = self._block(x, y, x, y)
            return color565(r, g, b)
        if not 0 <= x < self.width or not 0 <= y < self.height:
            return
        self._block(x, y, x, y, ustruct.pack(">H", color))

    def fill_rectangle(self, x, y, w, h, color):
        x = min(self.width - 1, max(0, x))
        y = min(self.height - 1, max(0, y))
        w = min(self.width - x, max(1, w))
        h = min(self.height - y, max(1, h))
        self._block(x, y, x + w - 1, y + h - 1, None)
        chunks, rest = divmod(w * h, 512)
        if chunks:
            data = ustruct.pack(">H", color) * 512
            for count in range(chunks):
                self._data(data)
        data = ustruct.pack(">H", color) * rest
        self._data(data)

    def fill(self, color):
        self.fill_rectangle(0, 0, self.width, self.height, color)

    def char(self, char, x, y, color=0xffff, background=0x0000):
        buffer = bytearray(8)
        framebuffer = framebuf.FrameBuffer1(buffer, 8, 8)
        framebuffer.text(char, 0, 0)
        color = ustruct.pack(">H", color)
        background = ustruct.pack(">H", background)
        data = bytearray(2 * 8 * 8)
        for c, byte in enumerate(buffer):
            for r in range(8):
                if byte & (1 << r):
                    data[r * 8 * 2 + c * 2] = color[0]
                    data[r * 8 * 2 + c * 2 + 1] = color[1]
                else:
                    data[r * 8 * 2 + c * 2] = background[0]
                    data[r * 8 * 2 + c * 2 + 1] = background[1]
        self._block(x, y, x + 7, y + 7, data)

    def text(self, text, x, y, color=0xffff, background=0x0000, wrap=None,
             vwrap=None, clear_eol=False):
        if wrap is None:
            wrap = self.width - 8
        if vwrap is None:
            vwrap = self.height - 8
        tx = x
        ty = y

        def new_line():
            nonlocal tx, ty

            tx = x
            ty += 8
            if ty >= vwrap:
                ty = y

        for char in text:
            if char == "\n":
                if clear_eol and tx < wrap:
                    self.fill_rectangle(tx, ty, wrap - tx + 7, 8, background)
                new_line()
            else:
                if tx >= wrap:
                    new_line()
                self.char(char, tx, ty, color, background)
                tx += 8
        if clear_eol and tx < wrap:
            self.fill_rectangle(tx, ty, wrap - tx + 7, 8, background)

    def scroll(self, dy=None):
        if dy is None:
            return self._scroll
        self._scroll = (self._scroll + dy) % self.height
        self._write(_VSCRSADD, ustruct.pack(">H", self._scroll))

    def print(self, text):
        self.scroll(8)
        self.text(text, 0, (232 + self.scroll()) % 240, clear_eol=True)
