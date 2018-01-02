import re
from givr.user import User
from givr.exceptions import SocketMessageException
from givr.websocket import WebSocketFrame
from givr.logging import get_logger

logger = get_logger(__name__)


class SocketMessageMetaClass(type):

    all_messages = {
        "JOIN": "JOIN",
        "ENTER": "ENTER",
        "LEAVE": "LEAVE",
        "SUCCESS": "SUCCESS",
        "WINNER": "WINNER",
        "GIVEAWAY": "GIVEAWAY",
        "FAILURE": "FAILURE"
    }

    def __init__(self, name, bases, namespace):
        super(SocketMessageMetaClass, self).__init__(name, bases, namespace)
        for msg, value in self.all_messages.items():
            setattr(self, msg, value)


class SocketMessage(metaclass=SocketMessageMetaClass):
    MSG_REGEX = re.compile(r"([\w\d-]+):([\w\d\-]+):(\w+)(?:\:(.+))?")
    UUID_REGEX = re.compile(r"[\w\d]{8}-[\w\d]{4}-[\w\d]{4}-[\w\d]{4}-[\w\d]{12}")

    def __init__(self, sender=None, recipient=None, message=None, info=None):
        if sender and not self.UUID_REGEX.findall(sender):
            logger.warning("Sender UUID '{uid}' invalid".format(uid=sender))
            raise SocketMessageException("Sender UUID '{uid}' invalid".format(uid=sender))
        if recipient and not self.UUID_REGEX.findall(recipient):
            logger.warning("Recipient UUID '{uid}' invalid".format(uid=recipient))
            raise SocketMessageException("Recipient UUID '{uid}' invalid".format(uid=recipient))
        if message and message not in SocketMessage.all_messages:
            logger.warning("Message '{msg}' invalid".format(msg=message))
            raise SocketMessageException("Message '{msg}' invalid".format(msg=message))

        self.sender = sender
        self.recipient = recipient
        self.message = message
        self.info = info
        logger.debug("New SocketMessage created '{msg}'".format(msg=self))

    def __str__(self):
        return "{sender}:{recipient}:{msg}{info}".format(sender=self.sender,
                                                       recipient=self.recipient,
                                                       msg=self.message,
                                                       info=":" + self.info if self.info else "")
    def to_text(self):
        return str(self)

    @classmethod
    def from_text(cls, text):
        matches = cls.MSG_REGEX.findall(text)
        if matches:
            sender, recipient, msg, info = matches[0]
        else:
            raise SocketMessageException("Message text '{msg}' invalid".format(msg=text))

        smsg = cls(sender=sender, recipient=recipient, message=msg, info=info)
        smsg._raw = text
        return smsg


class WebSocketMessage(SocketMessage):

    @classmethod
    def from_text(cls, data):
        frame = WebSocketFrame(data)
        return super(WebSocketMessage, cls).from_text(frame.message)
