from givr.socketmessage import SocketMessage, SocketMessage
from givr.exceptions import SocketMessageException
import unittest
import uuid


class TestSocketMessage(unittest.TestCase):

    def setUp(self):
        self.good_uid1 = str(uuid.uuid1())
        self.good_uid2 = str(uuid.uuid1())
        self.bad_uid = "BAD_UID"
        self.bad_message = "BAD MESSAGE"

    def test_valid_message(self):
        msg = SocketMessage(sender=self.good_uid1, recipient=self.good_uid2, message=SocketMessage.JOIN)
        self.assertEqual("{uid1}:{uid2}:JOIN".format(uid1=self.good_uid1, uid2=self.good_uid2), str(msg))

    def test_invalid_message_bad_sender(self):
        with self.assertRaises(SocketMessageException) as err:
            msg = SocketMessage(sender=self.bad_uid, recipient=self.good_uid1, message=SocketMessage.JOIN)
        self.assertIn("sender", err.exception.args[0].lower())

    def test_invalid_message_bad_recipient(self):
        with self.assertRaises(SocketMessageException) as err:
            msg = SocketMessage(sender=self.good_uid1, recipient=self.bad_uid, message=SocketMessage.JOIN)
        self.assertIn("recipient", err.exception.args[0].lower())

    def test_invalid_message_bad_message(self):
        with self.assertRaises(SocketMessageException) as err:
            msg = SocketMessage(sender=self.good_uid1, recipient=self.good_uid2, message=self.bad_message)
        self.assertIn("message", err.exception.args[0].lower())

    def test_valid_from_text(self):
        msg = SocketMessage.from_text("{uid1}:{uid2}:{msg}".format(uid1=self.good_uid1, uid2=self.good_uid2, msg="JOIN"))
        self.assertEqual(msg.sender, self.good_uid1)
        self.assertEqual(msg.recipient, self.good_uid2)
        self.assertEqual(msg.message, "JOIN")

    def test_from_text_with_info(self):
        msg = SocketMessage.from_text("{uid1}:{uid2}:SUCCESS:{uid3}".format(uid1=self.good_uid1, uid2=self.good_uid2, uid3=self.good_uid2))
        self.assertEqual(msg.sender, self.good_uid1)
        self.assertEqual(msg.recipient, self.good_uid2)
        self.assertEqual(msg.info, self.good_uid2)

    def test_invalid_from_text_bad_sender(self):
        with self.assertRaises(SocketMessageException) as err:
            msg = SocketMessage.from_text("{uid1}:{uid2}:{msg}".format(uid1=self.bad_uid, uid2=self.good_uid1, msg="JOIN"))
        self.assertIn("sender", err.exception.args[0].lower())

    def test_invalid_from_text_bad_recipient(self):
        with self.assertRaises(SocketMessageException) as err:
            msg = SocketMessage.from_text("{uid1}:{uid2}:{msg}".format(uid1=self.good_uid1, uid2=self.bad_uid, msg="JOIN"))
        self.assertIn("recipient", err.exception.args[0].lower())

    def test_invalid_from_text_bad_message(self):
        with self.assertRaises(SocketMessageException) as err:
            msg = SocketMessage.from_text("{uid1}:{uid2}:{msg}".format(uid1=self.good_uid1, uid2=self.good_uid2, msg=self.bad_message))
        self.assertIn("message", err.exception.args[0].lower())

    def test_all_messages_exist(self):
        for key, value, in SocketMessage.all_messages.items():
            self.assertTrue(hasattr(SocketMessage, key))
            self.assertEqual(getattr(SocketMessage, key), value)
