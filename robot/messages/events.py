# -*- coding: utf-8 -*-

from robot.messages.entries import StringEntry, IntEntry, FloatEntry
from robot.messages.base import RoBotMetaClass


class EventMetaClass(RoBotMetaClass):
    pass

class WeChatEvent(object, metaclass=EventMetaClass):
    target = StringEntry('ToUserName')
    source = StringEntry('FromUserName')
    time = IntEntry('CreateTime')
    message_id = IntEntry('MsgID', 0)

    def __init__(self, message):
        self.__dict__.update(message)

class TicketEvent(WeChatEvent):
    key = StringEntry('EventKey')
    ticket = StringEntry('Ticket')

class SubscribeEvent(TicketEvent):
    __type__ = 'subscribe_event'


class UnSubscribeEvent(WeChatEvent):
    __type__ = 'unsubscribe_event'

class UnknownEvent(WeChatEvent):
    __type__ = 'unknown_event'
