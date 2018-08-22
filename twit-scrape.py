import os
from datetime import datetime
import json
import requests
from requests_oauthlib import OAuth1Session
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import httplib2

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


def scrape_twidata(auth):

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
    return tweets, {'result': result, 'detail': f"ステータスコードは{str(status_code)[1:-1]}です。"}


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


def upload_data(auth, fd):
    try:
        f = auth.CreateFile({'title': f"{now.strftime('%m_%d__%y')}.txt"}) if fd == 0 else auth.CreateFile({'id': fd})
        f.SetContentFile(file_path)
        f.Upload()
    except httplib2.ServerNotFoundError:
        return {'result': False, 'detail': "サーバーとの接続に失敗しました。"}
    except:
        return {'result': False, 'detail': "予期せぬエラーしました。"}
    else:
        return {'result': True, 'detail': None}


def push_result(log):
    noty = f"［定時報告］ 現在時刻{hour}時{minute}分\n"
    if log['scrape']['result']:
        if log['upload']['result']:
            noty += "ツイート情報の収集および\ngoogle Driveへのアップロードに成功しました。"
        else:
            noty += f"ツイート情報の収集に成功しました。\ngoogle Driveへのアップロードに失敗しました。\n{log['upload']['detail']}"
    else:
        noty += f"ツイート情報の収集に失敗しました。\n{log['scrape']['detail']}"
    headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {CAT}"}
    dm = json.dumps({'to': MASTER,
                     'messages': [{'type': 'text', 'text': noty}]})
    req = requests.post(url_LINE, data=dm, headers=headers)
    if req.status_code == 200:
        print("success")
    else:
        print(f"Error: {req.status_code}\nDetail: {req.content}")


if __name__ == '__main__':
    # Logs
    logs = {}
    # Twitter
    twitter = OAuth1Session(CK, CS, AT, AS)
    twidata, logs['scrape'] = scrape_twidata(twitter)
    save_twidata(twidata)

    # Drive
    if logs['scrape']['result']:
        gauth = GoogleAuth()
        gauth.CommandLineAuth(GoogleAuth())
        drive = GoogleDrive(gauth)
        file_id = get_id(drive)
        logs['upload'] = upload_data(drive, file_id)
    else:
        logs['upload'] = False

    # result
    push_result(logs)
