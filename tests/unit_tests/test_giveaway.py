from givr.giveaway import Giveaway
import unittest
from unittest.mock import Mock
import uuid

class TestGiveaway(unittest.TestCase):

    def setUp(self):
        users = []
        for i in range(5):
            users.append(Mock(user_id=str(uuid.uuid1())))
        self.users = users

    def test_giveaway_draw_one(self):
        g = Giveaway(users=self.users)
        u = g.draw(1)
        self.assertEqual(len(u), 1)
        self.assertIn(u[0], self.users)

    def test_giveaway_draw_multiple(self):
        g = Giveaway(users=self.users)
        u = g.draw(5)
        self.assertEqual(len(u), 5)
        for user in u:
            self.assertIn(user, self.users)
            self.assertTrue(u.count(user) == 1)
