import uuid

class User:

    USER_ID_LEN = len(str(uuid.uuid1()))

    def __init__(self):
        self.user_id = str(uuid.uuid1())

    @staticmethod
    def from_user_id(uid):
        u = User()
        u.user_id = uid
        return u