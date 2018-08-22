import json
import os
import requests
from bottle import route, run, request


CAT = os.environ["CHANNEL_ACCESS_TOKEN"]
MASTER = os.environ["MASTER"]
url_reply = "https://api.line.me/v2/bot/message/reply"


@route("/callback", method='POST')
def callback():
    events = request.json
    print(events)
    """
    for event in events:
        if event['type'] == "message":
            reply_token = event['replyToken']
            mes_type = event['message']['type']
            if mes_type == "text":
                headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {CAT}"}
                body = json.dumps({'replyToken': reply_token,
                                   'messages': [{'type': 'text', 'text': "リクエストがPOSTされました。"}]})
                req = requests.post(url_reply, data=body, headers=headers)
    """
    return f"Hi, this is Jehanne."


run(host="0.0.0.0", port=int(os.environ.get("PORT", 443)))
