#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Twitter Platform Adapter for InteractRadar.
Provides integration with Twitter/X using a single admin account.
"""

import logging
import asyncio
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pathlib import Path

# Import the Twitter client from platforms directory
from platforms.twitter.client.client import Client
from platforms.twitter.errors import TooManyRequests

logger = logging.getLogger(__name__)

class TwitterAdapter:
    """
    Adapter for Twitter/X platform integration.
    Uses a single admin account for all operations.
    """

    def __init__(self):
        """Initialize the Twitter adapter with no authentication."""
        self.client = None  # Single Twitter client instance
        self.user = None    # Authenticated user info
        self.is_authenticated = False

    async def initialize_from_file(self, cookie_file_path: str) -> bool:
        """
        Initialize Twitter client from cookie.json file.

        Args:
            cookie_file_path: Path to cookies.json file

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Read cookies from file
            cookie_path = Path(cookie_file_path)
            if not cookie_path.exists():
                logger.error(f"Cookie file not found: {cookie_file_path}")
                return False

            with open(cookie_path, 'r') as f:
                cookies = json.load(f)

            # Create Twitter client
            self.client = Client(
                language='en-US',
                proxy=None  # Can be configured if needed
            )

            # Load cookies
            self.client.load_cookies(cookies)

            # Verify authentication by getting user info
            self.user = await self.client.user()
            self.is_authenticated = True

            logger.info(f"✅ Twitter authenticated as: @{self.user.screen_name}")
            logger.info(f"   User ID: {self.user.id}")
            logger.info(f"   Display Name: {self.user.name}")
            logger.info(f"   Followers: {self.user.followers_count}")

            return True

        except Exception as e:
            logger.error(f"❌ Twitter authentication failed: {e}")
            self.is_authenticated = False
            return False

    def _check_authenticated(self):
        """Check if client is authenticated, raise error if not."""
        if not self.is_authenticated or not self.client:
            raise Exception("Twitter client not authenticated. Please call initialize_from_file() first.")

    # ==================== USER OPERATIONS ====================

    async def get_user_by_screen_name(self, username: str) -> Dict[str, Any]:
        """
        Get user information by username.

        Args:
            username: Twitter username (with or without @)

        Returns:
            User data dictionary
        """
        self._check_authenticated()

        try:
            username = username.strip('@')
            user = await self.client.get_user_by_screen_name(username)

            return {
                "success": True,
                "user_id": user.id,
                "username": user.screen_name,
                "name": user.name,
                "bio": user.description,
                "followers_count": user.followers_count,
                "following_count": user.following_count,
                "profile_image_url": user.profile_image_url,
                "created_at": user.created_at
            }

        except Exception as e:
            logger.error(f"Error getting user @{username}: {e}")
            return {"success": False, "error": str(e)}

    async def get_user_tweets(
        self,
        username: str,
        count: int = 50,
        lookback_days: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user's recent tweets.

        Args:
            username: Twitter username
            count: Maximum number of tweets to retrieve
            lookback_days: Optional filter for tweet age (in days)

        Returns:
            List of tweet dictionaries
        """
        self._check_authenticated()

        try:
            username = username.strip('@')
            user = await self.client.get_user_by_screen_name(username)

            tweets = []
            result = await self.client.get_user_tweets(user.id, 'Tweets', count=count)

            for tweet in result:
                # Check age if lookback_days specified
                if lookback_days:
                    tweet_age = (datetime.now(timezone.utc) - tweet.created_at_datetime).days
                    if tweet_age > lookback_days:
                        break

                tweets.append({
                    "tweet_id": tweet.id,
                    "text": tweet.text,
                    "created_at": tweet.created_at,
                    "created_at_datetime": tweet.created_at_datetime,
                    "likes": tweet.favorite_count,
                    "retweets": tweet.retweet_count,
                    "replies": tweet.reply_count,
                    "url": f"https://x.com/{username}/status/{tweet.id}"
                })

            logger.info(f"Retrieved {len(tweets)} tweets from @{username}")
            return tweets

        except Exception as e:
            logger.error(f"Error getting tweets for @{username}: {e}")
            return []

    async def get_tweet_interactions(
        self,
        tweet_id: str
    ) -> Dict[str, List[str]]:
        """
        Get users who interacted with a tweet (likes, retweets).

        Args:
            tweet_id: Tweet ID

        Returns:
            Dictionary with lists of usernames who liked/retweeted
        """
        self._check_authenticated()

        interactions = {
            "likers": [],
            "retweeters": []
        }

        try:
            # Get likers (favoriters)
            favoriters = await self.client.get_favoriters(tweet_id, count=50)
            for user in favoriters:
                interactions["likers"].append(user.screen_name)
        except Exception as e:
            logger.warning(f"Could not get likers for tweet {tweet_id}: {e}")

        try:
            # Get retweeters
            retweeters = await self.client.get_retweeters(tweet_id, count=50)
            for user in retweeters:
                interactions["retweeters"].append(user.screen_name)
        except Exception as e:
            logger.warning(f"Could not get retweeters for tweet {tweet_id}: {e}")

        return interactions

    # ==================== TWEET OPERATIONS ====================

    async def create_tweet(
        self,
        text: str,
        reply_to: Optional[str] = None,
        media_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a tweet or reply.

        Args:
            text: Tweet text
            reply_to: Optional tweet ID to reply to
            media_ids: Optional list of media IDs

        Returns:
            Result dictionary with tweet info
        """
        self._check_authenticated()

        try:
            tweet = await self.client.create_tweet(
                text=text,
                reply_to=reply_to,
                media_ids=media_ids
            )

            return {
                "success": True,
                "tweet_id": tweet.id,
                "url": f"https://x.com/{self.user.screen_name}/status/{tweet.id}",
                "text": tweet.text
            }

        except TooManyRequests as e:
            logger.error(f"Twitter rate limit hit: {e}")
            return {
                "success": False,
                "error": "Twitter rate limit exceeded",
                "rate_limit": True
            }

        except Exception as e:
            logger.error(f"Error creating tweet: {e}")
            return {"success": False, "error": str(e)}

    async def search_tweets(
        self,
        query: str,
        count: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for tweets.

        Args:
            query: Search query
            count: Number of results

        Returns:
            List of tweet dictionaries
        """
        self._check_authenticated()

        try:
            tweets = []
            async for tweet in self.client.search_tweet(query, count=count):
                tweets.append({
                    "tweet_id": tweet.id,
                    "username": tweet.user.screen_name,
                    "text": tweet.text,
                    "created_at": tweet.created_at,
                    "likes": tweet.favorite_count,
                    "retweets": tweet.retweet_count,
                    "url": f"https://x.com/{tweet.user.screen_name}/status/{tweet.id}"
                })

            return tweets

        except Exception as e:
            logger.error(f"Error searching tweets: {e}")
            return []

    # ==================== GROK AI INTEGRATION ====================

    async def analyze_tweets_with_grok(
        self,
        tweets: List[Dict[str, Any]],
        analysis_prompt: str,
        model: str = 'grok-3'
    ) -> Dict[str, Any]:
        """
        Analyze tweets using Grok AI (Twitter's native AI).

        Args:
            tweets: List of tweet dictionaries
            analysis_prompt: Prompt for Grok AI
            model: Grok model to use (grok-3, grok-2)

        Returns:
            Analysis result dictionary
        """
        self._check_authenticated()

        try:
            # Create Grok conversation
            conversation = await self.client.create_grok_conversation()

            # Build full prompt
            full_prompt = f"{analysis_prompt}\n\nTWEETS TO ANALYZE:\n"

            for tweet in tweets[:20]:  # Max 20 tweets
                full_prompt += f"""
TWEET ID: {tweet.get('tweet_id')}
AUTHOR: @{tweet.get('username', 'unknown')}
TEXT: {tweet.get('text', '')}
ENGAGEMENT: {tweet.get('likes', 0)} likes, {tweet.get('retweets', 0)} retweets

"""

            # Get Grok response
            response = await conversation.generate(full_prompt, model=model, debug=False)
            analysis_text = response.message.strip()

            logger.info(f"Grok AI analysis completed ({len(tweets)} tweets)")

            return {
                "success": True,
                "analysis": analysis_text,
                "model": model,
                "tweets_analyzed": len(tweets)
            }

        except Exception as e:
            logger.error(f"Error analyzing tweets with Grok: {e}")
            return {"success": False, "error": str(e)}

    async def generate_reply_with_grok(
        self,
        tweet_text: str,
        author: str,
        template: str,
        url: str,
        model: str = 'grok-3'
    ) -> Optional[str]:
        """
        Generate a reply using Grok AI.

        Args:
            tweet_text: Original tweet text
            author: Tweet author username
            template: Reply template
            url: URL to include in reply
            model: Grok model to use

        Returns:
            Generated reply text or None if failed
        """
        self._check_authenticated()

        try:
            conversation = await self.client.create_grok_conversation()

            prompt = f"""
Generate a personalized Twitter reply.

Original Tweet:
Author: @{author}
Text: "{tweet_text}"

Reply Template: "{template}"

Instructions:
1. Make it natural and conversational
2. Replace {{author}} with @{author}
3. Replace {{url}} with {url}
4. Keep under 280 characters
5. Be friendly and relevant to the tweet
6. Don't be spammy

IMPORTANT: Return ONLY the reply text, no explanations or formatting.

Generated Reply:
"""

            response = await conversation.generate(prompt, model=model, debug=False)
            reply_text = response.message.strip().strip('"')

            # Character limit check
            if len(reply_text) > 280:
                reply_text = reply_text[:277] + "..."

            return reply_text

        except Exception as e:
            logger.error(f"Error generating reply with Grok: {e}")
            return None

    # ==================== RATE LIMIT HANDLING ====================

    async def safe_api_call(self, func, *args, **kwargs):
        """
        Execute API call with rate limit handling.

        Args:
            func: Async function to call
            *args, **kwargs: Arguments for the function

        Returns:
            Function result
        """
        try:
            return await func(*args, **kwargs)

        except TooManyRequests as e:
            logger.error(f"Twitter rate limit hit: {e}")

            # Get reset time from headers if available
            reset_time = getattr(e, 'headers', {}).get("x-rate-limit-reset")

            if reset_time:
                wait_seconds = int(reset_time) - int(datetime.now().timestamp())
                logger.info(f"Waiting {wait_seconds}s for rate limit reset...")
                await asyncio.sleep(wait_seconds)

                # Retry once
                return await func(*args, **kwargs)

            raise

    # ==================== UTILITY METHODS ====================

    def get_status(self) -> Dict[str, Any]:
        """
        Get current adapter status.

        Returns:
            Status dictionary
        """
        if not self.is_authenticated:
            return {
                "authenticated": False,
                "message": "Not authenticated. Call initialize_from_file() first."
            }

        return {
            "authenticated": True,
            "username": self.user.screen_name if self.user else None,
            "user_id": self.user.id if self.user else None,
            "display_name": self.user.name if self.user else None,
            "followers": self.user.followers_count if self.user else 0,
            "following": self.user.following_count if self.user else 0
        }
