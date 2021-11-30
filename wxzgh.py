# -*- coding:utf-8 -*-
from flask import Flask
from flask import request
import hashlib
import time
import re
import xml.etree.ElementTree as ET
import predict

WECHAT_TOKEN = "biao"


app = Flask(__name__)

@app.route("/")
def index():
    return "Hello World!"

@app.route("/weixin", methods=["GET","POST"])
def weixin():
    if request.method == "GET":     # 判断请求方式是GET请求
        my_signature = request.args.get('signature')     # 获取携带的signature参数
        my_timestamp = request.args.get('timestamp')     # 获取携带的timestamp参数
        my_nonce = request.args.get('nonce')        # 获取携带的nonce参数
        my_echostr = request.args.get('echostr')         # 获取携带的echostr参数
        print(my_signature)
        print(my_timestamp)
        print(my_nonce)
        print(my_echostr)


        # 进行字典排序
        data = [WECHAT_TOKEN,my_timestamp ,my_nonce ]
        data.sort()
        # 拼接成字符串,进行hash加密时需为字符串
        data = ''.join(data)
        #创建一个hash对象
        s = hashlib.sha1()
        #对创建的hash对象更新需要加密的字符串
        s.update(data.encode("utf-8"))
        #加密处理
        mysignature = s.hexdigest()

        # print("handle/GET func: mysignature, my_signature: ", mysignature, my_signature)

        # 加密后的字符串可与signature对比，标识该请求来源于微信
        if my_signature == mysignature:
            return my_echostr
        else:
            return ""
    else:
        # 解析xml
        xml = ET.fromstring(request.data)
        toUser = xml.find('ToUserName').text
        fromUser = xml.find('FromUserName').text
        msgType = xml.find("MsgType").text
        # createTime = xml.find("CreateTime")
        # 判断类型并回复
        if msgType == "text":
            content = xml.find('Content').text
            # print(content)
            if len(fromUser)>31:
                userid = str(fromUser[0:30])
            else:
                userid = str(fromUser)
            userid=re.sub(r'[^A-Za-z0-9]+', '', userid)
            # print(reply_userid)
            predict_replay_text = predict.predict(content, userid)
            # print(predict_replay_text)
            return reply_text(fromUser, toUser, predict_replay_text)
        #关注公众号的自动答复
        elif msgType == "event":
            Event = xml.find('Event').text
            if Event == "subscribe":
                subscribe_reply = "欢迎关注，你烦闷时，我还可以陪你聊天解闷哦~"
                return reply_text(fromUser, toUser, subscribe_reply)
        elif msgType == "image":
            mediaId = xml.find('MediaId').text
            return reply_image(fromUser, toUser, mediaId)
        else:
            return reply_text(fromUser, toUser, "我只懂文字")

def reply_text(to_user, from_user, content):
    """
    以文本类型的方式回复请求
    """
    return """
    <xml>
        <ToUserName><![CDATA[{}]]></ToUserName>
        <FromUserName><![CDATA[{}]]></FromUserName>
        <CreateTime>{}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{}]]></Content>
    </xml>
    """.format(to_user, from_user, int(time.time() * 1000), content)
def reply_image(to_user, from_user, mediaId):
    """
    以图片类型的方式回复请求，返回原图片
    """
    return """
    <xml>
        <ToUserName><![CDATA[{}]]></ToUserName>
        <FromUserName><![CDATA[{}]]></FromUserName>
        <CreateTime>{}</CreateTime>
        <MsgType><![CDATA[image]]></MsgType>
        <Image>
        <MediaId><![CDATA[{}]]></MediaId>
        </Image>
    </xml>
    """.format(to_user, from_user, int(time.time() * 1000), mediaId)

if __name__ == "__main__":
    # token = "biao"
    app.run(host="0.0.0.0",port=8000, debug=True)
