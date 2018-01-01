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
        self.parse_bits(self._complete_bit_str)

    def parse_bits(self, data):
        bit_gen = (x for x in data)
        get_next_bits = lambda x: "".join([next(bit_gen) for i in range(x)])

        #   First find the payload length
        first_9 = get_next_bits(9)
        bits_9_15_val = bits_value(get_next_bits(7))
        if bits_9_15_val <= 125:
            self.payload_length = bits_9_15_val
        elif bits_9_15_val == 126:
            self.payload_length = bits_value(get_next_bits(16))
        elif bits_9_15_val == 127:
            self.payload_length = bits_value(get_next_bits(64))

        self.mask = get_next_bits(32)
        self.message = ""
        for x in range(self.payload_length):
            char_data = get_next_bits(8)
            char = chr(bits_value(char_data) ^ bits_value(self.mask[(x % 4) * 8:((x % 4) * 8) + 8]))
            self.message += char
        
