import re

class SocketMessage:
    MSG_REGEX = re.compile(r"(\w+):([\w\d\-]+):(\w+)")

    def __init__(self, sender=None, recipient=None, command=None):
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
        msg = cls()
        msg._raw = text
        matches = msg.MSG_REGEX.findall(text)
        if matches:
            sender, recipient, command = matches[0]

        msg.sender = sender
        msg.recipient = recipient
        msg.command = command
        return msg

class SocketCommand:

    JOIN = "JOIN"
    LEAVE = "LEAVE"
    ENTER = "ENTER"
