import json
import os
import random
import re
import requests
from bottle import route, run, request, response, auth_basic, abort

from LINEbot import LineMessage
from JehanneTools import state_change


# Class Define
class JehanneAI:
    """
    機能：
    1. 名前に対する返事。(yes)
    2. 挨拶に対する返事。(greet)
    2. 定時報告の設定を確認・変更。(log_conf)
    3. NERVアラートのタグの確認・変更。(alert_conf)

    99. その他の簡単な受け答え。(chat)

    :param MASTER: Jehanne's master, yatabis.
    :param CAS: Channel Access Token of LINE bot.
    :param states_file: file path of Jehanne's states file.
    :param alert_tags: Tags of NERV_alert.
    """
    MASTER = os.environ["MASTER"]
    CAT = os.environ["CHANNEL_ACCESS_TOKEN"]
    states_file = "Jehanne_states.json"
    num = 0

    def __init__(self):
        _states = self.load_states()
        self.idx = JehanneAI.num
        self.state = _states['state']
        self.log_twitter = _states['log_twitter']
        self.log_mastodon = _states['log_mastodon']
        self.log_wikipedia = _states['log_wikipedia']
        self.alert_tags = _states['alert_tags']
        JehanneAI.num += 1

    def load_states(self):
        with open(self.states_file) as j:
            states = json.load(j)
        return states

    def callback(self, text):
        """
        メッセージを受け取った時のコールバック関数

        :param text: received text.
        :return:
        """
        if state == "alert_tag":
            pass
        else:
            self.chat(text)

    def state_check(self):
        reply = "私の現在のstatesです。\n"
        for k, v in vars(self).items():
            reply += f"{k}: {v}\n"
        self.push_line(reply)

    def yes(self, text):
        reply = [
            "およびですか、マスター。",
        ]
        self.push_line(random.choice(reply))

    def greet(self, text):
        morning = [
            "はい、おはようございます、マスター。",
        ]
        night = [
            "はい、おやすみなさい、マスター。"
        ]
        if "おはよう" in text:
            self.push_line(random.choice(morning))
        elif "おやすみ" in text:
            self.push_line(random.choice(night))

    def chat(self, text):
        """
        その他の簡単な受け答えをする関数

        :param text:
        :return:
        """
        self.push_line(f"【テスト】以下のテキストを受け取りました。\n{text}")

    @staticmethod
    def push_line(text):
        bot = LineMessage()
        bot.push_text(text)


# Routing
@route('/api/<state>')
@auth_basic(lambda x, y: x == JehanneAI.MASTER and y == JehanneAI.CAT)
def get_state(state):
    """API"""
    print(request.auth)
    if state in vars(jehanne):
        response.headers['Content-Type'] = 'application/json'
        return json.dumps(vars(jehanne)[state], ensure_ascii=False)
    elif state == "states":
        response.headers['Content-Type'] = 'application/json'
        return json.dumps(list(vars(jehanne).keys()))
    else:
        abort(404)


@route('/callback/line', method='POST')
def callback_line():
    """Line callback"""
    events = request.json['events']
    for event in events:
        if not event['type'] == "message":
            break
        message = LineMessage(event)
        if not message.room == "user" or not message.sender == JehanneAI.MASTER:
            return "こんにちは、私の名前はJehanneです。\n申し訳ありませんが、現在メッセージを受け取ることができません。"
        if message.type == "text":
            jehanne.callback(message.message)
            break
        elif message.type == "image":
            message.add_text("【テスト】画像を受け取りました。")
            message.add_text("受け取った画像はこちらです：")
            message.add_text("message.add_image")
        elif message.type == "video":
            message.add_text("【テスト】動画を受け取りました。")
            message.add_text("受け取った動画はこちらです：")
            message.add_text("message.add_video")
        elif message.type == "audio":
            message.add_text("【テスト】音声を受け取りました。")
            message.add_text("受け取った音声はこちらです：")
            message.add_text("message.add_audio")
        elif message.type == "file":
            message.add_text("【テスト】ファイルを受け取りました。")
            message.add_text(f"ファイル名は {message.message} です。")
        elif message.type == "sticker":
            message.add_text("【テスト】スタンプを受け取りました。")
            if int(message.message[0]) in range(1, 5):
                message.add_text("受け取ったスタンプはこちらです：")
                message.add_sticker(*message.message)
            else:
                message.add_text("こちらから送信できないスタンプです。")
        elif message.type == "postback":
            message.add_text("ポストバックを受け取りました。")
            message.add_text(message.message)
        message.reply_message()
        for k, v in vars(message).items():
            print(f"{k}: {v}")
    return f"Hi, this is Jehanne.\n"


def push_recent_log(days=0):
    with open("dict_data/tweet_data/logs.json") as j:
        logs = json.load(j)
    res = logs['result']['recent'][:days]
    return res


if __name__ == '__main__':
    jehanne = JehanneAI()
    run(host="0.0.0.0", port=int(os.environ.get('PORT', 443)))
