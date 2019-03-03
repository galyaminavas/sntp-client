import datetime
import socket
import struct
import time

_SYSTEM_EPOCH = datetime.date(*time.gmtime(0)[0:3])
"""system epoch"""
_NTP_EPOCH = datetime.date(1900, 1, 1)
"""NTP epoch"""
NTP_DELTA = (_SYSTEM_EPOCH - _NTP_EPOCH).days * 24 * 3600
"""delta between system and NTP time"""


class NTPPacket:
    """NTP packet class.
    This represents an NTP packet.
    """

    _PACKET_FORMAT = "!B B B b 11I"
    """packet format to pack/unpack"""

    def __init__(self, version=4, mode=3, tx_timestamp=0):
        self.version = version
        self.mode = mode
        self.orig_timestamp = 0
        self.recv_timestamp = 0
        self.tx_timestamp = tx_timestamp

    def to_data(self):
        packed = struct.pack(NTPPacket._PACKET_FORMAT,
                             (0 << 6 | self.version << 3 | self.mode), 0, 0, 0,
                             0, 0, 0, 0,
                             0, 0, 0, 0,
                             0,
                             int(self.tx_timestamp),
                             int(abs(self.tx_timestamp - int(self.tx_timestamp)) * 2 ** 32))
        return packed

    def from_data(self, data):
        unpacked = struct.unpack(NTPPacket._PACKET_FORMAT,
                                 data[0:struct.calcsize(NTPPacket._PACKET_FORMAT)])

        self.version = unpacked[0] >> 3 & 0x7
        self.mode = unpacked[0] & 0x7
        self.orig_timestamp = unpacked[9] + float(unpacked[10])/2**32
        self.recv_timestamp = unpacked[11] + float(unpacked[12])/2**32
        self.tx_timestamp = unpacked[13] + float(unpacked[14])/2**32