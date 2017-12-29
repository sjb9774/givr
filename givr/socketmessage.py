import re
from givr.user import User
from givr.exceptions import SocketMessageException
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
        return "{sender}:{recipient}:{msg}".format(sender=self.sender,
                                                       recipient=self.recipient,
                                                       msg=self.message)
    def to_text(self):
        return str(self)

    @classmethod
    def from_text(cls, text):
        matches = cls.MSG_REGEX.findall(text)
        if matches:
            sender, recipient, msg, info = matches[0]
        else:
            raise SocketMessageException("Message test '{msg}' invalid".format(msg=text))

        smsg = cls(sender=sender, recipient=recipient, message=msg, info=info)
        smsg._raw = text
        return smsg


class WebSocketMessage(SocketMessage):

    @classmethod
    def from_text(cls, data):
        parsed

    @classmethod
    def get_payload_length(cls, data):
        complete_bit_str = "".join([WebSocketMessage.bits(byte) for byte in data])
        # payload length is determined in bits 9-15 inclusive
        bits9_15_value = WebSocketMessage.bits_value(complete_bit_str[9:16])
        if bits9_15_value <= 125:
            return bits9_15_value
        # if the valus is 126 then we need to read the next 16 bits for the length
        elif bits9_15_value == 126:
            return WebSocketMessage.bits_value(complete_bit_str[16:33])
        # if the value is 127 then we need to read the next 64 bits for the length
        elif bits9_15_value == 127:
            return WebSocketMessage.bits_value(complete_bit_str[16:81])
        else:
            raise SocketMessageException("WebSocket payload data malformed")

    @staticmethod
    def bits(byte, p=7):
        if byte > 255:
            raise ValueError("Bytes can't be greater than 255")
        result = '1' if byte >= (2**p) else '0'
        if result == '0' and p > 0:
            result += WebSocketMessage.bits(byte, p-1)
        elif p > 0:
            leftover = byte - 2**p
            result += WebSocketMessage.bits(leftover, p-1)
        return result

    @staticmethod
    def bits_value(bits):
        p = len(bits) - 1
        total = 0
        for i, bit in enumerate(bits):
            total += int(bit) * (2**(p-i))
        return total


