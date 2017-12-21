import uuid

class User:

    USER_ID_LEN = len(str(uuid.uuid1()))

    def __init__(self):
        self.user_id = str(uuid.uuid1())
