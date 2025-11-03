"""Sentiment analysis wrapper around Hugging Face transformers."""

from __future__ import annotations

from functools import lru_cache
from typing import Iterable, List, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from transformers.pipelines import TextClassificationPipeline

from .schemas import ArticleSentiment, RawArticle
from .settings import Settings


@lru_cache
def get_sentiment_pipeline(model_name: str, device) -> "TextClassificationPipeline":
    """Cache the pipeline by model/device."""

    from transformers import pipeline  # local import to keep optional dependency lazy

    return pipeline("sentiment-analysis", model=model_name, device=device)


def annotate_sentiment(settings: Settings, articles: Iterable[RawArticle]) -> List[tuple[RawArticle, ArticleSentiment]]:
    pipe = get_sentiment_pipeline(
        model_name=settings.sentiment_model_name,
        device=settings.sentiment_device,
    )
    titles = [article.title for article in articles]
    if not titles:
        return []
    results = pipe(titles)
    annotated: list[tuple[RawArticle, ArticleSentiment]] = []
    for article, result in zip(articles, results):
        annotated.append(
            (
                article,
                ArticleSentiment(
                    label=result["label"],
                    score=float(result["score"]),
                ),
            )
        )
    return annotated
