import unittest
from givr.room import Room, SocketRoom, WebSocketRoom
from givr.user import User
from givr.exceptions import RoomException
from givr.socketmessage import SocketMessage
from unittest.mock import Mock

class TestRoom(unittest.TestCase):

    def test_new_room_has_id(self):
        r = Room()
        self.assertTrue(r.room_id)
        self.assertEqual(len(r.room_id), Room.ROOM_ID_LEN)

    def test_open_room(self):
        r = Room()
        r.open()
        self.assertTrue(r.is_open())

    def test_room_add_user(self):
        r = Room()
        r.open()
        u = User()
        r.add_user(u)
        self.assertEqual(len(r.users), 1)

    def test_room_add_owner(self):
        r = Room()
        r.open()
        o = User()
        r.add_owner(o)
        self.assertEqual(len(r.users), 1)
        self.assertEqual(o, r.owner)

    def test_remove_user(self):
        r = Room()
        r.open()
        u1 = User()
        u2 = User()
        r.add_user(u1)
        r.add_user(u2)
        self.assertIn(u1, r.users)
        r.remove_user(u1)
        self.assertNotIn(u1, r.users)
        self.assertIn(u2, r.users)

    def test_close_room(self):
        r = Room()
        r.open()
        u1 = User()
        u2 = User()
        o = User()
        r.add_user(u1)
        r.add_user(u2)
        r.add_owner(o)
        r.close()
        self.assertFalse(r.is_open())
        self.assertEqual(len(r.users), 0)
        self.assertEqual(r.owner, o)

    def test_add_users_to_unopened_room(self):
        r = Room()
        u = User()
        self.assertFalse(r.is_open())
        with self.assertRaises(RoomException):
            r.add_user(u)


import uuid
class TestSocketRoom(unittest.TestCase):

    def setUp(self):
        self.room = SocketRoom()

    def test_handle_message_join(self):
        test_id = str(uuid.uuid1())
        msg = "{uid1}:{uid2}:JOIN".format(uid1=test_id, uid2=self.room.room_id)
        self.room.open()
        resp = self.room.handle_message(Mock("mock connection"), msg)
        self.assertTrue(resp.to_text().endswith("SUCCESS"))
        self.assertEqual(test_id, self.room.users[0].user_id)

    def test_handle_message_leave(self):
        self.room.open()
        u = User()
        self.room.users = [u, User(), User(), User()]
        msg = "{uid1}:{uid2}:LEAVE".format(uid1=u.user_id, uid2=self.room.room_id)
        resp = self.room.handle_message(Mock("mock connection"), msg)
        self.assertTrue(resp.to_text().endswith("SUCCESS"))
        self.assertNotIn(u, self.room.users)

    def test_handle_message_giveaway(self):
        self.room.open()
        owner = User()
        self.room.add_owner(owner)
        msg = "{uid1}:{uid2}:GIVEAWAY".format(uid1=owner.user_id, uid2=self.room.room_id)
        resp = self.room.handle_message(Mock("mock connection"), msg)
        self.assertEqual(resp.info, owner.user_id)
        self.assertTrue(resp.message, "SUCCESS")

    def test_handle_message_giveaway_non_owner(self):
        self.room.open()
        owner = User()
        self.room.add_owner(owner)
        user = User()
        self.room.add_user(user)
        msg = "{uid1}:{uid2}:GIVEAWAY".format(uid1=user.user_id, uid2=self.room.room_id)
        resp = self.room.handle_message(Mock("mock connection"), msg)
        self.assertEqual(resp.message, "FAILURE")
        self.assertIn("initiated by the room owner", resp.info)

    def test_handle_bad_recipient(self):
        u = User()
        self.room.open()
        for message in ("JOIN", "LEAVE", "GIVEAWAY"):
            with self.subTest(message=message):
                msg = "{uid1}:{uid2}:{m}".format(uid1=str(uuid.uuid1()), uid2=u.user_id, m=message)
                resp = self.room.handle_message(Mock("mock connection"), msg)
                self.assertEqual(resp.message, "FAILURE")
                self.assertIn("not intended for this room", resp.info)

    def test_handlers(self):
        for handler in ("giveaway", "join", "leave"):
            with self.subTest(handler=handler):
                fn = getattr(self.room, "_handle_{handler}".format(handler=handler))
                u = User()
                self.room.open()
                self.room.add_owner(u)
                msg = SocketMessage(sender=u.user_id, recipient=self.room.room_id, message=handler.upper())
                resp = fn(msg)
                self.assertEqual(resp.message, SocketMessage.SUCCESS)

    def test__handle_giveaway_non_owner(self):
        u = User()
        msg = SocketMessage(sender=u.user_id, recipient=self.room.room_id, message=SocketMessage.GIVEAWAY)
        with self.assertRaises(RoomException) as err:
            self.room._handle_giveaway(msg)
            self.assertIn("room owner", err.args[0])


class TestWebSocketRoom(unittest.TestCase):

    def setUp(self):
        self.room = WebSocketRoom()

    def test_handle_handshake(self):
        client_handshake = "GET / HTTP/1.1\r\nSec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
        handshake_response = self.room.handle_websocket_handshake(client_handshake).split("\r\n")
        self.assertEqual(handshake_response[0], "HTTP/1.1 101 Switching Protocols")
        headers = {k: v for k,v in [header.split(": ") for header in handshake_response[1:4]]}
        self.assertEqual(headers.get("Upgrade"), "websocket")
        self.assertEqual(headers.get("Connection"), "Upgrade")
        self.assertEqual(headers.get("Sec-WebSocket-Accept"), "s3pPLMBiTxaQ9kYGzzhZRbK+xOo=")

    def test_handle_message(self):
        self.room.handshook = True # assume the handshake succeeded, it's tested above
        
