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

    def reply_text(self, text):
        if len(self.body) < 5:
            self.body.append({'type': 'text', 'text': text})

    def reply_image(self, url_ori, url_pre):
        if len(self.body) < 5:
            self.body.append({'type': 'image', 'originalContentUrl': url_ori, 'previewImageUrl': url_pre})

    def reply_video(self, url_ori, url_pre):
        if len(self.body) < 5:
            self.body.append({'type': 'video', 'originalContentUrl': url_ori, 'previewImageUrl': url_pre})

    def reply_audio(self, url_ori, dur):
        if len(self.body) < 5:
            self.body.append({'type': 'audio', 'originalContentUrl': url_ori, 'duration': dur})

    def reply_sticker(self, pkg, stk):
        if len(self.body) < 5:
            self.body.append({'type': 'sticker', 'packageId': pkg, 'stickerId': stk})

    def send_reply(self):
        header = {'Content-Type': 'application/json', 'Authorization': f"Bearer {self.CAT}"}
        data = {'replyToken': self.token, 'messages': self.body}
        req = requests.post(self.url_reply, data=data, headers=header)
        return req.status_code

    def push_text(self, text, to):
        pass
