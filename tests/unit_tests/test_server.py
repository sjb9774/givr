import unittest
from unittest.mock import Mock
import givr.server
import socket

class TestSocketServer(unittest.TestCase):

    def setUp(self):
        givr.server.socket = Mock()
        givr.server.select = Mock(select=Mock(return_value=([Mock()], None, None)))
        givr.server.threading = Mock()
        self.server = givr.server.SocketServer()

    def test__create_socket(self):
        self.server._create_socket()
        givr.server.socket.socket.assert_called_once_with(givr.server.socket.AF_INET, givr.server.socket.SOCK_STREAM)
        self.server.socket.bind.assert_called_once_with(("127.0.0.1", 9000))

    def test_listening_stop_listening(self):
        self.server._create_socket = Mock()
        self.server.socket = Mock(accept=Mock(return_value=(Mock(),)))
        # listen just once
        def fn(conn):
            self.assertTrue(self.server.listening)
            self.server.stop_listening()
            return "TEST"
        self.server.connection_handler = fn
        self.server.listen()
        self.assertFalse(self.server.listening)
        self.server._create_socket.assert_called_once_with()
        self.server.socket.close.assert_called_once_with()
        self.server.socket.accept()[0].close.assert_called_once_with()

    def test_dlisten(self):
        givr.server.threading = Mock(Thread=Mock(start=Mock()))
        self.server.dlisten()
        givr.server.threading.Thread.assert_called_once_with(target=self.server.listen)
        givr.server.threading.Thread().start.assert_called_once_with()

    def test_connection_handler_with_resp(self):
        self.server.handle_message = Mock(return_value="TEST")
        connection_mock = Mock(recv=Mock(return_value="MOCK BYTES"))
        resp = self.server.connection_handler(connection_mock)
        self.assertEqual(resp, "TEST")
        connection_mock.recv.assert_called_once_with(4096)
        self.server.handle_message.assert_called_once_with(connection_mock, "MOCK BYTES")

    def test_stop_listening(self):
        self.server.dlisten()
        self.server.stop_listening()
        self.assertFalse(self.server.listening)
