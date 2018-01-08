from givr.socketmessage import SocketMessage, WebSocketMessage
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


class TestWebSocketMessage(unittest.TestCase):

    def setUp(self):
        self.good_uid1 = str(uuid.uuid1())
        self.good_uid2 = str(uuid.uuid1())

    def test_msg_from_bytes_non_fragmented_no_mask(self):
        msg = "{uid1}:{uid2}:SUCCESS".format(uid1=self.good_uid1, uid2=self.good_uid2)
        wsm = WebSocketMessage.from_text(b'\x81Q' + bytes(msg, 'utf-8'))
        self.assertEqual(wsm.message, SocketMessage.SUCCESS)
        self.assertEqual(wsm.sender, self.good_uid1)
        self.assertEqual(wsm.recipient, self.good_uid2)

    def test_msg_from_bytes_non_fragmented_with_mask(self):
        # use preset uids to keep the scope of this test narrow and not involve
        # using the masking methods from WebSocketFrame
        uid1 = "ebffebb0-f42b-11e7-95bc-141877a352d3"
        uid2 = "ebfff43e-f42b-11e7-95bc-141877a352d3"
        wsm = WebSocketMessage.from_text(b'\x81\xd1\xec\xb7\x91\x81\x89\xd5\xf7\xe7\x89\xd5\xf3\xb1\xc1\xd1\xa5\xb3\x8e\x9a\xa0\xb0\x89\x80\xbc\xb8\xd9\xd5\xf2\xac\xdd\x83\xa0\xb9\xdb\x80\xf0\xb2\xd9\x85\xf5\xb2\xd6\xd2\xf3\xe7\x8a\xd1\xa5\xb2\x89\x9a\xf7\xb5\xde\xd5\xbc\xb0\xdd\xd2\xa6\xac\xd5\x82\xf3\xe2\xc1\x86\xa5\xb0\xd4\x80\xa6\xe0\xdf\x82\xa3\xe5\xdf\x8d\xc2\xd4\xaf\xf4\xd4\xd2\xbf')
        self.assertEqual(wsm.message, SocketMessage.SUCCESS)
        self.assertEqual(wsm.sender, uid1)
        self.assertEqual(wsm.recipient, uid2)
