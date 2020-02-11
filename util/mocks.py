
class TelebotMock:
    def send_message(self, id, msg):
        message = 'User {} sent message: {}'.format(id, msg)
        print(message)


class ChatMock:
    def __init__(self, id):
        self.id = id


class MessageMock:
    def __init__(self, text, id):
        self.text = text
        self.chat = ChatMock(id)

