from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
import os
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage,LocationSendMessage
from module import func
import json
import requests
# from invoiceapi.models import users
# from module import func

# Create your views here.
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
@csrf_exempt
def callback(request):
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
                print("event=",event)
                mtext = event.message.text
                r = requests.get('https://linebotproject.cognitiveservices.azure.com/luis/prediction/v3.0/apps/8a396cdc-190f-49e6-aec4-cd31f04029e0/slots/staging/predict?subscription-key=8fa62ff1ff354f64aa1aef460f685dee&verbose=true&show-all-intents=true&log=true&query='+mtext) 
                result = r.json()
                score=result['prediction']['intents']['縣市天氣']['score']
                en=result['prediction']['entities']
                # locationtext=event.message.LocationMessage
                if mtext == '你好':
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text='你好'))
                elif mtext =='使用說明':
                    func.sendUse(event,mtext)          
                elif score>=0.95 and '天氣' in en:
                    func.sendLUIS(event,result)
                elif event.message.type=='location':
                    func.getstore(event,events.message.address)
                else:
                    func.getstore(event,mtext)

        return HttpResponse()

    else:
        return HttpResponseBadRequest()