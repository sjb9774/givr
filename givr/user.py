import uuid

class User:

    USER_ID_LEN = len(str(uuid.uuid1()))

    def __init__(self):
        self.user_id = str(uuid.uuid1())

    def __eq__(self, other):
        return hasattr(other, "user_id") and self.user_id == other.user_id

    @staticmethod
    def from_user_id(uid):
        u = User()
        u.user_id = uid
        return u
