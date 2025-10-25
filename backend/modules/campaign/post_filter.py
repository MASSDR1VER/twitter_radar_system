#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Post Filter - Filters tweets based on keywords and optional Grok AI approval.
"""

import logging
import asyncio
import re
from typing import List, Dict, Any

from modules.integrations.twitter_adapter import TwitterAdapter
from modules.campaign.campaign_logger import campaign_logger

logger = logging.getLogger(__name__)


class PostFilter:
    """
    Filters tweets based on keywords and AI analysis.
    """

    def __init__(self, twitter_adapter: TwitterAdapter):
        """
        Initialize the post filter.

        Args:
            twitter_adapter: TwitterAdapter instance
        """
        self.twitter = twitter_adapter

    async def find_matching_posts(
        self,
        usernames: List[str],
        keywords: List[str],
        lookback_days: int = 7,
        max_posts_per_user: int = 5,
        use_grok_filter: bool = False,
        campaign_context: Dict[str, Any] = None,
        campaign_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Find tweets that match keywords from a list of users.

        Args:
            usernames: List of Twitter usernames
            keywords: List of keywords to match
            lookback_days: How many days to look back
            max_posts_per_user: Maximum posts per user
            use_grok_filter: Whether to use Grok AI for additional filtering
            campaign_context: Campaign info for Grok AI context

        Returns:
            List of matching posts
        """
        logger.info(f"Filtering posts from {len(usernames)} users...")
        logger.info(f"  Keywords: {keywords}")
        logger.info(f"  Grok filter: {'enabled' if use_grok_filter else 'disabled'}")

        matching_posts = []

        for i, username in enumerate(usernames):
            try:
                # Get user's recent tweets
                tweets = await self.twitter.get_user_tweets(
                    username=username,
                    count=50,
                    lookback_days=lookback_days
                )

                logger.info(f"  Checking {username} ({i+1}/{len(usernames)})...")

                # Filter by keywords
                user_matches = []
                for tweet in tweets:
                    if self._matches_keywords(tweet["text"], keywords):
                        matched_kw = self._get_matched_keywords(tweet["text"], keywords)

                        user_matches.append({
                            "tweet_id": tweet["tweet_id"],
                            "username": username,
                            "text": tweet["text"],
                            "created_at": tweet["created_at"],
                            "likes": tweet["likes"],
                            "retweets": tweet["retweets"],
                            "url": tweet["url"],
                            "matched_keywords": matched_kw
                        })

                        # Limit posts per user
                        if len(user_matches) >= max_posts_per_user:
                            break

                if user_matches:
                    logger.info(f"    Found {len(user_matches)} matching posts")
                    if campaign_id:
                        await campaign_logger.info(campaign_id, f"  ✓ {username}: Found {len(user_matches)} matching tweets")

                matching_posts.extend(user_matches)

                # Add delay every 10 users to avoid rate limits
                if (i + 1) % 10 == 0 and i + 1 < len(usernames):
                    logger.info(f"  Processed {i + 1}/{len(usernames)} users, pausing...")
                    if campaign_id:
                        await campaign_logger.info(campaign_id, f"  Progress: {i + 1}/{len(usernames)} users checked, {len(matching_posts)} matching posts so far...")
                    await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Error filtering posts for @{username}: {e}")
                continue

        logger.info(f"  Found {len(matching_posts)} keyword-matched posts")

        # Optional: Grok AI filtering
        if use_grok_filter and matching_posts and campaign_context:
            logger.info("  Applying Grok AI filter...")
            matching_posts = await self._filter_with_grok(matching_posts, campaign_context)
            logger.info(f"  After Grok filter: {len(matching_posts)} posts")

        logger.info(f"✅ Final result: {len(matching_posts)} matching posts")

        return matching_posts

    def _matches_keywords(self, text: str, keywords: List[str]) -> bool:
        """
        Check if text contains any of the keywords (case-insensitive).

        Args:
            text: Tweet text
            keywords: List of keywords

        Returns:
            True if any keyword matches
        """
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in keywords)

    def _get_matched_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """
        Get list of keywords that matched in the text.

        Args:
            text: Tweet text
            keywords: List of keywords

        Returns:
            List of matched keywords
        """
        text_lower = text.lower()
        return [kw for kw in keywords if kw.lower() in text_lower]

    async def _filter_with_grok(
        self,
        posts: List[Dict[str, Any]],
        campaign_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Use Grok AI to filter posts for suitability.

        Args:
            posts: List of posts to filter
            campaign_context: Campaign information

        Returns:
            Filtered list of suitable posts
        """
        if not posts:
            return []

        # Build analysis prompt
        analysis_prompt = f"""
IMPORTANT INSTRUCTIONS:
1. DO NOT return JSON format
2. DO NOT use Markdown formatting
3. DO NOT add explanations

You are helping a marketing campaign called "{campaign_context.get('name', 'Campaign')}".
We want to reply to relevant tweets with this message template:
"{campaign_context.get('reply_template', '')}"

Target URL: {campaign_context.get('target_url', '')}
Keywords: {', '.join(campaign_context.get('keywords', []))}

Analyze these tweets and determine which ones are SUITABLE for our reply.
A tweet is suitable if:
1. It's genuinely discussing {', '.join(campaign_context.get('keywords', []))}
2. The author would likely appreciate our reply (not spam)
3. The tweet has decent engagement (not a dead tweet)
4. It's not negative/toxic content

FORMAT YOUR RESPONSE:
For each SUITABLE tweet, output:
tweet_id=ID;suitable=yes;reason=brief reason

For unsuitable tweets, output:
tweet_id=ID;suitable=no

DO NOT add any other text or explanations.
"""

        try:
            # Get Grok analysis
            result = await self.twitter.analyze_tweets_with_grok(
                tweets=posts,
                analysis_prompt=analysis_prompt,
                model='grok-3'
            )

            if not result["success"]:
                logger.warning("Grok analysis failed, returning original posts")
                return posts

            # Parse Grok response
            analysis_text = result["analysis"]
            suitable_posts = self._parse_grok_analysis(analysis_text, posts)

            return suitable_posts

        except Exception as e:
            logger.error(f"Error in Grok filtering: {e}")
            return posts  # Return original posts if Grok fails

    def _parse_grok_analysis(
        self,
        analysis_text: str,
        original_posts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Parse Grok AI analysis response.

        Args:
            analysis_text: Grok's response text
            original_posts: Original list of posts

        Returns:
            Filtered posts that Grok approved
        """
        suitable_posts = []

        # Pattern: tweet_id=ID;suitable=yes;reason=REASON
        pattern = r'tweet_id=([^;]+);suitable=([^;]+)(?:;reason=([^\n]+))?'
        matches = re.findall(pattern, analysis_text)

        for match in matches:
            tweet_id = match[0].strip()
            is_suitable = match[1].strip().lower() == 'yes'
            reason = match[2].strip() if len(match) > 2 else ""

            if is_suitable:
                # Find original post
                original_post = next(
                    (p for p in original_posts if str(p['tweet_id']) == tweet_id),
                    None
                )

                if original_post:
                    original_post['grok_approved'] = True
                    original_post['grok_reason'] = reason
                    suitable_posts.append(original_post)

        return suitable_posts
