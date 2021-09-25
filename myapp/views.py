from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
import os
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
# from linebot.models import MessageEvent, TextSendMessage,LocationSendMessage
from linebot.models import *
import json
import requests
from myapp.models import users
from module import func
from module import invoice
from module import movie
from module import weather

# Create your views here.
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
score=0
en=''
@csrf_exempt
def callback(request):
    global score,en
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        
        for event in events:
            if isinstance(event, MessageEvent):
                userid = event.source.user_id
                if not users.objects.filter(uid=userid).exists():
                    unit = users.objects.create(uid=userid, state='no')
                    unit.save()
                if event.message.type=='location':
                    address = event.message.address
                    print("位置=",address)
                    func.getstore(event,address)
                else:
                    try:
                        mtext = event.message.text
                        r = requests.get('https://linebotproject.cognitiveservices.azure.com/luis/prediction/v3.0/apps/8a396cdc-190f-49e6-aec4-cd31f04029e0/slots/staging/predict?subscription-key=8fa62ff1ff354f64aa1aef460f685dee&verbose=true&show-all-intents=true&log=true&query='+mtext) 
                        result = r.json()
                        if result['prediction']['topIntent']=='縣市天氣':
                            s=result['prediction']['topIntent']
                            score=result['prediction']['intents'][s]['score']
                            en=result['prediction']['entities']['地點'][0]    
                        elif result['prediction']['topIntent']=='moviequery':
                            s=result['prediction']['topIntent']
                            score=result['prediction']['intents'][s]['score']
                            en=result['prediction']['entities']['電影名稱'][0]
                    except:
                        mtext = event.message.text
                    try:
                        if mtext=='你好':
                            text="可以點選圖文選單看看有什麼功能喔!"
                            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=text))
                        elif mtext =='使用說明':
                            func.sendUse(event,mtext)          
                        elif score>0.9 and '地點' in result['prediction']['entities']:
                            weather.sendLUIS(event,en)
                        elif score>=0.95  and '電影名稱' in result['prediction']['entities']:
                            movie.movieTime(event,en)
                        elif mtext=="@movie":
                            movie.new_movies(event)
                        elif mtext=="@weather":
                            weather.sendWeatherUse(event,mtext)
                        elif mtext=="@food":
                            func.sendFoodUse(event,mtext)
                        elif mtext=="@invoice":
                            text=f'此功能會提示您輸入發票後三碼，若後三碼有中獎，就提示您輸入發票前五碼。'                
                            line_bot_api.reply_message(  # 回復傳入的訊息文字
                            event.reply_token,
                            TemplateSendMessage(
                                alt_text='Buttons template',
                                template=ButtonsTemplate(
                                    title='Menu',
                                    text=text,
                                    actions=[
                                        PostbackTemplateAction(
                                            label='本期中獎號碼',
                                            data='本期'
                                        ),
                                        PostbackTemplateAction(
                                            label='前期中獎號碼',
                                            data='前期'
                                        ),
                                        PostbackTemplateAction(
                                            label='輸入發票最後三碼',
                                            data='輸入'
                                        ),
                                    ]
                            )))
                        elif len(mtext) == 3 and mtext.isdigit():
                            invoice.show3digit(event, mtext, userid)
                        elif len(mtext) == 5 and mtext.isdigit():
                            invoice.show5digit(event, mtext, userid)
                        else:
                            func.getstore(event,mtext)   
                            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='執行錯誤，請重新輸入!'))
                    except Exception as e:
                        print("錯誤訊息=",e)
                        text='''您好！
感謝您成為生活小助手的好友！
想要「查詢附近美食」、「發票兌獎」、「查詢天氣」、「查詢電影」都歡迎問我喔!'''
                        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=text))
            
            elif isinstance(event, PostbackEvent):
                if event.postback.data=="本期":
                    invoice.showCurrent(event)
                elif event.postback.data=="前期":
                    invoice.showOld(event)
                elif event.postback.data=="輸入":
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text='請輸入發票最後三碼進行對獎！'))
                else:
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text='執行錯誤，請重新輸入!'))

        return HttpResponse()

    else:
        return HttpResponseBadRequest()