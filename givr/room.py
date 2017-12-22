from givr.exceptions import RoomException
from givr.user import User
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

import socket, select, re

class SocketRoom(Room):
    USER_MSG_REGEX = re.compile(r"USER:([\w\d\-]+):(\w+)")

    def _create_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('127.0.0.1', 9000))

    def listen(self):
        self._create_socket()
        self.socket.listen(100)
        self.open()
        connections = []
        while True:
            conn, _, _ = select.select([self.socket], [], [], .1)
            for c in conn:
                connections.append(self.socket.accept())

            for connection in connections:
                try:
                    data = connection[0].recv(1024)
                    response = self.handle_message(connection, data)
                    if response:
                        connection[0].sendall(response)
                except socket.error:
                    connections.remove(connection)

    def handle_message(self, connection, data):
        matches = self.USER_MSG_REGEX.findall(data)
        if matches[0]:
            user_id, command = matches[0]
            u = User.from_user_id(user_id)
            if command == "JOIN":
                self.add_user(u)
            return "{room_id}:SUCCESS".format(room_id=self.room_id)
        else:
            return "{room_id}:FAIL".format(room_id=self.room_id)


