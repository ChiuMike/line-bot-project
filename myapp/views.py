from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
import os
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
# from linebot.models import MessageEvent, TextSendMessage,LocationSendMessage
from linebot.models import *
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
                            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='你好'))
                        elif mtext =='使用說明':
                            func.sendUse(event,mtext)          
                        elif score>=0.95 and '地點' in result['prediction']['entities']:
                            func.sendLUIS(event,en)
                        elif score>=0.95  and '電影名稱' in result['prediction']['entities']:
                            temp=en
                            line_bot_api.reply_message(  # 回復傳入的訊息文字
                            event.reply_token,
                            TemplateSendMessage(
                                alt_text='Buttons template',
                                template=ButtonsTemplate(
                                    title='選單',
                                    text='請選擇地區',
                                    actions=[
                                        PostbackTemplateAction(
                                            label='基隆',
                                            data='a01/'+temp
                                        ),
                                        PostbackTemplateAction(
                                            label='台北',
                                            data='a02/'+temp
                                        ),
                                        PostbackTemplateAction(
                                            label='桃園',
                                            data='a03/'+temp
                                        ),
                                        PostbackTemplateAction(
                                            label='新竹',
                                            data='a35/'+temp
                                        ),
                                        PostbackTemplateAction(
                                            label='苗栗',
                                            data='a37/'+temp
                                        ),
                                        PostbackTemplateAction(
                                            label='台中',
                                            data='a04/'+temp
                                        ),
                                        PostbackTemplateAction(
                                            label='彰化',
                                            data='a47/'+temp
                                        ),
                                        PostbackTemplateAction(
                                            label='雲林',
                                            data='a45/'+temp
                                        ),
                                        PostbackTemplateAction(
                                            label='嘉義',
                                            data='a05/'+temp
                                        ),
                                        PostbackTemplateAction(
                                            label='台南',
                                            data='a06/'+temp
                                        ),
                                        PostbackTemplateAction(
                                            label='高雄',
                                            data='a07/'+temp
                                        ),
                                        PostbackTemplateAction(
                                            label='屏東',
                                            data='a87/'+temp
                                        ),
                                        PostbackTemplateAction(
                                            label='宜蘭',
                                            data='a39/'+temp
                                        ),
                                        PostbackTemplateAction(
                                            label='花蓮',
                                            data='a38/'+temp
                                        ),
                                        PostbackTemplateAction(
                                            label='台東',
                                            data='a89/'+temp
                                        ),
                                    ]
                                )
                            ))
                        else:
                            func.getstore(event,mtext)   
                            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='錯誤'))
                    except Exception as e:
                        print("錯誤訊息=",e)
                        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='錯誤'))
            elif  isinstance(event, PostbackEvent):
                areaCode=event.postback.data
                func.movieTime(event,areaCode)

        return HttpResponse()

    else:
        return HttpResponseBadRequest()