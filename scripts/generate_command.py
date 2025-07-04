"""Utility to build EcoFlow protocol commands for Delta Pro."""

from __future__ import annotations

# CRC tables copied from the integration
_CRC8_TAB = [
    0, 7, 14, 9, 28, 27, 18, 21, 56, 63, 54, 49, 36, 35, 42, 45,
    112, 119, 126, 121, 108, 107, 98, 101, 72, 79, 70, 65, 84, 83, 90, 93,
    224, 231, 238, 233, 252, 251, 242, 245, 216, 223, 214, 209, 196, 195, 202, 205,
    144, 151, 158, 153, 140, 139, 130, 133, 168, 175, 166, 161, 180, 179, 186, 189,
    199, 192, 201, 206, 219, 220, 213, 210, 255, 248, 241, 246, 227, 228, 237, 234,
    183, 176, 185, 190, 171, 172, 165, 162, 143, 136, 129, 134, 147, 148, 157, 154,
    39, 32, 41, 46, 59, 60, 53, 50, 31, 24, 17, 22, 3, 4, 13, 10,
    87, 80, 89, 94, 75, 76, 69, 66, 111, 104, 97, 102, 115, 116, 125, 122,
    137, 142, 135, 128, 149, 146, 155, 156, 177, 182, 191, 184, 173, 170, 163, 164,
    249, 254, 247, 240, 229, 226, 235, 236, 193, 198, 207, 200, 221, 218, 211, 212,
    105, 110, 103, 96, 117, 114, 123, 124, 81, 86, 95, 88, 77, 74, 67, 68,
    25, 30, 23, 16, 5, 2, 11, 12, 33, 38, 47, 40, 61, 58, 51, 52,
    78, 73, 64, 71, 82, 85, 92, 91, 118, 113, 120, 127, 106, 109, 100, 99,
    62, 57, 48, 55, 34, 37, 44, 43, 6, 1, 8, 15, 26, 29, 20, 19,
    174, 169, 160, 167, 178, 181, 188, 187, 150, 145, 152, 159, 138, 141, 132, 131,
    222, 217, 208, 215, 194, 197, 204, 203, 230, 225, 232, 239, 250, 253, 244, 243,
]

_CRC16_TAB = [
    0, 49345, 49537, 320, 49921, 960, 640, 49729, 50689, 1728, 1920, 51009,
    1280, 50625, 50305, 1088, 52225, 3264, 3456, 52545, 3840, 53185, 52865, 3648,
    2560, 51905, 52097, 2880, 51457, 2496, 2176, 51265, 55297, 6336, 6528, 55617,
    6912, 56257, 55937, 6720, 7680, 57025, 57217, 8000, 56577, 7616, 7296, 56385,
    5120, 54465, 54657, 5440, 55041, 6080, 5760, 54849, 53761, 4800, 4992, 54081,
    4352, 53697, 53377, 4160, 61441, 12480, 12672, 61761, 13056, 62401, 62081,
    12864, 13824, 63169, 63361, 14144, 62721, 13760, 13440, 62529, 15360, 64705,
    64897, 15680, 65281, 16320, 16000, 65089, 64001, 15040, 15232, 64321, 14592,
    63937, 63617, 14400, 10240, 59585, 59777, 10560, 60161, 11200, 10880, 59969,
    60929, 11968, 12160, 61249, 11520, 60865, 60545, 11328, 58369, 9408, 9600,
    58689, 9984, 59329, 59009, 9792, 8704, 58049, 58241, 9024, 57601, 8640, 8320,
    57409, 40961, 24768, 24960, 41281, 25344, 41921, 41601, 25152, 26112, 42689,
    42881, 26432, 42241, 26048, 25728, 42049, 27648, 44225, 44417, 27968, 44801,
    28608, 28288, 44609, 43521, 27328, 27520, 43841, 26880, 43457, 43137, 26688,
    30720, 47297, 47489, 31040, 47873, 31680, 31360, 47681, 48641, 32448, 32640,
    48961, 32000, 48577, 48257, 31808, 46081, 29888, 30080, 46401, 30464, 47041,
    46721, 30272, 29184, 45761, 45953, 29504, 45313, 29120, 28800, 45121, 20480,
    37057, 37249, 20800, 37633, 21440, 21120, 37441, 38401, 22208, 22400, 38721,
    21760, 38337, 38017, 21568, 39937, 23744, 23936, 40257, 24320, 40897, 40577,
    24128, 23040, 39617, 39809, 23360, 39169, 22976, 22656, 38977, 34817, 18624,
    18816, 35137, 19200, 35777, 35457, 19008, 19968, 36545, 36737, 20288, 36097,
    19904, 19584, 35905, 17408, 33985, 34177, 17728, 34561, 18368, 18048, 34369,
    33281, 17088, 17280, 33601, 16640, 33217, 32897, 16448,
]

def _crc8(data: bytes) -> bytes:
    crc = 0
    for b in data:
        crc = _CRC8_TAB[(crc ^ b) & 0xFF]
    return crc.to_bytes(1, "little")


def _crc16(data: bytes) -> bytes:
    crc = 0
    for b in data:
        crc = _CRC16_TAB[(crc ^ b) & 0xFF] ^ (crc >> 8)
    return crc.to_bytes(2, "little")


def build_command(dst: int, cmd_set: int, cmd_id: int, data: bytes = b"") -> bytes:
    """Return a complete protocol frame."""
    buf = bytearray([0xAA, 0x02])
    buf += len(data).to_bytes(2, "little")
    buf += _crc8(buf)
    buf += bytes([0x0D, 0, 0, 0, 0, 0, 0, 0x20, dst, cmd_set, cmd_id])
    buf += data
    buf += _crc16(buf)
    return bytes(buf)


def ac_switch(enable: bool) -> bytes:
    """Create the AC on/off command for Delta Pro."""
    arg = bytes([1 if enable else 0, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    return build_command(4, 32, 66, arg)


# ---------------------------------------------------------------------------
# Query commands from the official integration
# ---------------------------------------------------------------------------

def get_product_info(dst: int = 2) -> bytes:
    """Return product information command."""
    return build_command(dst, 1, 5)


def get_cpu_id() -> bytes:
    """Return CPU ID command."""
    return build_command(2, 1, 64)


def get_serial_main() -> bytes:
    """Return main serial number command."""
    return build_command(2, 1, 65)


def get_serial_extra() -> bytes:
    """Return extra serial number command."""
    return build_command(6, 1, 65)


def get_pd() -> bytes:
    """Return power data command."""
    return build_command(2, 32, 2, b"\0")


def get_ems_main() -> bytes:
    """Return main EMS data command."""
    return build_command(3, 32, 2)


def get_inverter() -> bytes:
    """Return inverter data command."""
    return build_command(4, 32, 2)


def get_ems_extra() -> bytes:
    """Return extra EMS data command."""
    return build_command(6, 32, 2)


def get_lcd() -> bytes:
    """Return LCD settings command."""
    return build_command(2, 32, 40)


def is_delta(product: int) -> bool:
    """Return True if the product is a DELTA model."""
    return 12 < product < 16


def get_dc_in_type(product: int) -> bytes:
    """Return DC input type command."""
    if is_delta(product):
        cmd = (5, 32, 82)
    else:
        cmd = (4, 32, 68)
    return build_command(*cmd, b"\0")


def get_dc_in_current(product: int) -> bytes:
    """Return DC input current command."""
    dst = 5 if is_delta(product) else 4
    return build_command(dst, 32, 72)


def get_fan_auto() -> bytes:
    """Return fan auto state command."""
    return build_command(4, 32, 74)


def get_lab() -> bytes:
    """Return lab mode state command."""
    return build_command(4, 32, 84)


if __name__ == "__main__":
    # Print example commands for verification
    print("AC switch on:", ac_switch(True).hex())
    print("get_pd:", get_pd().hex())
    print("get_ems_main:", get_ems_main().hex())
