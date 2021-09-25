from django.conf import settings
from linebot import LineBotApi
from linebot.models import TextSendMessage
from bs4 import BeautifulSoup
import json
import requests
from functools import reduce

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)

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