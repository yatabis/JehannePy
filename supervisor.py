import os
import requests
from JehanneTools import get_status, set_status
from LINEbot import LineMessage

BASE_URL = "https://api.heroku.com/apps/jehanne/dynos"
DYNO = "worker.1"
EP = f"{BASE_URL}/{DYNO}"
API_KEY = os.environ['API_KEY']
HEADER = {"Content-Type": "application/json",
          "Accept": "application/vnd.heroku+json; version=3",
          "Authorization": f"Bearer {API_KEY}"}

req = requests.get(EP, headers=HEADER)
bot = LineMessage()
if req.status_code == 200:
    state = req.json()['state']
    if not state == 'up' and not state == get_status('state'):
        bot.push_text(f"【supervisor】\nJehanneのstateが{state}になっていました。")
    if state in ['up', 'idle']:
        req = requests.get("https://jehanne.herokuapp.com/ping")
        if not req.status_code == 200:
            bot.push_text(f"【supervisor】\nJehanneへのpingの送信に失敗しました。\nstatus code: {req.status_code}")
    elif state == 'crashed':
        req = requests.delete(EP, headers=HEADER)
        if not req.status_code == 202:
            bot.push_text(f"【supervisor】\nJehanneのstate変更に失敗しました。\nstatus code: {req.status_code}")
    set_status('state', state)
else:
    bot.push_text(f"【supervisor】\nJehanneのstate取得に失敗しました。\nstatus code: {req.status_code}")
