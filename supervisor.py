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
        bot.add_text(f"worker.1のstateが{state}になっていました。")
        bot.push_message()

        req = requests.delete(f"{BASE_URL}/{DYNO}", headers=HEADER)
        if not req.status_code == 202:
            bot.add_text("worker.1のstate変更に失敗しました。")
            bot.push_message()
else:
    bot.add_text(f"worker.1のstate取得に失敗しました。\nstatus code: {req.status_code}")
    bot.push_message()
