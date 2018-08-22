import os
import requests
from bottle import route, run, request


CAT = os.environ["CHANNEL_ACCESS_TOKEN"]
MASTER = os.environ["MASTER"]
url_reply = "https://api.line.me/v2/bot/message/push"


@route("/callback", method='POST')
def callback():
    # headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {CAT}"}
    # body = json.dumps({'to': MASTER,
    #                    'messages': [{'type': 'text', 'text': "リクエストがPOSTされました。"}]})
    # req = requests.post(url_reply, data=body, headers=headers)
    event = request.forms.get('events')
    # "request success" if req.status_code == 200 else f"Error: {req.status_code}\nDetail: {req.content}"
    print(event)
    return f"Hi, this is Jehanne.\n{event}"


run(host="0.0.0.0", port=int(os.environ.get("PORT", 443)))
