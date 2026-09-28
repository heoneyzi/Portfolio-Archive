"""Original answer metrics from MDR2DATA.ipynb, cell 5 (zero-based).

Research notebook authors: Jiheon Kang and Suhwan Jeong (Bi-CoT, 2025).
The normalization and metric functions below are copied without algorithm changes.
"""
import re
import string
from typing import List, Tuple


def normalize_answer(s: str) -> str:
    """SQuAD 스타일 정규화 (소문자, 기사/문장부호 제거, 공백 정리)"""
    def lower(text): return text.lower()
    def remove_punc(text):
        return "".join(ch for ch in text if ch not in set(string.punctuation))
    def remove_articles(text):
        return re.sub(r"\b(a|an|the)\b", " ", text)
    def white_space_fix(text):
        return " ".join(text.split())
    return white_space_fix(remove_articles(remove_punc(lower(s))))

def f1_score(pred: str, gold: str) -> float:
    pred_tokens = normalize_answer(pred).split()
    gold_tokens = normalize_answer(gold).split()
    if len(pred_tokens) == 0 and len(gold_tokens) == 0:
        return 1.0
    if len(pred_tokens) == 0 or len(gold_tokens) == 0:
        return 0.0
    common = {}
    for t in pred_tokens:
        common[t] = common.get(t, 0) + 1
    num_same = 0
    for t in gold_tokens:
        if common.get(t, 0) > 0:
            num_same += 1
            common[t] -= 1
    if num_same == 0:
        return 0.0
    precision = num_same / len(pred_tokens)
    recall = num_same / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)

def exact_match_score(pred: str, gold: str) -> int:
    return int(normalize_answer(pred) == normalize_answer(gold))

def max_over_golds(pred: str, golds: List[str]) -> Tuple[int, float]:
    em = max(exact_match_score(pred, g) for g in golds)
    f1 = max(f1_score(pred, g) for g in golds)
    return em, f1
