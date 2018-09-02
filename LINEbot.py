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
    MASTER = os.environ['MASTER']
    url_reply = "https://api.line.me/v2/bot/message/reply"
    url_push = "https://api.line.me/v2/bot/message/push"

    def __init__(self, event=None):
        """Constructor for LineMessage"""
        self.room = event['source']['type'] if event is not None else None
        self.sender = event['source']['userId'] if event is not None else None
        self.type = event['message']['type'] if event is not None else None
        self.token = event['replyToken'] if event is not None else None
        self.message = self.get_message(event['message']) if event is not None else None
        self.body = []

    def get_message(self, message):
        if self.type == "text":
            return message['text']
        elif self.type in ["image", "video", "audio"]:
            url_content = f"https://api.line.me/v2/bot/message/{message['id']}/content"
            header = {'Authorization': f"Bearer {self.CAT}"}
            return requests.get(url_content, headers=header).content
        elif self.type == "file":
            return message['fileName']
        elif self.type == "location":
            return None
        elif self.type == "sticker":
            return message['packageId'], message['stickerId']
        else:
            return None

    def add_text(self, text):
        if len(self.body) < 5:
            self.body.append({'type': 'text', 'text': text})

    def add_image(self, url_ori, url_pre):
        if len(self.body) < 5:
            self.body.append({'type': 'image', 'originalContentUrl': url_ori, 'previewImageUrl': url_pre})

    def add_video(self, url_ori, url_pre):
        if len(self.body) < 5:
            self.body.append({'type': 'video', 'originalContentUrl': url_ori, 'previewImageUrl': url_pre})

    def add_audio(self, url_ori, dur):
        if len(self.body) < 5:
            self.body.append({'type': 'audio', 'originalContentUrl': url_ori, 'duration': dur})

    def add_sticker(self, pkg, stk):
        if len(self.body) < 5:
            self.body.append({'type': 'sticker', 'packageId': pkg, 'stickerId': stk})

    def reply_message(self):
        header = {'Content-Type': 'application/json', 'Authorization': f"Bearer {self.CAT}"}
        data = {'replyToken': self.token, 'messages': self.body}
        req = requests.post(self.url_reply, data=json.dumps(data), headers=header)
        return req

    def push_message(self):
        header = {'Content-Type': 'application/json', 'Authorization': f"Bearer {self.CAT}"}
        data = {'to': self.MASTER, 'messages': self.body}
        req = requests.post(self.url_push, data=json.dumps(data), headers=header)
        return req
