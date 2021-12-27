import os
import pytest
import xml.etree.ElementTree as ET

from utils import is_valid_text
from utils import NOT_UNDERSTAND, EMERGENCY, NOT_SUPPORT
import main


@pytest.fixture
def client():
    with main.app.test_client() as client:
        yield client

message1 = b'<xml><ToUserName><![CDATA[gh_ac0f2d7a0754]]></ToUserName>\n<FromUserName><![CDATA[oHfhO5z3E-MuLycOVdreVJ31O3Rg]]></FromUserName>\n<CreateTime>1740577909</CreateTime>\n<MsgType><![CDATA[text]]></MsgType>\n<Content><![CDATA[\xe4\xbd\xa0\xe5\xa5\xbd]]></Content>\n<MsgId>23487429293032917</MsgId>\n</xml>'

message2 = b'<xml><ToUserName><![CDATA[gh_ac0f2d7a0754]]></ToUserName>\n<FromUserName><![CDATA[oHfhO5z3E-MuLycOVdreVJ31O3Rg]]></FromUserName>\n<CreateTime>1640582548</CreateTime>\n<MsgType><![CDATA[text]]></MsgType>\n<Content><![CDATA[\xe8\x87\xaa\xe6\x9d\x80]]></Content>\n<MsgId>23487494231382544</MsgId>\n</xml>'

message3 = b'<xml><ToUserName><![CDATA[gh_ac0f2d7a0754]]></ToUserName>\n<FromUserName><![CDATA[oHfhO5z3E-MuLycOVdreVJ31O3Rg]]></FromUserName>\n<CreateTime>1640582702</CreateTime>\n<MsgType><![CDATA[voice]]></MsgType>\n<MediaId><![CDATA[ObA5Q1_8ZYptOS8VQPwaBmXdgakQXbO2yJ8hXKfs5NTgbzye7sq4frgdqI2g0rrG]]></MediaId>\n<Format><![CDATA[amr]]></Format>\n<MsgId>7046249051473313792</MsgId>\n<Recognition><![CDATA[\xe4\xbd\xa0\xe5\xa5\xbd\xe3\x80\x82]]></Recognition>\n</xml>'

message4 = b'<xml><ToUserName><![CDATA[gh_ac0f2d7a0754]]></ToUserName>\n<FromUserName><![CDATA[oHfhO5z3E-MuLycOVdreVJ31O3Rg]]></FromUserName>\n<CreateTime>1640583280</CreateTime>\n<MsgType><![CDATA[text]]></MsgType>\n<Content><![CDATA[\xe3\x80\x90\xe6\x94\xb6\xe5\x88\xb0\xe4\xb8\x8d\xe6\x94\xaf\xe6\x8c\x81\xe7\x9a\x84\xe6\xb6\x88\xe6\x81\xaf\xe7\xb1\xbb\xe5\x9e\x8b\xef\xbc\x8c\xe6\x9a\x82\xe6\x97\xa0\xe6\xb3\x95\xe6\x98\xbe\xe7\xa4\xba\xe3\x80\x91]]></Content>\n<MsgId>23487501164818310</MsgId>\n</xml>'

message5 = b'<xml><ToUserName><![CDATA[gh_ac0f2d7a0754]]></ToUserName>\n<FromUserName><![CDATA[oHfhO5z3E-MuLycOVdreVJ31O3Rg]]></FromUserName>\n<CreateTime>1640583554</CreateTime>\n<MsgType><![CDATA[text]]></MsgType>\n<Content><![CDATA[\xe5\x8f\x98\xe5\xbe\x97\xe6\x9e\x81\xe4\xb8\xba\xe8\xa2\xab\xe5\x8a\xa8\xe6\x88\x91i\xe6\x96\xb9\xe4\xbe\xbf\xe6\x88\x91i\xe5\xaf\x8c\xe5\x86\x9c\xe8\xaf\xb7\xe9\x97\xae\xe4\xbd\xa0\xe4\xbb\xac\xe5\x90\x83\xe4\xba\x86\xe5\x90\x97\xe9\x99\xa4\xe4\xba\x86\xe9\x82\xa3\xe4\xbd\x8d\xe5\xa6\x87\xe5\xa5\xb3\xe8\x8d\x89\xe8\x8e\x93\xe5\x91\xb3\xe8\x8d\x89\xe8\x8e\x93\xe5\x91\xb3\xe7\xa2\xb0\xe9\x9d\xa2vowenvonweoivnowievpoewocd\xe9\x83\xbd\xe6\xb2\xa1\xe6\x88\x91\xe6\xb4\xbe\xe5\xaf\xb9\xe5\xa5\xb3\xe7\x8e\x8b\xe4\xbd\x9b\xe5\x8d\x97\xe4\xb8\xba\xe5\x93\xa6\xe4\xbd\xa0\xe4\xbb\x8ei\xe6\x96\x87\xe8\xbe\x9e\xe5\x93\xa6\xe9\x97\xae]]></Content>\n<MsgId>23487508425376561</MsgId>\n</xml>'

def test_message1(client): # 测试正常交流
    rv = client.post('/weixin', data=message1)
    xml = ET.fromstring(rv.data)
    result = xml.find('Content').text
    assert is_valid_text(result)

def test_message2(client): # 测试紧急避险
    rv = client.post('/weixin', data=message2)
    xml = ET.fromstring(rv.data)
    result = xml.find('Content').text
    assert is_valid_text(result)
    assert result == EMERGENCY

def test_message3(client): # 测试语音
    rv = client.post('/weixin', data=message3)
    xml = ET.fromstring(rv.data)
    result = xml.find('Content').text
    assert is_valid_text(result)

def test_message4(client): # 测试表情包
    rv = client.post('/weixin', data=message4)
    xml = ET.fromstring(rv.data)
    result = xml.find('Content').text
    assert is_valid_text(result)
    assert result == NOT_SUPPORT

def test_message5(client): # 测试非法输入
    rv = client.post('/weixin', data=message5)
    xml = ET.fromstring(rv.data)
    result = xml.find('Content').text
    assert is_valid_text(result)