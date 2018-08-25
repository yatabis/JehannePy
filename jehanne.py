import json
import os
import requests
from bottle import route, run, request


CAT = os.environ["CHANNEL_ACCESS_TOKEN"]
MASTER = os.environ["MASTER"]
url_reply = "https://api.line.me/v2/bot/message/reply"


@route("/callback", method='POST')
def callback():
    events = request.json['events']
    for event in events:
        if not event['type'] == "message":
            break
        reply_token = event['replyToken']
        mes_type = event['message']['type']
        if mes_type == "text":
            res = reply_text(reply_token, event['message'])
        else:
            res = "No response."
    return f"Hi, this is Jehanne.\nresponse: {res}"


def reply_text(token, message):
    print(message)
    header = {'Content-Type': 'application/json', 'Authorization': f"Bearer {CAT}"}
    text = f"メッセージを受け取りました。\nid: {message['id']}\ntext: {message['text']}"
    print(text)
    body = {'replyToken': token,
            'message': [
                {'type': 'text', 'text': text}
            ]}
    req = requests.post(url_reply, data=json.dumps(body), headers=header)
    print(req)
    return req.status_code


def reply_sticker():
    pass


def reply_image():
    pass


def reply_video():
    pass


run(host="0.0.0.0", port=int(os.environ.get("PORT", 443)))
