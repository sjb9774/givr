def bits(byte, p=7):
    if byte > 255 or byte < 0:
        raise ValueError("Bytes can't be greater than 255 or less than 0")
    result = '1' if byte >= (2**p) else '0'
    if result == '0' and p > 0:
        result += bits(byte, p-1)
    elif p > 0:
        leftover = byte - 2**p
        result += bits(leftover, p-1)
    return result

def bits_value(bits):
    if type(bits) != str:
        raise ValueError("Input should be a bit string")
    p = len(bits) - 1
    total = 0
    for i, bit in enumerate(bits):
        if bit not in ("1", "0"):
            raise ValueError("Invalid bit string")
        total += int(bit) * (2**(p-i))
    return total

def to_binary(n):
    r = n
    s = ""
    while r > 0:
        s += str(r % 2)
        r = r // 2
    return s[-1::-1]

import select
class WebSocketFrame:

    def __init__(self, data=None):
        self._raw_data = data
        if data:
            self._complete_bit_str = "".join([bits(byte) for byte in data])
            bits_gen = (b for b in self._complete_bit_str)
            self.parse_bits(lambda x: "".join(next(bits_gen) for i in range(x)))


    @classmethod
    def read_from_socket(cls, sck):
        def get_next_bits(x):
            if select.select([sck], [], []):
                return "".join((bits(i) for i in sck.recv(x)))
            else:
                raise StopIteration("No more bits to read")

    def parse_bits(self, get_next_bits):
        #   First find the payload length
        first_4 = get_next_bits(4)
        self.opcode = bits_value(get_next_bits(4))
        self.mask_flag = bits_value(get_next_bits(1))
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
