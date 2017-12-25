from givr.socketmessage import SocketMessage, SocketCommand
from givr.exceptions import SocketMessageException
import unittest
import uuid


class TestSocketMessage(unittest.TestCase):

    def setUp(self):
        self.good_uid1 = str(uuid.uuid1())
        self.good_uid2 = str(uuid.uuid1())
        self.bad_uid = "BAD_UID"
        self.bad_command = "BAD COMMAND"

    def test_valid_message(self):
        msg = SocketMessage(sender=self.good_uid1, recipient=self.good_uid2, command=SocketCommand.JOIN)
        self.assertEqual("{uid1}:{uid2}:JOIN".format(uid1=self.good_uid1, uid2=self.good_uid2), str(msg))

    def test_invalid_message_bad_sender(self):
        with self.assertRaises(SocketMessageException) as err:
            msg = SocketMessage(sender=self.bad_uid, recipient=self.good_uid1, command=SocketCommand.JOIN)
        self.assertIn("sender", err.exception.args[0].lower())

    def test_invalid_message_bad_recipient(self):
        with self.assertRaises(SocketMessageException) as err:
            msg = SocketMessage(sender=self.good_uid1, recipient=self.bad_uid, command=SocketCommand.JOIN)
        self.assertIn("recipient", err.exception.args[0].lower())

    def test_invalid_message_bad_command(self):
        with self.assertRaises(SocketMessageException) as err:
            msg = SocketMessage(sender=self.good_uid1, recipient=self.good_uid2, command=self.bad_command)
        self.assertIn("command", err.exception.args[0].lower())
