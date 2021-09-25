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

def sendWeatherUse(event,mtext):  #使用說明
    try:
        text1 =f'查詢天氣：\n輸入「縣市名稱」+「天氣詢問詞」\n例如「高雄天氣如何?」例如「台中有下雨嗎?」'
               
        message = TextSendMessage(
            text = text1
        )
        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！請重新輸入。'))

def sendFoodUse(event,mtext):
    try:
        text1 =f'查詢附近餐廳：\n輸入「地址資訊」或「傳送line位置資訊」即可獲得附近評價最高的餐廳資訊喔!'    
        message = TextSendMessage(
            text = text1
        )
        line_bot_api.reply_message(event.reply_token,message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！請重新輸入。'))

def new_movies(event,mtext):
    try:
        url_new='http://www.atmovies.com.tw/movie/new/'
        r=requests.get(url_new)
        resp=BeautifulSoup(r.content,'lxml')
        newMovies=[]
        replyarr=[]
        a_tags = resp.find_all('a')
        for tag in a_tags : 
            if ('/movie/' in tag.get('href')) and (len(tag.get('href')) == 20) and (tag.text != ""):
                newMovies.append(tag.text)
        text = '來看看本週有什麼新片吧 : \n'
        for i, movie in enumerate(newMovies):
            show = f'{i+1}. {movie.split(" ")[0]}' + '\n'
            text += show
        text1 =f'查詢電影：\n輸入「本周新片片名」+「場次資訊」\n例如「xxx場次」或「xxx時刻」或「xxx電影場次」\n即可獲得該片的電影時刻資訊喔!'
        replyarr.append(TextSendMessage(text=text))
        replyarr.append(TextSendMessage(text=text1))
        line_bot_api.reply_message(event.reply_token,replyarr)
        
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='執行時出錯，請重新輸入!'))

def movieTime(event,en):
    try:
        url_new='http://www.atmovies.com.tw/movie/new/'
        r=requests.get(url_new)
        resp=BeautifulSoup(r.content,'lxml')
        a_tags = resp.find_all('a')
        for tag in a_tags:
            if ('/movie/' in tag.get('href')) and en in tag.text:
                name=tag.get('href')
        reply='http://www.atmovies.com.tw/'+name
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply))
    except Exception as e:
        print("錯誤訊息=",e)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='重新輸入電影'))

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
    
def add(need,item):
    need[item['elementName']]=item['time'][0]['parameter']
    return need


def sendLUIS(event, en):  #LUIS
    try:
        iscity=False #判斷市

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
        locationData=reduce(add,locationData)
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