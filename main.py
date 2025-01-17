from datetime import datetime, timedelta
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
import requests
import os
import random
import json
from zhdate import ZhDate as lunar_date

nowtime = datetime.utcnow() + timedelta(hours=8)  
today = datetime.strptime(str(nowtime.date()), "%Y-%m-%d")

app_id = os.getenv("APP_ID")
app_secret = os.getenv("APP_SECRET")
template_id = os.getenv("TEMPLATE_ID")
DAILY_KEY_STR = "5e08bea90f6a43ad88511ba9d88cc722"

def get_time():
    dictDate = {'Monday': '星期一', 'Tuesday': '星期二', 'Wednesday': '星期三', 'Thursday': '星期四',
                'Friday': '星期五', 'Saturday': '星期六', 'Sunday': '星期天'}
    a = dictDate[nowtime.strftime('%A')]
    return nowtime.strftime("%Y年%m月%d日 %H时%M分 ")+ a

def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code != 200:
        return get_words()
    return words.json()['data']['text']

def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)

def get_city_id(city):
    url = "https://geoapi.qweather.com/v2/city/lookup?location=" + city + "&key=" + DAILY_KEY_STR
    res = requests.get(url).json()
    id = res['location'][0]['id']
    # print(id)
    return id

def get_weather(city_id):
    url = "https://devapi.qweather.com/v7/weather/3d?location=" + city_id + "&key=" + DAILY_KEY_STR
    #print(url)
    res = requests.get(url).json()
    weather = res['daily'][0]
    # print(weather)
    return weather

def get_air_quality(city_id):
    url = "https://devapi.qweather.com/v7/air/5d?location=" + city_id + "&key=" + DAILY_KEY_STR
    #print(url)
    res = requests.get(url).json()
    air = res['daily'][0]
    # print(air)
    return air

def get_ultroviolet(city_id):
    url = "https://devapi.qweather.com/v7/indices/1d?type=5&location="+ city_id + "&key=" + DAILY_KEY_STR
    #print(url)
    res = requests.get(url).json()
    uv = res['daily'][0]
    #print(uv)
    return uv

def get_count(born_date):
    # 农历转阳历
    year = int(born_date.split("-")[0])
    month = int(born_date.split("-")[1])
    day = int(born_date.split("-")[2])
    date_yangli = lunar_date(year, month, day)  # 农历
    # print("y=%d, m=%d, d=%d" %(year, month, day))
    ymd_yangli = str(date_yangli.to_datetime()).split(" ")[0]
    # print("born_date yl = %s" % ymd_yangli)
    delta = today - datetime.strptime(ymd_yangli, "%Y-%m-%d")
    # print("delta %d" %delta.days)
    return delta.days


def get_birthday(birthday):
    nextdate = datetime.strptime(str(today.year) + "-" + birthday, "%Y-%m-%d")
    next_ymd_nongli = str(nextdate).split(" ")[0]
    year = int(next_ymd_nongli.split("-")[0])
    month = int(next_ymd_nongli.split("-")[1])
    day = int(next_ymd_nongli.split("-")[2])
    next_yangli = lunar_date(year, month, day)
    next_ymd_yangli = next_yangli.to_datetime()
    # print("next_ymd_yangli--- %s, %s" %(type(next_ymd_yangli), next_ymd_yangli))
    # print("type %s, next: %s, y=%d, m=%d, d=%d" %(type(nextdate), nextdate, year, month, day))
    if next_ymd_yangli < today:
        nextdate = nextdate.replace(year=nextdate.year + 1)  # next year
        next2_ymd_nongli = str(nextdate).split(" ")[0]
        year2 = int(next2_ymd_nongli.split("-")[0])
        month2 = int(next2_ymd_nongli.split("-")[1])
        day2 = int(next2_ymd_nongli.split("-")[2])
        next2_yangli = lunar_date(year2, month2, day2)
        next_ymd_yangli = next2_yangli.to_datetime()
        # print("2.next %s, %s, (%d-%d-%d), %s" %(type(nextdate), nextdate, year2, month2, day2, next_ymd_yangli))
    rev = (next_ymd_yangli - today).days
    # print("rev = %s, %s" %(type(rev), rev))
    return rev

client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)

f = open("./users_info.json", encoding="utf-8")
js_text = json.load(f)
f.close()
data = js_text['data']
num = 0
for user_info in data:
    born_date = user_info['born_date']
    birthday = born_date[5:]
    city = user_info['city']
    user_id = user_info['user_id']
    name=user_info['user_name'].upper()

    city_id = get_city_id(city)
    weather = get_weather(city_id)
    air = get_air_quality(city_id)
    uv = get_ultroviolet(city_id)

    data = dict()
    data['time'] = {
        'value': get_time(), 
        'color':'#470024'
        }
    data['words'] = {
        'value': get_words(), 
        'color': get_random_color()
        }
    data['weather'] = {
        'value': weather['textDay'],
        'color': '#002fa4'
        }
    data['city'] = {
        'value': city, 
        'color': get_random_color()
        }
    data['tem_high'] = {
        'value': weather['tempMax'],
        'color': '#D44848'
        }
    data['tem_low'] = {
        'value': weather['tempMin'],
        'color': '#01847F'
        }
    data['born_days'] = {
        'value': get_count(born_date), 
        'color': get_random_color()
        }
    data['birthday_left'] = {
        'value': get_birthday(birthday), 
        'color': get_random_color()
        }
    data['air'] = {
        'value': air['category'],
        'color': get_random_color()
        }
    data['wind'] = {
        'value': weather['windDirDay'],
        'color': get_random_color()
        }
    data['name'] = {
        'value': name, 
        'color': get_random_color()
        }
    data['uv'] = {
        'value': uv['category'],
        'color': get_random_color()
        }
    
    res = wm.send_template(user_id, template_id, data)
    print(res)
    num += 1
print(num)
