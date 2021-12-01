# -*- coding:utf-8 -*-
class predict_arg:
    def __init__(self):
        self.device = '0'
        self.temperature = 1 # 生成的temperature
        self.topk = 8
        self.topp = 0
        self.vocab_path = "../vocab/vocab.txt"
        self.model_path = "../gpt2model/"
        self.repetition_penalty = 1.0
        self.max_len = 25 # 每个utterance的最大长度,超过指定长度则进行截断
        self.max_history_len = 3 # dialogue history的最大长度
        self.no_cude = True
