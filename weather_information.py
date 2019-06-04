from datetime import datetime, timedelta, timezone
import os
import requests

LATITUDE = 34.745
LONGTITUDE = 135.498
SECRET_KEY = os.environ.get('DARKSKY_KEY')
JST = timezone(timedelta(hours=+9), 'JST')
NOW = int(datetime.now(JST).timestamp())
TODAY = int(datetime(NOW.year, NOW.month, NOW.day, 6).timestamp())
TOMORROW = int(datetime(NOW.year, NOW.month, NOW.day + 1, 6).timestamp())
DAILY_EP = (f"https://api.darksky.net/forecast/{SECRET_KEY}/{LATITUDE},{LONGTITUDE},{NOW}"
            f"?exclude=[currently,minutely,hourly,alerts]&lang=ja&units=si")
HOURLY_EP = [(f"https://api.darksky.net/forecast/{SECRET_KEY}/{LATITUDE},{LONGTITUDE},{ts}"
              f"?exclude=[currently,minutely,daily,alerts]&lang=ja&units=si") for ts in (TODAY, TOMORROW)]


def forecast_chart(forecast: list) -> str:
    degree = "ºC"
    text = "3時間毎の予報です。\n"
    for fc in forecast:
        # pprint(fc)
        time = datetime.fromtimestamp(fc['time']).strftime('%Y年%-m月%-d日%k時')
        summary = fc['summary']
        icon = fc['icon']
        temp = fc['temperature']
        temp_apparent = fc['apparentTemperature']
        humidity = int(fc['humidity'] * 100)
        precip_prob = int(fc['precipProbability'] * 100)
        precip = fc['precipIntensity']
        pressure = fc['pressure']
        wind_speed = fc['windSpeed']
        wind_bearing = fc['windBearing']
        wind_direction = ['南', '南西', '西', '北西', '北', '北東', '東', '南東'][wind_bearing // 45]
        uv_index = fc['uvIndex']
        text += f"時刻：{time}|"
        text += f"{summary} ({icon})|"
        text += f"気温{temp}{degree} ({temp_apparent}{degree})|"
        text += f"湿度{humidity}%|"
        text += f"降水{precip_prob}% ({precip}mm/h)|"
        text += f"気圧{pressure}hPa|"
        text += f"{wind_direction}向きの風{wind_speed}m/s|"
        text += f"UV指数{uv_index}\n"
    return text


def hourly_forecast(response: dict) -> list:
    error = response['flags'].get('darksky-unavailable', False)
    if error:
        on_error(error)
    else:
        ret = []
        data = response['hourly']['data']
        for d in data:
            hour = datetime.fromtimestamp(d['time']).hour
            if i == 0 and hour in (6, 9, 12, 15, 18, 21) or i == 1 and hour in (0, 3):
                ret.append(d)
        return ret


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


def get_hourly() -> str:
    res = []
    for i in (0, 1):
        req = requests.get(HOURLY_EP[i])
        if req.status_code == 200:
            res += hourly_forecast(req.json())
        else:
            return f"天気予報の取得に失敗しました。: {req.status_code}"
    return forecast_chart(res)


def get_daily() -> str:
    req = requests.get(DAILY_EP)
    if req.status_code == 200:
        return daily_forecast(req.json())
    else:
        return f"天気予報の取得に失敗しました。: {req.status_code}"