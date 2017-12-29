def bits(byte, p=7):
    if byte > 255:
        raise ValueError("Bytes can't be greater than 255")
    result = '1' if byte >= (2**p) else '0'
    if result == '0' and p > 0:
        result += bits(byte, p-1)
    elif p > 0:
        leftover = byte - 2**p
        result += bits(leftover, p-1)
    return result

def bits_value(bits):
    p = len(bits) - 1
    total = 0
    for i, bit in enumerate(bits):
        total += int(bit) * (2**(p-i))
    return total


class WebSocketFrame:

    def __init__(self, data):
        self._raw_data = data
        self._complete_bit_str = "".join([bits(byte) for byte in data])
        self.parse_data()

    def parse_data(self):
        #   First find the payload length

