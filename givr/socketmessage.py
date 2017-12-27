import re
from givr.user import User
from givr.exceptions import SocketMessageException


class SocketMessageMetaClass(type):

    all_messages = {
        "JOIN": "JOIN",
        "ENTER": "ENTER",
        "LEAVE": "LEAVE",
        "SUCCESS": "SUCCESS"
    }

    def __init__(self, name, bases, namespace):
        super(SocketMessageMetaClass, self).__init__(name, bases, namespace)
        for msg, value in self.all_messages.items():
            setattr(self, msg, value)


class SocketMessage(metaclass=SocketMessageMetaClass):
    MSG_REGEX = re.compile(r"([\w\d-]+):([\w\d\-]+):(\w+)")
    UUID_REGEX = re.compile(r"[\w\d]{8}-[\w\d]{4}-[\w\d]{4}-[\w\d]{4}-[\w\d]{12}")

    def __init__(self, sender=None, recipient=None, message=None):
        if sender and not self.UUID_REGEX.findall(sender):
            raise SocketMessageException("Sender UUID '{uid}' invalid".format(uid=sender))
        if recipient and not self.UUID_REGEX.findall(recipient):
            raise SocketMessageException("Recipient UUID '{uid}' invalid".format(uid=recipient))
        if message and message not in SocketMessage.all_messages:
            raise SocketMessageException("Message '{msg}' invalid".format(msg=message))
        self.sender = sender
        self.recipient = recipient
        self.message = message

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
            sender, recipient, msg = matches[0]
        else:
            raise SocketMessageException("Message test '{msg}' invalid".format(msg=text))

        smsg = cls(sender=sender, recipient=recipient, message=msg)
        smsg._raw = text
        return smsg
