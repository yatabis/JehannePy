import json
import os
import re
import ssl
import bs4
from pprint import pprint
import requests
import LINEbot
# from Jehanne import JehanneAI

AT = os.environ['MSTDN_ACCESS_TOKEN']
HEADER = {'Authorization': f"Bearer {AT}"}
EP = "https://mstdn.jp/api/v1/streaming/user"
NERV_ID = '59194'


def alert(data):
    # with open('Jehanne_states.json') as j:
    #     jehanne_states = json.load(j)
    #     alert_tags = jehanne_states['alert_tags']
    alert_tags = ['大阪府', '京都府', '和歌山県', '緊急']
    if data['account']['id'] == NERV_ID and {t['name'] for t in data['tags']}.intersection(alert_tags):
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
    pprint(data)


def error_check(data):
    title = bs4.BeautifulSoup(data, "html.parser").title
    if title and title.getText() == "mstdn.jp | 502: Bad gateway":
        bot = LINEbot.LineMessage()
        bot.push_text("ジャンヌです。現在mstdnのサーバーが停止しているため、速報をお届けできない状況です。")
        return True
    else:
        return False


if __name__ == '__main__':
    req = requests.get(EP, headers=HEADER, stream=True)
    for line in req.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            if error_check(decoded):
                break
            if decoded.startswith('data'):
                alert(json.loads(decoded[6:]))
