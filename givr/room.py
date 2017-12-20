from givr.exceptions import RoomException
import uuid

class Room:
    ROOM_ID_LEN = len(str(uuid.uuid1()))

    def __init__(self):
        self.room_id = str(uuid.uuid1())
        self._open = False
        self.users = []

    def open(self):
        self._open = True

    def is_open(self):
        return self._open

    def close(self):
        self._open = False
        users_copy = self.users[:] # avoid looping through list we're modifying
        [self.remove_user(u) for u in users_copy]

    def add_user(self, user):
        if not self.is_open():
            raise RoomException("Can't add user to closed room")
        self.users.append(user)

    def add_owner(self, user):
        self.owner = user
        self.add_user(user)

    def remove_user(self, user):
        self.users.remove(user)
