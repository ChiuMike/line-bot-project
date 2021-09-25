from django.conf import settings

from linebot import LineBotApi
from linebot.models import TextSendMessage

import googlemaps
from bs4 import BeautifulSoup
import json
import requests

from functools import reduce

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
cities = ["臺北","新北","桃園","臺中","臺南","高雄","基隆","新竹","嘉義"]  #市
counties = ["苗栗","彰化","南投","雲林","嘉義","屏東","宜蘭","花蓮","臺東","澎湖","金門","連江"]  #縣
GOOGLE_PLACES_API_KEY='AIzaSyBv5_PtgBFnbp9vpQ5l76isoHu0_fGlUUg'
gmaps = googlemaps.Client(GOOGLE_PLACES_API_KEY)

def sendFoodUse(event,mtext):
    try:
        text1 =f'查詢附近餐廳：\n輸入「地址資訊」或「傳送line位置資訊」即可獲得附近評價最高的餐廳資訊喔!'    
        message = TextSendMessage(
            text = text1
        )
        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！請重新輸入。'))

def getstore(event,mtext):
    try:
        geocode = gmaps.geocode(mtext, language='zh-TW')
        lat = geocode[0]['geometry']['location']['lat']
        lng = geocode[0]['geometry']['location']['lng']
        url='https://ifoodie.tw/explore/list?place=current&latlng='+str(lat)+','+str(lng)+'&sortby=rating'
        r=requests.get(url)
        resp=BeautifulSoup(r.text,'lxml')
        store=[]
        content=resp.find_all('div',class_="jsx-3440511973 info-rows")

        for i in content:
            title=i.find('div',class_="jsx-3440511973 title").text
            # spend=i.find('div',class_="jsx-3440511973 avg-price").text.replace('·','')
            address=i.find('div',class_="jsx-3440511973 address-row").text
            opentime=i.find('div',class_="jsx-3440511973 info").text
            category=i.find('div',class_="jsx-3440511973 category-row")
            topic=category.find_all('a',class_="jsx-3440511973 category")
            if len(topic)>1:
                topic=topic[1].text
            else:
                topic=''
            res=title+'(' +topic+')\n'+opentime+'\n地址:'+address+'\n\n'
            store.append(res)
            if len(store)>9:
                break
        msg=''
        for i in store:
            msg=msg+i
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=msg))
    except Exception as e:
        print("錯誤訊息=",e)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="請重新輸入!"))