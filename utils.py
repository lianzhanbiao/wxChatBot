# -*- coding:utf-8 -*-

NOT_UNDERSTAND = "不好意思，没太明白你的意思"
EMERGENCY = "这个世界虽然不完美，但总有人守护着你。24小时免费心理危机咨询热线:010-82951332"
NOT_SUPPORT = "我只能看懂文字哦"


def is_valid_text(text):
    return text is not None and len(text) < 50