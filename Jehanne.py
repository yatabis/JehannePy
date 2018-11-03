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
        self.debug = _states['debug']
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

    def callback(self, message):
        """
        メッセージを受け取った時のコールバック関数

        :param message: received message object.
        :return:
        """

        text = message.message

        if "state" in text:
            self.state = "state_check"
        elif "アラートタグ" in text:
            self.state = "alert_tags"

        if self.state == "top":
            keyword = [
                [["おはよう", ], ["はい、おはようございます。マスター。", "おはようございます。気分はどうですか？"]],
                [["おやすみ", ], ["おやすみなさい、マスター。", "おやすみなさい。良い眠りを...💤"]],
                [["ジャンヌ", "じゃんぬ", "Jehanne"], ["はい、何でしょうか、マスター。", "お呼びですか、マスター。"]]
            ]
            flag = 0
            for kw in keyword:
                for k in kw[0]:
                    if k in text:
                        message.push_text(random.choice(kw[1]))
                        flag = 1
                        break
                if flag:
                    break
        elif self.state == "state_check":
            reply = "現在のステータスはこちらです。\n"
            for k, v in vars(self).items():
                reply += f"{k}: {v}\n"
            message.push_text(reply)
            self.state = "top"
        elif self.state == "alert_tags":
            if "確認" in text:
                reply = "現在のアラートタグはこちらです。\n"
                for tag in self.alert_tags:
                    reply += f"・{tag}\n"
                message.push_text(reply)
                self.state = "top"
            elif "追加" in text:
                message.push_text("追加するタグを送信してください。\n複数追加する場合は改行区切りでお願いします。")
                self.state = "alert_tags_append"
            else:
                message.push_text("アラートタグを確認、または追加することができます。")
        elif self.state == "alert_tags_append":
            append_list = text.split()
            self.alert_tags.append(append_list)
            reply = f"以下のタグを追加しました。\n"
            for al in append_list:
                reply += f"・{al}\n"
            message.add_text(reply)
            reply = "現在のアラートタグはこちらです。\n"
            for tag in self.alert_tags:
                reply += f"・{tag}\n"
            message.push_text(reply)
            self.state = "top"
        self.state_update()

    def state_update(self):
        with open(JehanneAI.states_file, 'w') as j:
            json.dump(vars(self), j)


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
            jehanne.callback(message)
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


if __name__ == '__main__':
    jehanne = JehanneAI()
    run(host="0.0.0.0", port=int(os.environ.get('PORT', 443)))
