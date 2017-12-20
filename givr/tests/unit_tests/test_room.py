import unittest
from givr.room import Room
from givr.user import User
from givr.exceptions import RoomException

class TestRoom(unittest.TestCase):

    def test_new_room_has_id(self):
        r = Room()
        self.assertTrue(r.room_id)
        self.assertEqual(r.room_id, Room.ROOM_ID_LEN)

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
        self.assertIn(u1, r.users)

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
        self.assertEqual(r.users, 0)
        self.assertEqual(r.owner, o)

    def test_add_users_to_unopened_room(self):
        r = Room()
        u = User()
        self.assertFalse(r.is_open())
        self.assertRaises(RoomException, r.add_user(u))
