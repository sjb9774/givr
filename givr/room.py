from givr.exceptions import RoomException, GivrException
from givr.user import User
from givr.socketmessage import SocketMessage, WebSocketMessage
from givr.giveaway import Giveaway
from givr.logging import get_logger
from givr.websocket import WebSocketFrame
import uuid
import functools

logger = get_logger(__name__)


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

    def remove_user(self, user):
        logger.debug("Removing user '{u}' from room {r}".format(u=user.user_id, r=self.room_id))
        self.users = [u for u in self.users if user.user_id != u.user_id]


import socket, select, re, threading, base64, hashlib

class SocketRoom(Room):

    def __init__(self, address=('127.0.0.1', 9000)):
        super(SocketRoom, self).__init__()
        self.address = address
        self.listening = False

    def _create_socket(self):
        logger.debug("Creating socket")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(self.address)

    def dlisten(self):
        t = threading.Thread(target=self.listen)
        t.start()
        return t

    def listen(self):
        self._create_socket()
        logger.debug("Listening on socket")
        self.socket.listen(100)
        self.open()
        connections = []

        self.listening = True
        while self.listening:
            conn, _, _ = select.select([self.socket], [], [], .1)
            for c in conn:
                connections.append(self.socket.accept())
                logger.debug("New connection created at {addr}".format(addr=connections[-1]))

            for connection in connections:
                try:
                    data = connection[0].recv(4096)
                    if data:
                        response = self.handle_message(connection, data)
                        if response:
                            connection[0].sendall(response.encode())
                except socket.error as err:
                    logger.warning("Socket error '{err}'".format(err=err))
                    connections.remove(connection)
        logger.debug("Room '{r}' done listening".format(r=self.room_id))
        self.socket.close()
        [c.close() for c in connections]

    def stop_listening(self):
        logger.debug("Stopping listening for room '{r}'".format(r=self.room_id))
        self.listening = False

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
                return SocketMessage(recipient=msg.sender,
                                     sender=self.room_id,
                                     message=SocketMessage.FAILURE,
                                     info=fail_msg)

    def handle_message(self, connection, data):
        data = data.decode() if type(data) == bytes else data
        logger.debug("SocketRoom '{r}' recieved data '{m}'".format(r=self.room_id, m=data))
        msg = SocketMessage.from_text(data)
        return self.delegate_command(msg).to_text()

    def check_recipient(fn):
        @functools.wraps(fn)
        def wrapped_fn(self, msg):
            if msg.recipient != self.room_id:
                logger.warn("Message sent to incorrect room: {msg}".format(msg=msg))
                return SocketMessage(recipient=msg.sender,
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
        return SocketMessage(recipient=msg.sender, sender=self.room_id, message=SocketMessage.SUCCESS)

    @check_recipient
    def _handle_leave(self, msg):
        user = User.from_user_id(msg.sender)
        self.remove_user(user)
        return SocketMessage(recipient=msg.sender, sender=self.room_id, message=SocketMessage.SUCCESS)

    @check_recipient
    def _handle_giveaway(self, msg):
        sender = User.from_user_id(msg.sender)
        if sender != self.owner:
            logger.warning("Giveaway attempted in room {r} by non-owner {u}".format(r=self.room_id, u=sender.user_id))
            raise RoomException("Giveaways can only be initiated by the room owner")
        else:
            g = Giveaway(users=self.users)
            winner = g.draw(1)[-1]
            return SocketMessage(sender=self.room_id,
                                 recipient=sender.user_id,
                                 message=SocketMessage.SUCCESS,
                                 info=winner.user_id)


class WebSocketRoom(SocketRoom):

    WEBSOCKET_MAGIC = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    def __init__(self, address=('127.0.0.1', 9000)):
        super(WebSocketRoom, self).__init__(address=address)
        self.handshook = False

    def handle_message(self, conn, data):
        logger.debug("WebSocket data: {d}".format(d=data))
        if not self.handshook:
            self.handshook = True
            return self.handle_websocket_handshake(data.decode())
        else:
            msg = WebSocketMessage.from_text(data)
            return self.delegate_command(msg).to_text()

    def _get_websocket_accept(self, key):
        return base64.b64encode(hashlib.sha1((key + self.WEBSOCKET_MAGIC).encode()).digest()).decode()

    def handle_websocket_handshake(self, data):
        split_data = data.split("\r\n")
        method, path, http = split_data[0].split(" ")
        headers = {}
        for header in split_data[1:]:
            if ": " in header:
                key, value = header.split(": ")
                headers[key] = value
        accept = self._get_websocket_accept(headers.get("Sec-WebSocket-Key"))
        response = "".join(["HTTP/1.1 101 Switching Protocols\r\n",
                            "Upgrade: websocket\r\n",
                            "Connection: Upgrade\r\n",
                            "Sec-WebSocket-Accept: {accept}\r\n\r\n".format(accept=accept)])
        return response
