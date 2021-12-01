# -*- coding:utf-8 -*-
import werobot
import predict
# from werobot.utils import to_binary
import redis
from werobot.session.redisstorage import RedisStorage
import re


db = redis.Redis()
session_storage = RedisStorage(db, prefix="my_prefix_")
robot = werobot.WeRoBot(token="biao", enable_session=True,
                        session_storage=session_storage)


@robot.filter(re.compile(".*?讲个故事.*?"), "讲故事")
def story():
    return "你是要听故事吗？"


@robot.text
def r_text(message, session):
    dialog = session.get("dialog", [])
    reply, new_dialog = predict.predict(message.content, dialog)
    session['dialog'] = new_dialog
    return reply


@robot.image
def r_image(message, session):
    return message.img

robot.config['HOST'] = '0.0.0.0'
robot.config['PORT'] = 8000

robot.run()