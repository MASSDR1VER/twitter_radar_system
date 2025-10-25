import random, re, json, uuid
from collections import Counter
from typing import List

def avoid_phrases(recent_tweets: List[str], n: int = 4, k: int = 10) -> str:
    """
    Return the top-k n-grams from recent tweets, joined by semicolons.
    Used to nudge the model away from verbatim repetition.
    """
    counter = Counter(
        " ".join(tokens[i : i + n]).lower()
        for t in recent_tweets
        for tokens in [t.split()]
        for i in range(max(len(tokens) - n + 1, 0))
    )
    return "; ".join(g for g, _ in counter.most_common(k))

def random_sampling_params() -> dict:
    """
    Generate a high-entropy decoding profile for a chat-completion call.
    """
    return dict(
        temperature       = random.uniform(0.75, 0.9),
        top_p             = random.uniform(0.85, 0.95),
        frequency_penalty = 0.4,
        presence_penalty  = 0.6,
        max_tokens        = 320,
    )