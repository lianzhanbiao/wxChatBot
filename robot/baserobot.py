# -*- coding: utf-8 -*-

import warnings

from robot.config import Config, ConfigAttribute
from robot.parser import parse_xml, process_message
from robot.replies import process_function_reply
from robot.utils import (
    to_binary, to_text, check_signature, cached_property,
    is_regex
)

from inspect import signature

__all__ = ['BaseRoBot', 'FRoBot']

_DEFAULT_CONFIG = dict(
    TOKEN=None,
    SESSION_STORAGE=None,
)


class BaseRoBot(object):
    """
    BaseRoBot 是整个应用的核心对象，负责提供 handler 的维护，消息和事件的处理等核心功能。

    :param config: 用来设置的 :class:`werobot.config.Config` 对象 \\

    .. note:: 对于下面的参数推荐使用 :class:`~werobot.config.Config` 进行设置，\

    :param token: 微信公众号设置的 token **(deprecated)**
    :param enable_session: 是否开启 session **(deprecated)**
    :param session_storage: 用来储存 session 的对象
    """
    message_types = [
        'subscribe_event',
        'unsubscribe_event',
        'text',
        'image',
        'link',
        'voice',
        'unknown',
        'video',
    ]

    token = ConfigAttribute("TOKEN")
    session_storage = ConfigAttribute("SESSION_STORAGE")

    def __init__(
        self,
        token=None,
        enable_session=None,
        session_storage=None,
        config=None,
        **kwargs
    ):

        self._handlers = {k: [] for k in self.message_types}
        self._handlers['all'] = []


        if config is None:
            self.config = Config(_DEFAULT_CONFIG)
            self.config.update(
                TOKEN=token,
            )
            for k, v in kwargs.items():
                self.config[k.upper()] = v

            if not enable_session:
                self.config["SESSION_STORAGE"] = False

            if session_storage:
                self.config["SESSION_STORAGE"] = session_storage
        else:
            self.config = config


    @cached_property
    def session_storage(self):
        if self.config["SESSION_STORAGE"] is False:
            return None
        if not self.config["SESSION_STORAGE"]:
            from .session.sqlitestorage import SQLiteStorage
            self.config["SESSION_STORAGE"] = SQLiteStorage()
        return self.config["SESSION_STORAGE"]

    @session_storage.setter
    def session_storage(self, value):
        warnings.warn(
            "You should set session storage in config",
            DeprecationWarning,
            stacklevel=2
        )
        self.config["SESSION_STORAGE"] = value

    def handler(self, f):
        """
        为每一条消息或事件添加一个 handler 方法的装饰器。
        """
        self.add_handler(f, type='all')
        return f

    def text(self, f):
        """
        为文本 ``(text)`` 消息添加一个 handler 方法的装饰器。
        """
        self.add_handler(f, type='text')
        return f

    def image(self, f):
        """
        为图像 ``(image)`` 消息添加一个 handler 方法的装饰器。
        """
        self.add_handler(f, type='image')
        return f

    def link(self, f):
        """
        为链接 ``(link)`` 消息添加一个 handler 方法的装饰器。
        """
        self.add_handler(f, type='link')
        return f

    def voice(self, f):
        """
        为语音 ``(voice)`` 消息添加一个 handler 方法的装饰器。
        """
        self.add_handler(f, type='voice')
        return f

    def video(self, f):
        """
        为视频 ``(video)`` 消息添加一个 handler 方法的装饰器。
        """
        self.add_handler(f, type='video')
        return f

    def subscribe(self, f):
        """
        为被关注 ``(subscribe)`` 事件添加一个 handler 方法的装饰器。
        """
        self.add_handler(f, type='subscribe_event')
        return f

    def unsubscribe(self, f):
        """
        为被取消关注 ``(unsubscribe)`` 事件添加一个 handler 方法的装饰器。
        """
        self.add_handler(f, type='unsubscribe_event')
        return f

    def filter(self, *args):
        """
        为文本 ``(text)`` 消息添加 handler 的简便方法。

        使用 ``@filter("xxx")``, ``@filter(re.compile("xxx"))``
        或 ``@filter("xxx", "xxx2")`` 的形式为特定内容添加 handler。
        """
        def wraps(f):
            self.add_filter(func=f, rules=list(args))
            return f

        return wraps

    def add_handler(self, func, type='all'):
        """
        为 BaseRoBot 实例添加一个 handler。

        :param func: 要作为 handler 的方法。
        :param type: handler 的种类。
        :return: None
        """
        if not callable(func):
            raise ValueError("{} is not callable".format(func))

        self._handlers[type].append(
            (func, len(signature(func).parameters.keys()))
        )

    def get_handlers(self, type):
        return self._handlers.get(type, []) + self._handlers['all']

    def add_filter(self, func, rules):
        """
        为 BaseRoBot 添加一个 ``filter handler``。

        :param func: 如果 rules 通过，则处理该消息的 handler。
        :param rules: 一个 list，包含要匹配的字符串或者正则表达式。
        :return: None
        """
        if not callable(func):
            raise ValueError("{} is not callable".format(func))
        if not isinstance(rules, list):
            raise ValueError("{} is not list".format(rules))
        if len(rules) > 1:
            for x in rules:
                self.add_filter(func, [x])
        else:
            target_content = rules[0]
            if isinstance(target_content, str):
                target_content = to_text(target_content)

                def _check_content(message):
                    return message.content == target_content
            elif is_regex(target_content):

                def _check_content(message):
                    return target_content.match(message.content)
            else:
                raise TypeError("%s is not a valid rule" % target_content)
            argc = len(signature(func).parameters.keys())

            @self.text
            def _f(message, session=None):
                _check_result = _check_content(message)
                if _check_result:
                    if isinstance(_check_result, bool):
                        _check_result = None
                    return func(*[message, session, _check_result][:argc])

    def parse_message(
        self, body, timestamp=None, nonce=None, msg_signature=None
    ):
        """
        解析获取到的 Raw XML。
        :param body: 微信服务器发来的请求中的 Body。
        :return: WeRoBot Message
        """
        message_dict = parse_xml(body)
        return process_message(message_dict)

    def get_reply(self, message):
        """
        根据 message 的内容获取 Reply 对象。

        :param message: 要处理的 message
        :return: 获取的 Reply 对象
        """

        session_storage = self.session_storage

        id = None
        session = None
        if session_storage and hasattr(message, "source"):
            id = to_binary(message.source)
            session = session_storage[id]

        handlers = self.get_handlers(message.type)
        try:
            for handler, args_count in handlers:
                args = [message, session][:args_count]
                reply = handler(*args)
                if session_storage and id:
                    session_storage[id] = session
                if reply:
                    return process_function_reply(reply, message=message).render()
        except:
            pass


    def check_signature(self, timestamp, nonce, signature):
        """
        根据时间戳和生成签名的字符串 (nonce) 检查签名。

        :param timestamp: 时间戳
        :param nonce: 生成签名的随机字符串
        :param signature: 要检查的签名
        :return: 如果签名合法将返回 ``True``，不合法将返回 ``False``
        """
        return check_signature(
            self.config["TOKEN"], timestamp, nonce, signature
        )


class FRoBot(BaseRoBot):
    """
    FRoBot 是一个继承自 BaseRoBot 的对象，在 BaseRoBot 的基础上使用了 flask 框架，
    提供接收微信服务器发来的请求的功能。
    """
    @cached_property
    def wsgi(self):
        if not self._handlers:
            raise RuntimeError('No Handler.')
        from flask import Flask
        from robot.flask import make_view

        app = Flask(__name__)
        app.add_url_rule(rule='/weixin/', # WeRoBot 挂载地址
                 #endpoint='helloo', # Flask 的 endpoint
                 view_func=make_view(self),
                 methods=['GET', 'POST'])
        return app
