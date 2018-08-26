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
        header = {'Content-Type': 'application/json', 'Authorization': f"Bearer {CAT}"}
        body = {'replyToken': token,
                'messages': [
                    {'type': 'text', 'text': t} for t in text
                ]}
        req = requests.post(self.url, data=body, headers=header)
        print(req.text)
        return req.status_code


if __name__ == '__main__':
    test = "text"
    print(isinstance(text, str))
