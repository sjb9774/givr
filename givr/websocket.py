from givr.logging import get_logger

logger = get_logger(__name__)

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

def to_binary(n, pad_to=None):
    r = n
    s = ""
    while r > 0:
        s += str(r % 2)
        r = r // 2
    result = s[-1::-1]
    if pad_to and len(result) < pad_to:
        while len(result) < pad_to:
            result = "0" + result
    return result

import select
class WebSocketFrame:

    def __init__(self, fin=1, opcode=1, rsv=0, mask_flag=0, mask=None, message=None):
        self.fin = fin
        self.opcode = opcode
        self.mask_flag = mask_flag
        self.mask = mask
        self.message = message
        self.payload_length = len(message)
        self.rsv = rsv

    def to_bytes(self):
        full_bit_str = ""
        full_bit_str += to_binary(self.fin)
        full_bit_str += to_binary(self.rsv, pad_to=3)
        full_bit_str += to_binary(self.opcode, pad_to=4)
        full_bit_str += to_binary(self.mask_flag)
        full_bit_str += to_binary(self.payload_length, pad_to=7)
        if self.mask:
            full_bit_str += to_binary(self.mask)
        if self.mask_flag:
            mask_values = [bits_value(mask[x:x+8]) for x in range(0, len(mask), 8)]
            masked_message = []
            for i, char in enumerate(self.message):
                masked_message.append(ord(char) ^ mask_values[i % 4])
            full_bit_str += "".join(to_binary(x) for x in masked_message)
        else:
            full_bit_str += "".join([to_binary(x) for x in (ord(y) for y in self.message)])
        return bytes((bits_value(full_bit_str[x:x+8])) for x in range(0, len(full_bit_str), 8))

    @classmethod
    def from_bytes(cls, in_bytes):
        full_bit_str = "".join([bits(byte) for byte in in_bytes])
        bit_generator = (bit for bit in full_bit_str)
        get_next_bits = lambda x: "".join(next(bit_generator) for i in range(x))

        #   First find the payload length
        fin = bits_value(get_next_bits(1))
        rsv = bits_value(get_next_bits(3)) # can be safely ignored
        opcode = bits_value(get_next_bits(4))
        mask_flag = bits_value(get_next_bits(1))
        bits_9_15_val = bits_value(get_next_bits(7))
        if bits_9_15_val <= 125:
            payload_length = bits_9_15_val
        elif bits_9_15_val == 126:
            payload_length = bits_value(get_next_bits(16))
        elif bits_9_15_val == 127:
            payload_length = bits_value(get_next_bits(64))

        if bool(mask_flag):
            mask = get_next_bits(32)
        message = ""
        for x in range(payload_length):
            char_data = get_next_bits(8)
            char = chr(bits_value(char_data) ^ bits_value(mask[(x % 4) * 8:((x % 4) * 8) + 8]))
            message += char
        f = cls(fin=fin, opcode=opcode, rsv=rsv, mask_flag=mask_flag, mask=mask, message=message)
        return f
