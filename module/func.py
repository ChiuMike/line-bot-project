from django.conf import settings

from linebot import LineBotApi
from linebot.models import TextSendMessage

import requests
from functools import reduce

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
cities = ["臺北","新北","桃園","臺中","臺南","高雄","基隆","新竹","嘉義"]  #市
counties = ["苗栗","彰化","南投","雲林","嘉義","屏東","宜蘭","花蓮","臺東","澎湖","金門","連江"]  #縣

def add(need,item):
    need[item['elementName']]=item['time'][0]['parameter']
    return need

def sendUse(event):  #使用說明
    try:
        text1 ='''
查詢天氣：輸入「XXXX天氣如何?」，例如「高雄天氣如何?」
         輸入「XXXX有下雨嗎?」，例如「台中有下雨嗎?」
               '''
        message = TextSendMessage(
            text = text1
        )
        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！請重新輸入。'))

def sendLUIS(event, mtext):  #LUIS
    try:
        r = requests.get('https://linebotproject.cognitiveservices.azure.com/luis/prediction/v3.0/apps/8a396cdc-190f-49e6-aec4-cd31f04029e0/slots/staging/predict?subscription-key=8fa62ff1ff354f64aa1aef460f685dee&verbose=true&show-all-intents=true&log=true&query='
             +mtext) 
        result = r.json()
        if result['prediction']['topIntent']=='縣市天氣':
            if result['prediction']['entities']['$instance']['地點'][0]['type']=="地點":
                city=result['prediction']['entities']['地點'][0]       
        iscity=False #判斷市

        city=city.replace('台','臺')
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
        locationData=reduce(add,locationData)
        target={}
        target["天氣狀況"]=locationData['time'][0]['parameter']['parameterName']
        target["最高溫"]=locationData["MaxT"]['parameterName']+'度'
        target["最低溫"]=locationData["MinT"]['parameterName']+'度'
        target["降雨機率"]=locationData["PoP"]['parameterName']+'%'
        target["舒適度"]=locationData["CI"]['parameterName']
        weather=city+'天氣狀況: '+target["天氣狀況"]+'\n'+'最高溫: '+target["最高溫"]+'\n'+'最低溫: '+target["最低溫"]+'\n'+'降雨機率: '+target["降雨機率"]+'\n'+'舒適度: '+target["舒適度"]+'\n'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=weather))
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='執行時產生錯誤！請重新輸入!'))