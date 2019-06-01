import json
import os
import requests

from typing import List, Optional, Any


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

    CAT = os.environ['CHANNEL_ACCESS_TOKEN']                # type: str
    MASTER = os.environ['MASTER']                           # type: str
    url_reply = "https://api.line.me/v2/bot/message/reply"  # type: str
    url_push = "https://api.line.me/v2/bot/message/push"    # type: str

    def __init__(self):
        self.body = []  # type: List[dict]

    def add_text(self, text: str) -> None:
        self.body.append({'type': 'text', 'text': text})

    def add_image(self, url_ori: str, url_pre: str) -> None:
        self.body.append({'type': 'image', 'originalContentUrl': url_ori, 'previewImageUrl': url_pre})

    def add_video(self, url_ori: str, url_pre: str) -> None:
        self.body.append({'type': 'video', 'originalContentUrl': url_ori, 'previewImageUrl': url_pre})

    def add_audio(self, url_ori: str, dur: str) -> None:
        self.body.append({'type': 'audio', 'originalContentUrl': url_ori, 'duration': dur})

    def add_sticker(self, pkg: str, stk: str) -> None:
        self.body.append({'type': 'sticker', 'packageId': pkg, 'stickerId': stk})

    def reply_message(self) -> List[requests.Response]:
        req = []    # type: List[requests.Response]
        header = {'Content-Type': 'application/json', 'Authorization': f"Bearer {self.CAT}"}
        while self.body:
            data = {'replyToken': self.token, 'messages': self.body[:5]}
            req.append(requests.post(self.url_reply, data=json.dumps(data), headers=header))
            self.body = self.body[5:]
        return req

    def push_message(self) -> List[requests.Response]:
        req = []    # type: List[requests.Response]
        header = {'Content-Type': 'application/json', 'Authorization': f"Bearer {self.CAT}"}
        while self.body:
            data = {'to': self.MASTER, 'messages': self.body[:5]}
            req.append(requests.post(self.url_push, data=json.dumps(data), headers=header))
            self.body = self.body[5:]
        return req

    def reply_text(self, text: str) -> List[requests.Response]:
        self.add_text(text)
        return self.reply_message()

    def push_text(self, text: str) -> List[requests.Response]:
        self.add_text(text)
        return self.push_message()


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
    content : str?
        main contents of received message.
    """

    def __init__(self, event=None):
        LineClient.__init__(self)
        self.room = event['source']['type'] if event else None                  # type: Optional[str]
        self.sender = event['source']['userId'] if event else None              # type: Optional[str]
        self.type = event['message']['type'] if event else None                 # type: Optional[str]
        self.token = event['replyToken'] if event else None                     # type: Optional[str]
        self.content = self.get_content(event['message']) if event else None    # type: Any

    def get_content(self, message: dict) -> Any:
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
        self.token = event['replyToken']                    # type: str
        self.data = json.loads(event['postback']['data'])   # type: str
