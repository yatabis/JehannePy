from datetime import datetime, timedelta, timezone
import os
import requests

LATITUDE = 34.745
LONGTITUDE = 135.498
SECRET_KEY = os.environ.get('DARKSKY_KEY')
JST = timezone(timedelta(hours=+9), 'JST')
NOW = int(datetime.now(JST).timestamp())
DAILY_EP = (f"https://api.darksky.net/forecast/{SECRET_KEY}/{LATITUDE},{LONGTITUDE},{NOW}"
            f"?exclude=[currently,minutely,hourly,alerts]&lang=ja&units=si")


def daily_forecast(response: dict) -> str:
    degree = "ºC"
    error = response['flags'].get('darksky-unavailable', False)
    if error:
        return f"現在Dark Skyのデータを利用することができません。\nエラーメッセージ: {error}"
    else:
        data = response['daily']['data'][0]
        date = datetime.fromtimestamp(data['time']).strftime('%Y年%-m月%-d日')
        summary = data['summary'][:-1]
        icon = data['icon']
        max_temp = data['temperatureMax']
        max_temp_time = datetime.fromtimestamp(data['temperatureMaxTime']).strftime('%k時').lstrip()
        max_temp_apparent = data['apparentTemperatureMax']
        max_temp_apparent_time = datetime.fromtimestamp(data['apparentTemperatureMaxTime']).strftime('%k時').lstrip()
        min_temp = data['temperatureMin']
        min_temp_time = datetime.fromtimestamp(data['temperatureMinTime']).strftime('%k時').lstrip()
        min_temp_apparent = data['apparentTemperatureMin']
        min_temp_apparent_time = datetime.fromtimestamp(data['apparentTemperatureMinTime']).strftime('%k時').lstrip()
        low_temp = data['temperatureLow']
        low_temp_time = datetime.fromtimestamp(data['temperatureLowTime']).strftime('%k時').lstrip()
        low_temp_apparent = data['apparentTemperatureLow']
        uv_index = data['uvIndex']
        uv_index_time = datetime.fromtimestamp(data['uvIndexTime']).strftime('%k時').lstrip()
        forecast = f"{date}の天気予報をお知らせします。\n"
        forecast += f"【{icon}】\n"
        forecast += f"今日は{summary}でしょう。\n"
        forecast += f"最高気温は{max_temp_time}頃に{max_temp}{degree}で、最低気温は{min_temp_time}頃に{min_temp}{degree}です。\n"
        if low_temp < min_temp and low_temp_apparent < min_temp:
            forecast += f"さらに、翌日{low_temp_time}には{low_temp}{degree}まで下がる予報です。"
        if max_temp != max_temp_apparent and min_temp != min_temp_apparent:
            forecast += f"また、体感気温は{max_temp_apparent_time}頃に最高で{max_temp_apparent}{degree}、"
            forecast += f"{min_temp_apparent_time}頃に最低で{min_temp_apparent}{degree}となる予報です。\n"
        forecast += f"今日は{uv_index_time}頃にUV指数が{uv_index}となります。"
        return forecast


def get_daily() -> str:
    req = requests.get(DAILY_EP)
    if req.status_code == 200:
        return daily_forecast(req.json())
    else:
        return f"天気予報の取得に失敗しました。: {req.status_code}"
