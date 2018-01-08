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

    def test_listening(self):
        self.server._create_socket = Mock()
        self.server.socket = Mock(accept=Mock(return_value=(Mock(),)))
        # listen just once
        def fn(conn):
            self.server.listening = False
            return "TEST"
        self.server.connection_handler = fn
        self.server.listen()
        self.server._create_socket.assert_called_once_with()
        self.server.socket.close.assert_called_once_with()
        self.server.socket.accept()[0].close.assert_called_once_with()


