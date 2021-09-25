from django.conf import settings
from linebot import LineBotApi
from linebot.models import TextSendMessage
from functools import reduce
import googlemaps
from bs4 import BeautifulSoup
import json
import requests

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
cities = ["臺北","新北","桃園","臺中","臺南","高雄","基隆","新竹","嘉義"]  #市
counties = ["苗栗","彰化","南投","雲林","嘉義","屏東","宜蘭","花蓮","臺東","澎湖","金門","連江"]  #縣
GOOGLE_PLACES_API_KEY='AIzaSyBv5_PtgBFnbp9vpQ5l76isoHu0_fGlUUg'
gmaps = googlemaps.Client(GOOGLE_PLACES_API_KEY)

def sendWeatherUse(event,mtext):  #使用說明
    try:
        text1 =f'查詢天氣：\n輸入「縣市名稱」+「天氣詢問詞」\n例如「高雄天氣如何?」例如「台中有下雨嗎?」'
               
        message = TextSendMessage(
            text = text1
        )
        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！請重新輸入。'))

def add(need,item):
    need[item['elementName']]=item['time'][0]['parameter']
    return need


def sendLUIS(event, en):  #LUIS
    try:
        iscity=False #判斷是否為市或縣

        city=en.replace('台','臺')
        if '市' in city:
            iscity=True
        elif '縣' in city:
            iscity=False
        if city in cities:
            city += '市'
            iscity = True
        elif city in counties:  #加上「縣」
            city += '縣'
            iscity = False
        api_link="https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=CWB-0B5EC65C-E060-4E55-96B4-CBD8E27F46E1&format=JSON&locationName="+city
        report =requests.get(api_link).json()
        locationData=report['records']['location'][0]['weatherElement']
        locationData=reduce(add,locationData) #使用reduce取出需要回傳的部分
        target={}
        target["天氣狀況"]=locationData['time'][0]['parameter']['parameterName']
        target["最高溫"]=locationData["MaxT"]['parameterName']+'度'
        target["最低溫"]=locationData["MinT"]['parameterName']+'度'
        target["降雨機率"]=locationData["PoP"]['parameterName']+'%'
        target["舒適度"]=locationData["CI"]['parameterName']
        weather=city+'天氣狀況: '+target["天氣狀況"]+'\n'+'最高溫: '+target["最高溫"]+'\n'+'最低溫: '+target["最低溫"]+'\n'+'降雨機率: '+target["降雨機率"]+'\n'+'舒適度: '+target["舒適度"]
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=weather))
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='無此地點天氣資料!請重新輸入!'))