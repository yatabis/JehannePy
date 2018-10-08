import os
import requests
import LINEbot

BASE_URL = "https://api.heroku.com/apps/jehanne/dynos"
DYNO = "worker.1"
API_KEY = os.environ['API_KEY']
HEADER = {"Content-Type": "application/json",
          "Accept": "application/vnd.heroku+json; version=3",
          "Authorization": f"Bearer {API_KEY}"}

bot = LINEbot.LineMessage()
req = requests.get(f"{BASE_URL}/{DYNO}", headers=HEADER)
if req.status_code == 200:
    state = req.json()['state']
    if not state == 'up':
        bot.push_text(f"【supervisor】\n{DYNO}のstateが{state}になっていました。")

        req = requests.delete(f"{BASE_URL}/{DYNO}", headers=HEADER)
        if not req.status_code == 202:
            bot.push_text(f"【supervisor】\n{DYNO}のstate変更に失敗しました。\nstatus code: {req.status_code}")
else:
    bot.push_text(f"【supervisor】\n{DYNO}のstate取得に失敗しました。\nstatus code: {req.status_code}")
