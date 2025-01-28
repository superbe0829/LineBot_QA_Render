# -*- coding: utf-8 -*-
print()
print("===================================")
print("Program：LineBot_QA_Render_1140128")
print("Author： Chang Pi-Tsao")
print("Created on Jan. 28  2025")
print("===================================")
print()

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os  # 用於讀取環境變數
import requests
import json

# 初始化 Flask 應用程式
app = Flask(__name__)

# Line Bot Token & Secret (從環境變數讀取)
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    raise EnvironmentError("請設定 LINE_CHANNEL_ACCESS_TOKEN 和 LINE_CHANNEL_SECRET 環境變數。")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # Get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # Get request body as text
    body = request.get_data(as_text=True)
    # Handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    # 將用戶的訊息傳送到 Azure Question Answering 服務，並取得回應
    answer = get_answer_from_qa(user_message)
    # 回應用戶
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=answer))

def get_answer_from_qa(user_message):
    # 在這裡串接 Azure 的 Question Answering API
    # endpoint = "Your_QA_Endpoint"
    # key = "Your_QA_API_Key"
    # project_name = "Your_Project_Name"
    # deployment_name = "Your_Deployment_Name"
    endpoint = "https://myqa20250127.cognitiveservices.azure.com"
    key = "2nH8GHtm9rMSnjE7ib5Mr379Bq1XowSRCAiMVVLZu7s5RSAKRVjrJQQJ99BAACYeBjFXJ3w3AAAaACOGBYTv"
    project_name = "MyQA-Test"
    deployment_name = "production"
    url = f"{endpoint}/language/:query-knowledgebases?projectName={project_name}&api-version=2021-10-01&deploymentName={deployment_name}"
    headers = {
    "Ocp-Apim-Subscription-Key": key,
    "Content-Type": "application/json"
    }
    data = {
    "question": user_message,
    "top": 1
    }
    response = requests.post(url, headers=headers, json=data)
    answer = response.json()["answers"][0]["answer"]
    return answer


# 啟動伺服器
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # Render 平台使用的動態 Port
    app.run(host="0.0.0.0", port=port)