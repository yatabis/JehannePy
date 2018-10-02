import json
import os
import re
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
            message.add_text(text)
        elif message.type == "image":
            message.add_text("画像を受け取りました。")
            message.add_text("受け取った画像はこちらです：")
            message.add_text("message.add_image")
        elif message.type == "video":
            message.add_text("動画を受け取りました。")
            message.add_text("受け取った動画はこちらです：")
            message.add_text("message.add_video")
        elif message.type == "audio":
            message.add_text("音声を受け取りました。")
            message.add_text("受け取った音声はこちらです：")
            message.add_text("message.add_audio")
        elif message.type == "file":
            message.add_text("ファイルを受け取りました。")
            message.add_text(f"ファイル名は {message.message} です。")
        elif message.type == "sticker":
            message.add_text("スタンプを受け取りました。")
            if int(message.message[0]) in range(1, 5):
                message.add_text("受け取ったスタンプはこちらです：")
                message.add_sticker(*message.message)
            else:
                message.add_text("こちらから送信できないスタンプです。")
        res = message.reply_message()
    return f"Hi, this is Jehanne.\nresponse: {res.content}"


def push_recent_log(days=0):
    with open("dict_data/tweet_data/logs.json") as j:
        logs = json.load(j)
    res = logs['result']['recent'][:days]
    return res


def create_text(message):
    # 名前に対する返事
    if "ジャンヌ" in message:
        reply = "およびですか、マスター。"
    else:
        reply = f"メッセージを受け取りました。\ntext: {message}"

    # ログ出力
    if "ログ" in message:
        numbers = re.findall(r'[0-9]+', message)
        if len(numbers) == 0:
            reply = "直近何日間のログを出力しますか？"
        elif len(numbers) == 1:
            days = int(numbers[0])
            reply = f"直近{days}日間のログを出力します。\n"
            for l in push_recent_log(days):
                reply += f"{l}\n"
        else:
            reply = "正常なログ出力に失敗しました。"

    # ログ出力設定
    if message.startswith("ログ") and "設定" in message:
        with open("dict_data/tweet_data/logs.json") as j:
            log_conf = json.load(j)
        if "hourly" in message or "毎時" in message:
            log_conf['output']['hourly'] = 'オフ' not in message
            reply = f"ログ出力設定 [hourly] を{log_conf['output']['hourly']}にしました。"
        elif "daily" in message or "デイリー" in message or "毎時" in message:
            log_conf['output']['daily'] = 'オフ' not in message
            reply = f"ログ出力設定 [hourly] を{log_conf['output']['daily']}にしました。"
        elif "monthly" in message or "マンスリー" in message or "毎月" in message:
            log_conf['output']['monthly'] = 'オフ' not in message
            reply = f"ログ出力設定 [hourly] を{log_conf['output']['monthly']}にしました。"
        else:
            reply = f"現在のログ出力設定は\n" \
                    f"hourly: {log_conf['output']['hourly']}\n" \
                    f"daily: {log_conf['output']['daily']}\n" \
                    f"monthly: {log_conf['output']['monthly']}\n" \
                    f"です。"
        with open("dict_data/tweet_data/logs.json", 'w') as j:
            json.dump(log_conf, j)

    return reply


if __name__ == '__main__':
    run(host="0.0.0.0", port=int(os.environ.get("PORT", 443)))
