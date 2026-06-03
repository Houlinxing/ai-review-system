from app.crawlers.youtube_crawler import (
    get_youtube_comments
)

from app.utils.text_cleaner import (
    clean_text
)


def get_clean_youtube_comments(
    video_id: str,
    max_results: int = 20
):

    comments = get_youtube_comments(
        video_id,
        max_results=max_results
    )

    clean_comments = []

    for comment in comments:

        comment = clean_text(comment)

        if len(comment.strip()) < 5:
            continue

        clean_comments.append(comment)

    return clean_comments