# -*- coding:utf-8 -*-
from flask import Flask
from flask import request
import hashlib
import time
import re
import xml.etree.ElementTree as ET
from utils import is_valid_text
from model import predict

WECHAT_TOKEN = "biao"


app = Flask(__name__)

ms_cache = {}
dialogs = {}

@app.route("/weixin", methods=["GET","POST"])
def weixin():
    if request.method == "GET":     # 判断请求方式是GET请求
        my_signature = request.args.get('signature')     # 获取携带的signature参数
        my_timestamp = request.args.get('timestamp')     # 获取携带的timestamp参数
        my_nonce = request.args.get('nonce')        # 获取携带的nonce参数
        my_echostr = request.args.get('echostr')         # 获取携带的echostr参数

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
        createTime = xml.find("CreateTime").text
        # print("data:",fromUser, " ", createTime)
        ms = fromUser+createTime
        # 判断类型并回复
        if msgType == "text" or msgType == "voice":
            content = xml.find('Content').text if msgType == "text" else xml.find('Recognition').text
            print("content:",content)
            if not is_valid_text(content):
                return reply_text(fromUser, toUser, "不好意思，没太明白你的意思")
            if len(fromUser)>31:
                userid = str(fromUser[0:30])
            else:
                userid = str(fromUser)
            userid=re.sub(r'[^A-Za-z0-9]+', '', userid)
            
            dialog = dialogs[userid] if userid in dialogs else []
            u_cache = ms_cache[userid] if userid in ms_cache else {}
            if createTime in u_cache:
                print("不是第一次了")
                reply = u_cache[createTime]
                if reply:
                    if len(u_cache) >= 10:
                        u_cache.clear()
                    return reply_text(fromUser, toUser, reply)
                else:
                    reply_text(fromUser, toUser, "不好意思，没太明白你的意思")
                return reply_text(fromUser, toUser, predict_replay_text)
            print("第一次请求")
            try:
                reply, dialog_new = predict(content, dialog)
                if reply:
                    u_cache[createTime] = reply
                    ms_cache[userid] = u_cache
                    if len(dialog_new) > 8: # 缓存当前4轮对话
                        del(dialog_new[0])
                        del(dialog_new[0])
                    dialogs[userid] = dialog_new
                    return reply_text(fromUser, toUser, reply)
            except:
                print("生成回复过程有异常")
                pass
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
            return reply_text(fromUser, toUser, "我目前只能看懂文字哦~")

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
    app.run(host="0.0.0.0",port=8000, debug=True)
