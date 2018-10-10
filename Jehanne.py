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

    def __init__(self):
        _states = self.load_states()
        self.log_twitter = _states['log_twitter']
        self.log_mastodon = _states['log_mastodon']
        self.log_wikipedia = _states['log_wikipedia']
        self.log_note = _states['log_note']
        self.log_hatena = _states['log_hatena']
        self.alert_tags = _states['alert_tags']

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
        kw = {
            'yes': ["Jehanne", "ジャンヌ", ],
            'greet': ["おはよう", "おやすみ", ],
            'log_conf': ["log", "ログ", ],
            'alert_conf': ["NERV", "nerv", "alert", "アラート"],
        }
        for k in kw:
            for l in kw[k]:
                if l in text:
                    eval(f"self.{k}")(text)
                    break

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

    @state_change
    def log_conf(self, text):
        kw = {
            'twitter': [],
            'mastodon': [],
            'Wikipedia': [],
            'hatena': [],
            'note': [],
        }

    @state_change
    def alert_conf(self, text):
        pass

    def chat(self, text):
        """
        その他の簡単な受け答えをする関数

        :param text:
        :return:
        """
        return text

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
        if not message.room == "user" or not message.sender == MASTER:
            return "こんにちは、私の名前はJehanneです。\n申し訳ありませんが、現在メッセージを受け取ることができません。"
        if message.type == "text":
            jehanne.callback(message.message)
            res = None
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
            reply = f"ログ出力設定 [daily] を{log_conf['output']['daily']}にしました。"
        elif "monthly" in message or "マンスリー" in message or "毎月" in message:
            log_conf['output']['monthly'] = 'オフ' not in message
            reply = f"ログ出力設定 [monthly] を{log_conf['output']['monthly']}にしました。"
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
    jehanne = JehanneAI()
    if os.environ.get('APP_LOCATION') == 'heroku':
        run(host="0.0.0.0", port=int(os.environ.get('PORT', 443)))
    else:
        run(port=8080, reloader=True, debug=True)
