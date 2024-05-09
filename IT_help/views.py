from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
 
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage
import requests
import json
import time

# ngrok config add-authtoken 2g7tPTsmnUMaENhuDXegYecgkaz_6jDD1k3LeVjxHsPUzTuzN

# ./ngrok authtoken 'ngrok授權碼'
# ./ngrok http 8000

# venv\Scripts\activate
# python manage.py runserver
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
 
 
@csrf_exempt
def callback(request):
 
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
 
        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
 
        for event in events:
            if isinstance(event, MessageEvent):  # 如果有訊息事件
                line_bot_api.reply_message(  # 回復傳入的訊息文字
                    event.reply_token,
                    TextSendMessage(text=findStock(event.message.text))

                    # TextSendMessage(text=event.message.text)
                )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
    
def findStock(number):
    if number.startswith('6'):
        query_url = f'http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=otc_{number}.tw'
    else:
        query_url = f'http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{number}.tw'

    # 呼叫股票資訊API
    response = requests.get(query_url)

    # 判斷該API呼叫是否成功
    if response.status_code != 200:
        raise Exception('取得股票資訊失敗')

    columns = ['c','n','z','tv','v','o','h','l','y']
    maps = ['股票代號','公司簡稱','成交價','成交量','累積成交量','開盤價','最高價','最低價','昨收價']

    # maps = ['股票代號','公司簡稱','成交價','成交量','累積成交量','開盤價','最高價','最低價','昨收價', '資料更新時間']
    # 將回傳的JSON格式資料轉成Python的dictionary
    try:
        # Attempt to parse the JSON response
        totalResponse = ""
        data = json.loads(response.text)
        if (data['msgArray'] != []):
            for i in range(len(columns)):
                if maps[i] == '資料更新時間':
                    eachResponse = maps[i] + ": " + time2str(data["msgArray"][0][columns[i]]) + '\n'
                else:
                    eachResponse = maps[i] + ": " + data["msgArray"][0][columns[i]] + '\n'
                totalResponse += eachResponse
            eachResponse = "漲跌百分比: " + count_per(data["msgArray"][0]['z'], data["msgArray"][0]['y'])
            totalResponse += eachResponse
            return totalResponse
        else:
            return '取得股票資訊失敗'
    except json.JSONDecodeError as e:
        print(f'JSON decoding error: {e}')
        return "JSON decoding error"
        # return None  # Return None or handle the error as appropriate
# 紀錄更新時間
def time2str(t):
#   print(t)
  t = int(t) / 1000 + 8 * 60 * 60. # UTC時間加8小時為台灣時間
  return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))

def count_per(new, old):
    return str(round((float(new) - float(old)) / float(old) * 100 * 100, 2)) + '%'