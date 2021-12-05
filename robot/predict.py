# -*- coding:utf-8 -*-
import torch
import os
from datetime import datetime
from transformers import GPT2LMHeadModel
from transformers import BertTokenizerFast
import torch.nn.functional as F

PAD = '[PAD]'
pad_id = 0
AUDIENCE_MARK = "[AUDI]"
OWNER_MARK = "[USER]"
NO_IDEA = "啊哦，我好像突然傻掉了呢，请问问标神看看他怎么回答吧"

device = 'cpu'
temperature = 1 # 生成的temperature
topk = 8
topp = 0
vocab_path = "vocab/vocab.txt"
model_path = "gpt2model/"
repetition_penalty = 1.0
max_len = 25 # 每个utterance的最大长度,超过指定长度则进行截断
max_history_len = 3 # dialogue history的最大长度


def top_k_top_p_filtering(logits, top_k=0, top_p=0.0, filter_value=-float('Inf')):
    """ Filter a distribution of logits using top-k and/or nucleus (top-p) filtering
        Args:
            logits: logits distribution shape (vocab size)
            top_k > 0: keep only top k tokens with highest probability (top-k filtering).
            top_p > 0.0: keep the top tokens with cumulative probability >= top_p (nucleus filtering).
                Nucleus filtering is described in Holtzman et al. (http://arxiv.org/abs/1904.09751)
        From: https://gist.github.com/thomwolf/1a5a29f6962089e871b94cbd09daf317
    """
    assert logits.dim() == 1  # batch size 1 for now - could be updated for more but the code would be less clear
    top_k = min(top_k, logits.size(-1))  # Safety check
    if top_k > 0:
        # Remove all tokens with a probability less than the last token of the top-k
        # torch.topk()返回最后一维最大的top_k个元素，返回值为二维(values,indices)
        # ...表示其他维度由计算机自行推断
        indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
        logits[indices_to_remove] = filter_value  # 对于topk之外的其他元素的logits值设为负无穷

    if top_p > 0.0:
        sorted_logits, sorted_indices = torch.sort(logits, descending=True)  # 对logits进行递减排序
        cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)

        sorted_indices_to_remove = cumulative_probs > top_p
        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
        sorted_indices_to_remove[..., 0] = 0

        indices_to_remove = sorted_indices[sorted_indices_to_remove]
        logits[indices_to_remove] = filter_value
    return logits


def predict(text, dialog):
    # os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    tokenizer = BertTokenizerFast(vocab_file=vocab_path, sep_token="[SEP]", pad_token="[PAD]", cls_token="[CLS]", do_lower_case=False, additional_special_tokens=["[AUDI]","[USER]"])
    model = GPT2LMHeadModel.from_pretrained(model_path)
    model = model.to(device)
    model.eval()

    
    history = dialog
    # text = "你好"
    text = OWNER_MARK + text
    text_ids = tokenizer.encode(text, add_special_tokens=False)
    history.append(text_ids)
    input_ids = [tokenizer.cls_token_id]  # 每个input以[CLS]为开头

    for history_id, history_utr in enumerate(history[-max_history_len:]):
        input_ids.extend(history_utr)
        input_ids.append(tokenizer.sep_token_id)
    input_ids = torch.tensor(input_ids).long().to(device)
    input_ids = input_ids.unsqueeze(0)
    response = []  # 根据context，生成的response
    # 最多生成max_len个token
    for _ in range(max_len):
        outputs = model(input_ids=input_ids)
        logits = outputs.logits
        next_token_logits = logits[0, -1, :]
        # 对于已生成的结果generated中的每个token添加一个重复惩罚项，降低其生成概率
        for id in set(response):
            next_token_logits[id] /= repetition_penalty
        next_token_logits = next_token_logits / temperature
        # 对于[UNK]的概率设为无穷小，也就是说模型的预测结果不可能是[UNK]这个token
        next_token_logits[tokenizer.convert_tokens_to_ids('[UNK]')] = -float('Inf')
        filtered_logits = top_k_top_p_filtering(next_token_logits, top_k=topk, top_p=topp)
        # torch.multinomial表示从候选集合中无放回地进行抽取num_samples个元素，权重越高，抽到的几率越高，返回元素的下标
        next_token = torch.multinomial(F.softmax(filtered_logits, dim=-1), num_samples=1)
        if next_token == tokenizer.sep_token_id:  # 遇到[SEP]则表明response生成结束
            break
        response.append(next_token.item())
        input_ids = torch.cat((input_ids, next_token.unsqueeze(0)), dim=1)
    history.append(response)
    reply = tokenizer.convert_ids_to_tokens(response)
    if reply[0] != AUDIENCE_MARK:
        reply = [NO_IDEA]
    else:
        reply = reply[1:]
    return "".join(reply), history
