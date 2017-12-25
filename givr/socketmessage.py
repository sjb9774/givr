import re
from givr.user import User
from givr.exceptions import SocketMessageException
class SocketMessage:
    MSG_REGEX = re.compile(r"([\w\d-]+):([\w\d\-]+):(\w+)")
    UUID_REGEX = re.compile(r"[\w\d]{8}-[\w\d]{4}-[\w\d]{4}-[\w\d]{4}-[\w\d]{12}")

    def __init__(self, sender=None, recipient=None, command=None):
        if sender and not self.UUID_REGEX.findall(sender):
            raise SocketMessageException("Sender UUID '{uid}' invalid".format(uid=sender))
        if recipient and not self.UUID_REGEX.findall(recipient):
            raise SocketMessageException("Recipient UUID '{uid}' invalid".format(uid=recipient))
        if command and command not in SocketCommandMetaClass.all_commands:
            raise SocketMessageException("Command '{cmd}' invalid".format(cmd=command))
        self.sender = sender
        self.recipient = recipient
        self.command = command

    def __str__(self):
        return "{sender}:{recipient}:{command}".format(sender=self.sender,
                                                       recipient=self.recipient,
                                                       command=self.command)
    def to_text(self):
        return str(self)

    @classmethod
    def from_text(cls, text):
        matches = cls.MSG_REGEX.findall(text)
        if matches:
            sender, recipient, command = matches[0]
        else:
            raise SocketMessageException("Message text '{msg}' invalid".format(msg=text))

        msg = cls(sender=sender, recipient=recipient, command=command)
        msg._raw = text
        return msg

class SocketCommandMetaClass(type):

    all_commands = {
        "JOIN": "JOIN",
        "ENTER": "ENTER",
        "LEAVE": "LEAVE"
    }

    def __init__(self, name, bases, namespace):
        super(SocketCommandMetaClass, self).__init__(name, bases, namespace)
        for command, value in self.all_commands.items():
            setattr(self, command, value)

class SocketCommand(metaclass=SocketCommandMetaClass):
    pass
