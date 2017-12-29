from givr.room import SocketRoom
from givr.user import User
from givr.socketmessage import SocketMessage

def create_new_room():
    s = SocketRoom()
    s.open()
    s.listen()
    return s.room_id

def create_new_user():
    u = User()
    return u.id

def add_user_to_room(user_id, room_id):
    msg = SocketMessage(sender=user_id, recipient=room_id, message=SocketMessage.JOIN)
