from transformers import pipeline
from functools import lru_cache
from typing import List
import logging

logger = logging.getLogger(__name__)

BATCH_SIZE = 16


# =================================================
# 1. 模型单例（只加载一次）
# =================================================
@lru_cache(maxsize=1)
def get_sentiment_pipeline():
    return pipeline(
        "sentiment-analysis",
        model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
        device=-1,
        truncation=True,
        max_length=128
    )


# =================================================
# 2. 统一分数映射
# =================================================
def score_from(r: dict) -> float:
    label = r["label"].lower()
    score = float(r["score"])

    if "pos" in label:
        return score
    elif "neg" in label:
        return -score
    return 0.0


# =================================================
# 3. 单条（API用）
# =================================================
def analyze_sentiment(text: str) -> float:
    if not text or not text.strip():
        return 0.0

    try:
        pipe = get_sentiment_pipeline()
        result = pipe(text.strip())[0]
        return score_from(result)

    except Exception as e:
        logger.warning(f"single sentiment error: {e}")
        return 0.0


# =================================================
# 4. 批量（核心 crawler 用）
# =================================================
def analyze_sentiments_batch(comments: List[str]) -> List[float]:

    if not comments:
        return []

    pipe = get_sentiment_pipeline()

    results = [0.0] * len(comments)

    valid_indices = []
    valid_texts = []

    # -----------------------------
    # 收集有效数据（保持索引）
    # -----------------------------
    for i, text in enumerate(comments):
        if text and text.strip():
            valid_indices.append(i)
            valid_texts.append(text.strip())

    # -----------------------------
    # batch 推理
    # -----------------------------
    for start in range(0, len(valid_texts), BATCH_SIZE):

        batch_texts = valid_texts[start:start + BATCH_SIZE]
        batch_indices = valid_indices[start:start + BATCH_SIZE]

        try:
            outputs = pipe(batch_texts)

            for idx, r in zip(batch_indices, outputs):
                results[idx] = score_from(r)

        except Exception as e:
            logger.warning(f"batch error: {e}")

            # fallback：逐条
            for idx, t in zip(batch_indices, batch_texts):
                try:
                    r = pipe(t)[0]
                    results[idx] = score_from(r)
                except:
                    results[idx] = 0.0

    return results