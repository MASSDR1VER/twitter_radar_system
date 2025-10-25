#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interaction Mapper - Finds top interacted users from seed users.
Analyzes Twitter interactions (likes, retweets, replies) to identify the most engaged users.
"""

import logging
import asyncio
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Any

from modules.integrations.twitter_adapter import TwitterAdapter
from modules.campaign.campaign_logger import campaign_logger

logger = logging.getLogger(__name__)


class InteractionMapper:
    """
    Maps user interactions to find the most engaged users.
    """

    def __init__(self, twitter_adapter: TwitterAdapter):
        """
        Initialize the interaction mapper.

        Args:
            twitter_adapter: TwitterAdapter instance
        """
        self.twitter = twitter_adapter

    async def find_top_interacted_users(
        self,
        seed_users: List[str],
        top_n: int = 50,
        lookback_days: int = 7,
        campaign_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Find the top N users who interact most with seed users.

        Interaction scoring:
        - Like: 1 point
        - Retweet: 2 points
        - Reply: 3 points

        Args:
            seed_users: List of seed usernames (e.g., ["@elonmusk", "@sama"])
            top_n: Number of top users to return
            lookback_days: How many days to look back

        Returns:
            List of top interacted users with scores
        """
        logger.info(f"Finding top {top_n} interacted users from {len(seed_users)} seed users...")

        interaction_scores = defaultdict(int)  # username -> total_score

        for i, seed_username in enumerate(seed_users):
            logger.info(f"  Analyzing interactions for {seed_username}...")
            if campaign_id:
                await campaign_logger.info(campaign_id, f"Analyzing seed user {seed_username} ({i+1}/{len(seed_users)})...")

            try:
                # Get seed user's recent tweets (limit to 20 to avoid rate limits)
                tweets = await self.twitter.get_user_tweets(
                    username=seed_username,
                    count=20,  # Reduced from 100 to avoid rate limits
                    lookback_days=lookback_days
                )

                logger.info(f"    Found {len(tweets)} recent tweets")
                if campaign_id:
                    await campaign_logger.info(campaign_id, f"  Found {len(tweets)} tweets from {seed_username}, analyzing interactions...")

                # Analyze each tweet's interactions (with rate limiting)
                for tweet_idx, tweet in enumerate(tweets):
                    tweet_id = tweet["tweet_id"]

                    # Get users who interacted with this tweet
                    interactions = await self.twitter.get_tweet_interactions(tweet_id)

                    # Score likers (1 point each)
                    for liker in interactions["likers"]:
                        interaction_scores[liker] += 1

                    # Score retweeters (2 points each)
                    for retweeter in interactions["retweeters"]:
                        interaction_scores[retweeter] += 2

                    # Add delay every 5 tweets to avoid rate limits
                    if (tweet_idx + 1) % 5 == 0:
                        logger.info(f"    Processed {tweet_idx + 1}/{len(tweets)} tweets, pausing...")
                        if campaign_id:
                            await campaign_logger.info(campaign_id, f"  Processed {tweet_idx + 1}/{len(tweets)} tweets from {seed_username}...")
                        await asyncio.sleep(2)  # 2 second delay

                    # Note: Replies are harder to get from Twitter API
                    # If tweet has reply_count, we could fetch them too
                    # For now, we'll skip detailed reply analysis

            except Exception as e:
                logger.error(f"  Error analyzing {seed_username}: {e}")
                continue

            # Add delay between seed users to avoid rate limits
            if seed_username != seed_users[-1]:  # Don't delay after last user
                logger.info(f"  Pausing before next seed user...")
                await asyncio.sleep(3)

        # Remove seed users from results (don't want to reply to them)
        for seed in seed_users:
            username = seed.strip('@')
            interaction_scores.pop(username, None)

        # Sort by score and get top N
        sorted_users = sorted(
            interaction_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]

        # Format results
        results = [
            {
                "username": username,
                "interaction_score": score,
                "last_interaction": datetime.now()  # Simplified - could track actual time
            }
            for username, score in sorted_users
        ]

        logger.info(f"✅ Found {len(results)} top interacted users")
        logger.info(f"   Top 5: {[r['username'] for r in results[:5]]}")

        return results
