from transformers import pipeline
from functools import lru_cache
from typing import List
from app.core.logger import setup_logger

logger = setup_logger(__name__)

BATCH_SIZE = 16


@lru_cache(maxsize=1)
def get_sentiment_pipeline():
    return pipeline(
        "sentiment-analysis",
        model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
        device=-1,
        truncation=True,
        max_length=128
    )


def score_from(r: dict) -> float:
    label = r["label"].lower()
    score = float(r["score"])
    if "pos" in label:
        return score
    elif "neg" in label:
        return -score
    return 0.0


def analyze_sentiment(text: str) -> float:
    if not text or not text.strip():
        return 0.0
    try:
        pipe = get_sentiment_pipeline()
        result = pipe(text.strip()[:1000])[0]  # ← 加字符预截断
        return score_from(result)
    except Exception as e:
        logger.warning(f"single sentiment error: {e}")
        return 0.0


def analyze_sentiments_batch(comments: List[str]) -> List[float]:
    if not comments:
        return []

    pipe = get_sentiment_pipeline()
    results = [0.0] * len(comments)
    valid_indices = []
    valid_texts = []

    for i, text in enumerate(comments):
        if text and text.strip():
            valid_indices.append(i)
            valid_texts.append(text.strip()[:1000])  # ← 加字符预截断

    for start in range(0, len(valid_texts), BATCH_SIZE):
        batch_texts   = valid_texts[start:start + BATCH_SIZE]
        batch_indices = valid_indices[start:start + BATCH_SIZE]

        try:
            outputs = pipe(batch_texts)
            for idx, r in zip(batch_indices, outputs):
                results[idx] = score_from(r)

        except Exception as e:
            logger.warning(f"batch error at start={start}: {e}")
            for idx, t in zip(batch_indices, batch_texts):
                try:
                    r = pipe(t)[0]
                    results[idx] = score_from(r)
                except Exception as e2:                          # ← 补日志
                    logger.warning(f"single fallback error idx={idx}: {e2}")
                    results[idx] = 0.0

    return results