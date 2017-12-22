import unittest
from givr.user import User

class TestUser(unittest.TestCase):

    def test_user_has_id(self):
        u = User()
        self.assertEqual(len(u.user_id), User.USER_ID_LEN)

    def test_user_from_id(self):
        test_id = "TEST_ID"
        u = User.from_user_id(test_id)
        self.assertEqual(test_id, u.user_id)


