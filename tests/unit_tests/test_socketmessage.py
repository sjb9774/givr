from givr.socketmessage import SocketMessage, SocketCommand
import unittest
import uuid


class TestSocketMessage(unittest.TestCase):

    def test_valid_message(self):
        uid = str(uuid.uuid1())
        msg = SocketMessage(sender="USER", recipient=uid, command=SocketCommand.JOIN)
        self.assertEqual("USER:{uid}:JOIN".format(uid=uid), str(msg))
