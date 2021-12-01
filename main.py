# -*- coding:utf-8 -*-
import werobot
from robot import baserobot
from robot.predict import predict
# from werobot.utils import to_binary
import redis
# from werobot.session.redisstorage import RedisStorage
from robot.session.redisstorage import RedisStorage
import re


db = redis.Redis()
session_storage = RedisStorage(db, prefix="my_prefix_")
robot =baserobot.FRoBot(token="biao", enable_session=True,
                        session_storage=session_storage)
app = robot.wsgi


@robot.filter(re.compile(".*?讲个故事.*?"), "讲故事")
def story():
    return "你是要听故事吗？"


@robot.text
def r_text(message, session):
    dialog = session.get("dialog", [])
    reply, new_dialog = predict(message.content, dialog)
    session['dialog'] = new_dialog
    return reply


@robot.image
def r_image(message, session):
    return "我现在还不支持图片哦！"

@robot.voice
def r_voice(message, session):
    return "我现在还不支持语音哦！"

@robot.video
def r_video(message, session):
    return "我现在还不支持视频哦！"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8000')