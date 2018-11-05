import json
import os
import requests


class LineClient:

    """
    LineClient is the protocol class of LineMessage and LinePostback.

    Attributes
    ----------
    CAT : str
        Channel Access Token for LINE MessagingAPI.
    MASTER : str
        Jehanne's master, yatabis's LINE user ID.
    url_reply : str
        the endpoint for reply message API.
    url_push : str
        the endpoint for push message API.
    body : list of message object
        list of LINE message objects for reply or push message.
    """

    CAT = os.environ['CHANNEL_ACCESS_TOKEN']
    MASTER = os.environ['MASTER']
    url_reply = "https://api.line.me/v2/bot/message/reply"
    url_push = "https://api.line.me/v2/bot/message/push"

    def __init__(self):
        self.body = []

    def add_text(self, text):
        self.body.append({'type': 'text', 'text': text})

    def add_image(self, url_ori, url_pre):
        self.body.append({'type': 'image', 'originalContentUrl': url_ori, 'previewImageUrl': url_pre})

    def add_video(self, url_ori, url_pre):
        self.body.append({'type': 'video', 'originalContentUrl': url_ori, 'previewImageUrl': url_pre})

    def add_audio(self, url_ori, dur):
        self.body.append({'type': 'audio', 'originalContentUrl': url_ori, 'duration': dur})

    def add_sticker(self, pkg, stk):
        self.body.append({'type': 'sticker', 'packageId': pkg, 'stickerId': stk})

    def reply_message(self):
        req = []
        header = {'Content-Type': 'application/json', 'Authorization': f"Bearer {self.CAT}"}
        while self.body:
            data = {'replyToken': self.token, 'messages': self.body[:5]}
            req.append(requests.post(self.url_reply, data=json.dumps(data), headers=header))
            self.body = self.body[5:]
        return req

    def push_message(self):
        req = []
        header = {'Content-Type': 'application/json', 'Authorization': f"Bearer {self.CAT}"}
        while self.body:
            data = {'to': self.MASTER, 'messages': self.body[:5]}
            req.append(requests.post(self.url_push, data=json.dumps(data), headers=header))
            self.body = self.body[5:]
        return req

    def reply_text(self, text):
        self.add_text(text)
        self.reply_message()

    def push_text(self, text):
        self.add_text(text)
        self.push_message()


class LineMessage(LineClient):

    """
    Parameters
    ----------
    event : event object
        received LINE event object.

    Attributes
    ----------
    room    : ["user", "group", "room"]
        room type of received message.
    sender  : str
        user ID of sender.
    type    : ["text", "image", "video", "audio", "file", "location", "sticker"]
        type of received message.
    token   : str
        reply token of received message.
    content : str
        main contents of received message.
    """

    def __init__(self, event=None):
        LineClient.__init__(self)
        self.room = event['source']['type'] if event else None
        self.sender = event['source']['userId'] if event else None
        self.type = event['message']['type'] if event else None
        self.token = event['replyToken'] if event else None
        self.content = self.get_content(event['message']) if event else None

    def get_content(self, message):
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


class LinePostback(LineClient):
    """
    Parameters
    ----------
    event : event object
        received LINE event object.

    Attributes
    ----------
    token : str
        reply token of received postback.
    data : str
        data of received postback.
    """

    def __init__(self, event):
        LineClient.__init__(self)
        self.token = event['replyToken']
        self.data = json.loads(event['postback']['data'])
