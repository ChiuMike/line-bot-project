from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
import os
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage
from module import func
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
                mtext = event.message
                if mtext.text == '你好':
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text='你好'))
                elif mtext.text =='使用說明':
                    func.sendUse(event,mtext)
                elif mtext.location:
                    text=mtext.location['type']
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text))
                else:
                    func.sendLUIS(event,mtext)

        return HttpResponse()

    else:
        return HttpResponseBadRequest()