import json
import os
import requests
from bottle import route, run, request

from LINEbot import LineMessage


CAT = os.environ["CHANNEL_ACCESS_TOKEN"]
MASTER = os.environ["MASTER"]
url_reply = "https://api.line.me/v2/bot/message/reply"


@route("/callback", method='POST')
def callback():
    events = request.json['events']
    for event in events:
        if not event['type'] == "message":
            break
        message = LineMessage(event)
        if not message.room == "user" or not message.sender == MASTER:
            return f"Hi, this is Jehanne.\nauthorization failed."
        if message.type == "text":
            text = create_text(message.message)
            res = message.reply_text(text)
        elif mes_type == "image":
            pass
        else:
            res = "No response."
    return f"Hi, this is Jehanne.\nresponse: {res}"


def create_text(message):
    if "ジャンヌ" in message:
        reply = "およびですか、マスター。"
    else:
        reply = f"メッセージを受け取りました。\ntext: {message}"
    return message


run(host="0.0.0.0", port=int(os.environ.get("PORT", 443)))
