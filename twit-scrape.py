import os
from datetime import datetime
import json
import requests
from requests_oauthlib import OAuth1Session
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import httplib2
from LINEbot import LineMessage

CK = os.environ["CONSUMER_KEY_J"]
CS = os.environ["CONSUMER_SECRET_J"]
AT = os.environ["ACCESS_TOKEN_J"]
AS = os.environ["ACCESS_SECRET_J"]
CAT = os.environ["CHANNEL_ACCESS_TOKEN"]
MASTER = os.environ["MASTER"]

url_search = "https://api.twitter.com/1.1/search/tweets.json"
url_DM = "https://api.twitter.com/1.1/direct_messages/new.json"
url_LINE = "https://api.line.me/v2/bot/message/push"

now = datetime.now()
hour = now.hour
minute = now.minute

file_name = f"{now.strftime('%m_%d__%y')}.txt"
file_path = f"dict_data/tweet_data/text/{file_name}"


def scrape_twidata(auth, log):

    text = "lang:ja -rt -bot"
    count = 100
    loop = 15
    max_id = None
    tweets = []
    check = 0

    for _ in range(loop):
        params = {"q": text, "count": count, "max_id": max_id}
        req = auth.get(url=url_search, params=params)
        status_code = []
        if req.status_code == 200:
            result = json.loads(req.text)['statuses']
            for r in result:
                tweets.append(r['text'].replace('\n', ''))
            max_id = result[-1]['id'] - 1
            check += 1
        else:
            status_code.append(req.status_code)

    result = check == loop
    log['result'][hour] = 0 if result else 1
    log['scrape']['result'] = result
    log['scrape']['detail'] = f"ステータスコードは{str(status_code)[1:-1]}です。"
    return tweets


def save_twidata(tweets):
    with open(file_path, 'a') as f:
        f.write('\n'.join(tweets))


def get_id(auth):
    file_list = auth.ListFile().GetList()
    for fl in file_list:
        if fl['title'] == file_name:
            fd = fl['id']
            break
    else:
        fd = 0
    return fd


def upload_data(auth, fd, log):
    try:
        f = auth.CreateFile({'title': f"{now.strftime('%m_%d__%y')}.txt"}) if fd == 0 else auth.CreateFile({'id': fd})
        f.SetContentFile(file_path)
        f.Upload()
    except httplib2.ServerNotFoundError:
        log['result'][hour] = 1
        log['upload']['result'] = False
        log['upload']['detail'] = "サーバーとの接続に失敗しました。"
    except:
        log['scraping'][hour] = 1
        log['upload']['result'] = False
        log['upload']['detail'] = "予期せぬエラーが発生しました。"
    else:
        log['scraping'][hour] = 0
        log['upload']['result'] = True
        log['upload']['detail'] = None


def push_result(log):
    line = LineMessage()
    noty = f"［定時報告］ 現在時刻{hour}時{minute}分\n"
    if log['scrape']['result']:
        if log['upload']['result']:
            noty += "ツイート情報の収集および\ngoogle Driveへのアップロードに成功しました。"
        else:
            noty += f"ツイート情報の収集に成功しました。\ngoogle Driveへのアップロードに失敗しました。\n{log['upload']['detail']}"
    else:
        noty += f"ツイート情報の収集に失敗しました。\n{log['scrape']['detail']}"
    line.add_text(noty)
    req = line.push_message()
    if req.status_code == 200:
        print("success")
    else:
        print(f"Error: {req.status_code}\nDetail: {req.content}")


def push_logs(log):
    if sum(log['result']) == 0:
        noty = "本日のデータ収集は全て完了しました。"
    else:
        noty = "本日のデータ収集は一部失敗しました。"
    line = LineMessage()
    line.add_text(noty)
    req = line.push_message()
    if req.status_code == 200:
        print("success")
    else:
        print(f"Error: {req.status_code}\nDetail: {req.content}")


if __name__ == '__main__':
    # Logs
    with open("dict_data/tweet_data/logs.json") as j:
        logs = json.load(j)

    # Twitter
    twitter = OAuth1Session(CK, CS, AT, AS)
    twidata = scrape_twidata(twitter, logs)
    save_twidata(twidata)

    # Drive
    if logs['scrape']['result']:
        gauth = GoogleAuth()
        gauth.CommandLineAuth(GoogleAuth())
        drive = GoogleDrive(gauth)
        file_id = get_id(drive)
        upload_data(drive, file_id, logs)
    else:
        logs['upload'] = False

    # result
    push_result(logs)
    if hour == 23:
        push_logs(logs)
    with open("dict_data/tweet_data/logs.json", 'w') as j:
        json.dump(logs, j)
