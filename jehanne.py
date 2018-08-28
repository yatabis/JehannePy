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
            message.reply_text(text)
        elif message.type == "image":
            message.reply_text("画像を受け取りました。")
            message.reply_text("受け取った画像はこちらです：")
            message.reply_text("message.reply_image")
        elif message.type == "video":
            message.reply_text("動画を受け取りました。")
            message.reply_text("受け取った動画はこちらです：")
            message.reply_text("message.reply_video")
        elif message.type == "audio":
            message.reply_text("音声を受け取りました。")
            message.reply_text("受け取った音声はこちらです：")
            message.reply_text("message.reply_audio")
        elif message.type == "file":
            message.reply_text("ファイルを受け取りました。")
            message.reply_text(f"ファイル名は {message.message} です。")
        elif message.type == "sticker":
            message.reply_text("スタンプを受け取りました。")
            if int(message.message[0]) in range(1, 5):
                message.reply_text("受け取ったスタンプはこちらです：")
                message.reply_sticker(*message.message)
            else:
                message.reply_text("こちらから送信できないスタンプです。")
        res = message.send_reply()
    return f"Hi, this is Jehanne.\nresponse: {res}"


def create_text(message):
    if "ジャンヌ" in message:
        reply = "およびですか、マスター。"
    else:
        reply = f"メッセージを受け取りました。\ntext: {message}"
    return reply


run(host="0.0.0.0", port=int(os.environ.get("PORT", 443)))
