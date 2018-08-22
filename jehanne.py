import os
from bottle import route, run


@route("/callback", method='POST')
def callback():
    return "callback: Hi, this is Jehanne."


run(host="0.0.0.0", port=int(os.environ.get("PORT", 443)))
