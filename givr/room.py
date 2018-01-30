from givr.exceptions import RoomException, GivrException
from givr.user import User
from givr.socketmessage import SocketMessage
from givr.giveaway import Giveaway
from givr.logging import get_logger
from stevesockets.websocket import WebSocketFrame
import uuid
import functools

logger = get_logger(__name__)


class House:

    _instance = None

    def __init__(self, log=None):
        if self._instance:
            raise RuntimeError("House is a Singleton class that should be instantiated with House.get_instance()")
        if not log:
            log = logger
        self.logger = log
        self.rooms = []

    def add_room(self, room):
        self.rooms.append(room)

    def remove_room(self, room):
        self.rooms.remove(room)

    def get_room(self, room_id):
        r = [room for room in self.rooms if room.room_id == room_id]
        if len(r) > 1:
            self.logger.warn("More than one room found with id '{room_id}'?".format(room_id=room_id))
        elif len(r) == 0:
            self.logger.error("No rooms found with id '{room_id}'".format(room_id=room_id))
            raise RoomException("No rooms found with id '{room_id}'".format(room_id=room_id))
        else:
            return r[0]

    @classmethod
    def get_instance(cls, log=None):
        if cls._instance:
            return cls._instance
        else:
            h = cls(log=log)
            cls._instance = h
            return h

class Room:
    ROOM_ID_LEN = len(str(uuid.uuid1()))

    def __init__(self):
        self.room_id = str(uuid.uuid1())
        self._open = False
        self.users = []
        self.owner = None
        logger.debug("Room '{r}' created".format(r=self.room_id))

    def open(self):
        logger.debug("Opening room '{r}'".format(r=self.room_id))
        self._open = True

    def is_open(self):
        return self._open

    def close(self):
        logger.debug("Closing room '{r}'".format(r=self.room_id))
        self._open = False
        users_copy = self.users[:] # avoid looping through list we're modifying
        [self.remove_user(u) for u in users_copy]

    def add_user(self, user):
        if not self.is_open():
            logger.warning("Can't add user to closed room")
            raise RoomException("Can't add user to closed room")
        logger.debug("Adding user '{u}' to room '{r}'".format(u=user.user_id, r=self.room_id))
        self.users.append(user)

    def add_owner(self, user):
        logger.debug("Adding owner '{u}' to room '{r}'".format(u=user.user_id, r=self.room_id))
        self.owner = user
        self.add_user(user)

    def has_user(self, user):
        has_user = user in self.users
        logger.debug("Room '{r}' has user '{u}'? {b}".format(r=self.room_id, u=user.user_id, b=has_user))
        return has_user

    def remove_user(self, user):
        logger.debug("Removing user '{u}' from room {r}".format(u=user.user_id, r=self.room_id))
        self.users = [u for u in self.users if user.user_id != u.user_id]

    def user_count(self):
        return len(self.users)


import socket, select, re, threading, base64, hashlib
from stevesockets.server import SocketServer, WebSocketServer

class SocketRoom(SocketServer, Room):

    MessageClass = SocketMessage

    def __init__(self, address=('127.0.0.1', 9000)):
        SocketServer.__init__(self, address=address, logger=logger)
        Room.__init__(self)

    def handle_message(self, connection, data):
        data = data.decode() if type(data) == bytes else data
        logger.debug("SocketRoom '{r}' recieved data '{m}'".format(r=self.room_id, m=data))
        msg = self.MessageClass.from_text(data)
        return self.delegate_command(msg).to_text()

    def delegate_command(self, msg):
        failed = False
        try:
            handler = getattr(self, "_handle_{msg}".format(msg=msg.message.lower()))
            resp = handler(msg)
            return resp
        except GivrException as err:
            logger.warn("A handled application error has occurred: {err}".format(err=err))
            failed = True
            fail_msg = "{err_type}: '{err_msg}'".format(err_type=err.__class__.__name__, err_msg=err.args[0])
        except BaseException as err:
            logger.error("An unhandled application error has occurred: {err}".format(err=err))
            failed = True
            fail_msg = "{err_type}: '{err_msg}'".format(err_type=err.__class__.__name__, err_msg=err.args[0])
        finally:
            if failed:
                return self.MessageClass(recipient=msg.sender,
                                         sender=self.room_id,
                                         message=SocketMessage.FAILURE,
                                         info=fail_msg)

    def check_recipient(fn):
        @functools.wraps(fn)
        def wrapped_fn(self, msg):
            if msg.recipient != self.room_id:
                logger.warn("Message sent to incorrect room: {msg}".format(msg=msg))
                return self.MessageClass(recipient=msg.sender,
                                         sender=self.room_id,
                                         message=SocketMessage.FAILURE,
                                         info="Message not intended for this room")
            else:
                return fn(self, msg)
        return wrapped_fn

    @check_recipient
    def _handle_join(self, msg):
        user = User.from_user_id(msg.sender)
        self.add_user(user)
        return self.MessageClass(recipient=msg.sender, sender=self.room_id, message=SocketMessage.SUCCESS)

    @check_recipient
    def _handle_leave(self, msg):
        user = User.from_user_id(msg.sender)
        self.remove_user(user)
        return self.MessageClass(recipient=msg.sender, sender=self.room_id, message=SocketMessage.SUCCESS)

    @check_recipient
    def _handle_giveaway(self, msg):
        sender = User.from_user_id(msg.sender)
        if sender != self.owner:
            logger.warning("Giveaway attempted in room {r} by non-owner {u}".format(r=self.room_id, u=sender.user_id))
            raise RoomException("Giveaways can only be initiated by the room owner")
        else:
            g = Giveaway(users=self.users)
            winner = g.draw(1)[-1]
            return self.MessageClass(sender=self.room_id,
                                     recipient=sender.user_id,
                                     message=SocketMessage.SUCCESS,
                                     info=winner.user_id)


class WebSocketRoom(SocketRoom, WebSocketServer):

    MessageClass = SocketMessage

    def __init__(self, address=('127.0.0.1', 9000)):
        SocketRoom.__init__(self, address=address)
        WebSocketServer.__init__(self, address=address, logger=logger)

    def handle_message(self, conn, data):
        logger.debug("WebSocket data: {d}".format(d=data))
        try:
            msg = self.MessageClass.from_text(data)
            return self.delegate_command(msg).to_text()
        except GivrException as err:
            return self.MessageClass(sender=self.room_id, recipient=self.room_id, message=SocketMessage.FAILURE).to_text()
