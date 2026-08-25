# backend/tests/test_sentiment.py
import pytest
from app.services.sentiment_service import (
    analyze_sentiments_batch,
    score_from
)

# ── score_from 函数测试 ──────────────────────

def test_score_from_positive():
    r = {"label": "positive", "score": 0.95}
    assert score_from(r) == 0.95

def test_score_from_negative():
    r = {"label": "negative", "score": 0.88}
    assert score_from(r) == -0.88

def test_score_from_neutral():
    r = {"label": "neutral", "score": 0.6}
    assert score_from(r) == 0.0

# ── analyze_sentiments_batch 测试 ────────────

def test_empty_input():
    result = analyze_sentiments_batch([])
    assert result == []

def test_output_length_matches_input():
    comments = ["great!", "terrible", "okay"]
    result = analyze_sentiments_batch(comments)
    assert len(result) == 3             # 输出长度必须和输入一致

def test_empty_comment_preserved():
    comments = ["good", "", "bad"]
    result = analyze_sentiments_batch(comments)
    assert len(result) == 3             # 空评论不能被跳过
    assert result[1] == 0.0             # 空评论位置是 0.0

def test_all_empty_comments():
    result = analyze_sentiments_batch(["", "", ""])
    assert result == [0.0, 0.0, 0.0]

def test_score_range():
    comments = ["I love this!", "I hate this!"]
    result = analyze_sentiments_batch(comments)
    for score in result:
        assert -1.0 <= score <= 1.0     # 所有分数在 -1 到 1 之间