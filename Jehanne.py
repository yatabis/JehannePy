import json
import multiprocessing
import os
import random
import re
import requests
from bottle import route, run, request, auth_basic, HTTPResponse
from pprint import pformat

from typing import Optional

from JehanneTools import *
from LINEbot import LineMessage
from NERV_alert import nerv_alert
from weather_information import get_daily, get_hourly


# Class Define
class JehanneAI:

    """
    TODO
    ----
    1. 名前に対する返事。(yes)
    2. 挨拶に対する返事。(greet)
    2. 定時報告の設定を確認・変更。(log_conf)
    3. NERVアラートのタグの確認・変更。(alert_conf)

    99. その他の簡単な受け答え。(chat)

    Parameters
    ----------
    MASTER : str
        Jehanne's master, yatabis's LINE user ID.
    CAT : str
        Channel Access Token of LINE MessagingAPI.
    states_file : str
        file path of Jehanne's states file.

    idx : int
        serial number ob Jehanne instance.
    debug : bool
        whether debug mode or not.
    state : str
        Jehanne's internal state for determining callback process.
    alert_tags : list of str
        Tags of NERV_alert.
    """

    MASTER = os.environ["MASTER"]
    CAT = os.environ["CHANNEL_ACCESS_TOKEN"]
    num = 0

    def __init__(self):
        JehanneAI.num += 1
        self.idx = JehanneAI.num
        self.status = get_status()
        # self.debug = self._states['debug']
        self.state = self.status['state']
        self.alert_tags = self.status['alert_tags']
        if self.idx == 1:
            launcher = LineMessage()
            launcher.push_text("こんにちは、私の名前はJehanneです。")

    def callback(self, message):

        """
        callback function receiving LINE message.

        Parameters
        ----------
        message : LineMessage object
            received message object.
        """

        text = message.content

        if "state" in text:
            self.state = "state_check"
        elif "アラートタグ" in text:
            self.state = "alert_tags"
        elif "リッチメニュー" in text:
            self.state = "rich_menu"

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
                        message.reply_text(random.choice(kw[1]))
                        flag = 1
                        break
                if flag:
                    break
        elif self.state == "state_check":
            message.add_text("現在のステータスはこちらです")
            state = vars(self)
            # del state['_states']
            message.add_text(pformat(state))
            message.reply_message()
            self.state = "top"
        elif self.state == "alert_tags":
            if "確認" in text:
                reply = "現在のアラートタグはこちらです。\n"
                for tag in self.alert_tags:
                    reply += f"・{tag}\n"
                message.reply_text(reply)
                self.state = "top"
            elif "追加" in text:
                message.reply_text("追加するタグを送信してください。\n複数追加する場合は改行区切りでお願いします。")
                self.state = "alert_tags_append"
            else:
                message.push_text("アラートタグを確認、または追加することができます。")
        elif self.state == "alert_tags_append":
            append_list = text.split()
            self.alert_tags += append_list
            reply = f"以下のタグを追加しました。\n"
            for al in append_list:
                reply += f"・{al}\n"
            message.add_text(reply)
            reply = "現在のアラートタグはこちらです。\n"
            for tag in self.alert_tags:
                reply += f"・{tag}\n"
            message.add_text(reply)
            message.reply_message()
            self.state = "top"
        elif self.state == "rich_menu":
            if "リスト" in text:
                res = self.line_request("GET", ep="https://api.line.me/v2/bot/richmenu/list")
                if res:
                    message.add_text("リッチメニューのリストです。")
                    for r in res['richmenus']:
                        message.add_text(pformat(r))
                message.reply_message()
                self.state = "top"
            elif "デフォルト" in text:
                res = self.line_request(GET, ep="https://api.line.me/v2/bot/user/all/richmenu")
                if res:
                    message.add_text("デフォルトリッチメニューです。")
                    message.add_text(pformat(res))
                message.reply_message()
                self.state = "top"
            elif text.startswith("richmenu-"):
                res = self.line_request("GET", ep=f"https://api.line.me/v2/bot/richmenu/{text}")
                if res:
                    message.reply_text(pformat(res))
                self.state = "top"
            else:
                reply = "リッチメニューのリストを確認する場合は「リスト」を、\n" \
                        "個別のリッチメニューを確認する場合はリッチメニューIDを送信してください。\n" \
                        "また、デフォルトのリッチメニューを確認する場合は「デフォルト」を送信してください。"
                message.reply_text(reply)

        self.state_update()

    @staticmethod
    def line_request(method="GET", ep="", q=None):
        header = {'Authorization': f"Bearer {JehanneAI.CAT}"}
        if method == "GET":
            req = requests.get(ep, params=q, headers=header)
        elif method == "POST":
            req = requests.post(ep, data=q, headers=header)
        else:
            req = requests.Response()
        if req.status_code == 200:
            return req.json()
        else:
            error = LineMessage()
            error.push_text(f"エラー　{req.status_code}\n{pformat(req.json())}")
            return None


# Routing
@route('/callback/line', method='POST')
def callback_line():
    """Line callback"""
    events = request.json['events']
    for event in events:
        if event['type'] == 'postback':
            # jehanne.callback(event['displayText'])
            message = LineMessage()
            message.push_text(json.dumps(event, ensure_ascii=False))
        if not event['type'] == "message":
            continue
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
        message.reply_message()
        if jehanne.debug:
            for k, v in vars(message).items():
                print(f"{k}: {v}")
    return f"Hi, this is Jehanne.\n"


@route('/weather/call', method='GET')
def weather_call() -> HTTPResponse:
    line = LineMessage()
    daily_forecast = get_daily()
    hourly_forecast = get_hourly()
    line.add_text(f"おはようございます。Jehanneです。\n{daily_forecast}")
    line.add_text(hourly_forecast)
    line.push_message()
    return HTTPResponse()


@route('/weather/request', method='GET')
def weather_request() -> HTTPResponse:
    return HTTPResponse("Weather request has not prepared yet.")


@route('/notify', method='POST')
def notify(title: Optional[str] = None, message: Optional[str] = None) -> HTTPResponse:
    """LINE notification"""
    data = request.json
    title = data.get('title', title)
    message = data.get('message', message)
    body = ""
    if title is not None:
        body += f"【{title}】\n"
    if message is not None:
        body += message
    line = LineMessage()
    line.push_text(body)
    return HTTPResponse('OK')


@route('/ping', method='GET')
def ping():
    return HTTPResponse('ping')


def jehanne_start():
    run(host="0.0.0.0", port=int(os.environ.get('PORT', 443)))


if __name__ == '__main__':
    jehanne = JehanneAI()
    process_Jehanne = multiprocessing.Process(target=jehanne_start)
    process_NERV = multiprocessing.Process(target=nerv_alert)
    process_Jehanne.start()
    process_NERV.start()
