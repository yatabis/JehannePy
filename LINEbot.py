import json
import os
import requests


class LineMessage:
    """
    :param room: ["user", "group", "room"]
    :param sender: userId
    :param type: ["text", "image", "video", "audio", "file", "location", "sticker"]
    :param token: ReplyToken
    :param message
    :param body
    """

    CAT = os.environ['CHANNEL_ACCESS_TOKEN']
    url_reply = "https://api.line.me/v2/bot/message/reply"
    url_push = "https://api.line.me/v2/bot/message/push"

    def __init__(self, event):
        """Constructor for LineMessage"""
        self.room = event['source']['type']
        self.sender = event['source']['userId']
        self.type = event['message']['type']
        self.token = event['replyToken']
        self.message = self.get_message(event['message'])
        self.body = []

    def get_message(self, message):
        if self.type == "text":
            return message['text']
        elif self.type == "image":
            return None
        elif self.type == "video":
            return None
        elif self.type == "audio":
            return None
        elif self.type == "file":
            return message['fileName']
        elif self.type == "location":
            return None
        elif self.type == "sticker":
            return message['packageId'], message['stickerId']

    def reply_text(self, text):
        if isinstance(text, str):
            text = [text]
        for t in text:
            if len(self.body) < 5:
                self.body.append({'type': 'text', 'text': t})

    def reply_sticker(self, pkgId, stkId):
        if len(self.body) < 5:
            self.body.append({'type': 'sticker', 'packageId': pkgId, 'stickerId': stkId})

    def send_reply(self):
        header = {'Content-Type': 'application/json', 'Authorization': f"Bearer {self.CAT}"}
        data = {'replyToken': self.token, 'messages': self.body}
        req = requests.post(self.url_reply, data=json.dumps(data), headers=header)
        print(req.text)
        return req.status_code

    def push_text(self, text, to):
        pass
