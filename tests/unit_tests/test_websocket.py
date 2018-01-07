import unittest
from givr.websocket import WebSocketFrame, bits, bits_value


class TestBitsFunctions(unittest.TestCase):

    def test_bits_valid_input(self):
        num = 201
        bstr = bits(num)
        self.assertEqual(bstr, "11001001")

    def test_bits_large_input(self):
        with self.assertRaises(ValueError):
            bits(5400)

    def test_bits_neg_input(self):
        with self.assertRaises(ValueError):
            bits(-100)

    def test_bits_value_valid_input(self):
        v = bits_value("10010100")
        self.assertEqual(148, v)

    def test_bits_value_invalid_bits(self):
        inputs = ["102332", "0000kkksm", "hello world", "1100 1"]
        for i in inputs:
            with self.subTest(i=i):
                with self.assertRaises(ValueError):
                    bits_value(i)

    def test_bits_value_invalid_input(self):
        with self.assertRaises(ValueError):
            bits_value(10010110)


class TestWebSocketFrame(unittest.TestCase):

    def test_webframe_from_data_non_fragmented(self):
        data = b'\x81\x89I\x96k\xa8\x1d\xd38\xfci\xd2*\xfc\x08'
        f = WebSocketFrame.from_bytes(data)
        self.assertEqual(f.message, "TEST DATA")
        self.assertEqual(f.payload_length, 9)
        self.assertEqual(f.opcode, 1)
        self.assertEqual(f.mask_flag, 1)
        self.assertEqual(f.mask, "01001001100101100110101110101000")
