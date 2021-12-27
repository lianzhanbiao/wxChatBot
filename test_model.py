import os
import pytest
from model import predict
from utils import is_valid_text


def test_predict():
    text = "你好"
    dialog = []
    reply, dialog_new = predict(text, dialog)
    assert is_valid_text(reply)
    assert len(dialog_new) > 0