import os
import requests


class LineMessage:
    """
    :param room: ["user", "group", "room"]
    :param sender: userId
    :param type: ["text", "image", "video", "audio", "file", "location", "sticker"]
    :param message: text
    :param token: ReplyToken
    """

    CAT = os.environ['CHANNEL_ACCESS_TOKEN']
    url_reply = "https://api.line.me/v2/bot/message/reply"
    url_push = "https://api.line.me/v2/bot/message/push"

    def __init__(self, event):
        """Constructor for LineMessage"""
        self.room = event['source']['type']
        self.sender = event['source']['userId']
        self.type = event['message']['type']
        self.message = event['message']['text'] if self.type == "text" else None
        self.token = event['replyToken']

    def reply_text(self, text):
        if isinstance(text, str):
            text = [text]
        header = {'Content-Type': 'application/json', 'Authorization': f"Bearer {self.CAT}"}
        body = {'replyToken': self.token,
                'messages': [
                    {'type': 'text', 'text': t} for t in text
                ]}
        req = requests.post(self.url_reply, data=body, headers=header)
        print(req.text)
        return req.status_code

    def push_text(self, text, to):
        pass


if __name__ == '__main__':
    test = "text"
    print(isinstance(text, str))
