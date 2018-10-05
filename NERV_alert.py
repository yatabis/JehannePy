import json
import os
import re
import ssl
import bs4
import requests
import websocket
import LINEbot
from Jehanne import JehanneAI

AT = os.environ['MSTDN_ACCESS_TOKEN']
PORT = os.environ.get('PORT', 443)
ENDPOINT = f'wss://mstdn.jp/api/v1/streaming/?stream=user'
NERV_ID = '59194'
OSAKA_ID = '59958'


def on_open(ws):
    print(f"connected streaming server: {ws.url}")


def on_message(ws, message):
    message = json.loads(message)
    for k in message:
        print(k, message[k])
    if message['event'] == 'update':
        data = json.loads(message['payload'])
        if data['account']['id'] == NERV_ID and JehanneAI.alert_tags[0] in [t['name'] for t in data['tags']]:
            name = data['account']['display_name']
            status_url = data['url']
            content = bs4.BeautifulSoup(re.sub('<br>', "\n", data['content']), "html.parser")
            text = f"　{name}\n{content.p.getText()}"
            media_list = []
            for media in data['media_attachments']:
                media_list.append({
                    'type': media['type'],
                    'url': media['url'],
                    'preview_url': media['preview_url']
                })
            bot = LINEbot.LineMessage()
            bot.add_text("ジャンヌです。NERVからの速報をお届けします。")
            bot.add_text(text)
            bot.push_message()
            for media in media_list:
                if media['type'] == 'image':
                    bot.add_image(media['url'], media['preview_url'])
            bot.push_message()
            bot.add_text(status_url)
            bot.push_message()
        for d in data:
            print(d, data[d])


def on_error(ws, error):
    print(f"Error: {error}")


def on_close(ws):
    print(f"disconnected streaming server: {ws.url}")


if __name__ == '__main__':
    wss = websocket.WebSocketApp(ENDPOINT,
                                 header={'Authorization': f'Bearer {AT}'},
                                 on_open=on_open,
                                 on_message=on_message,
                                 on_error=on_error,
                                 on_close=on_close)
    try:
        wss.run_forever(http_proxy_port=PORT, sslopt={"cert_reqs": ssl.CERT_NONE})
    except KeyboardInterrupt:
        wss.close()
