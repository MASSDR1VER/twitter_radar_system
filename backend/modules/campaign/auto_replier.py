#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Auto Replier - Generates and posts automated replies to tweets.
Supports multiple AI providers: OpenAI, Anthropic, Grok AI, or combined approach.
"""

import logging
from typing import Dict, Any, Optional

from modules.integrations.twitter_adapter import TwitterAdapter
from modules.llm.llm_service import LLMService

logger = logging.getLogger(__name__)


class AutoReplier:
    """
    Handles automatic reply generation and posting.
    """

    def __init__(self, twitter_adapter: TwitterAdapter, link_shortener=None):
        """
        Initialize the auto replier.

        Args:
            twitter_adapter: TwitterAdapter instance
            link_shortener: LinkShortener instance (optional)
        """
        self.twitter = twitter_adapter
        self.link_shortener = link_shortener

    async def generate_reply(
        self,
        tweet_data: Dict[str, Any],
        campaign: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate a reply using the configured AI provider.

        Args:
            tweet_data: Tweet information
            campaign: Campaign configuration

        Returns:
            Generated reply text or None if failed
        """
        ai_provider = campaign.get("ai_provider", "openai")
        template = campaign["reply_template"]
        short_url = campaign["short_url"]

        logger.info(f"Generating reply using {ai_provider}...")

        try:
            if ai_provider == "grok":
                # Use Grok AI
                return await self._generate_with_grok(
                    tweet_data, template, short_url, campaign
                )

            elif ai_provider == "openai":
                # Use OpenAI GPT
                return await self._generate_with_llm(
                    tweet_data, template, short_url, campaign, provider="openai"
                )

            elif ai_provider == "anthropic":
                # Use Anthropic Claude
                return await self._generate_with_llm(
                    tweet_data, template, short_url, campaign, provider="anthropic"
                )

            elif ai_provider == "both":
                # Use Grok for approval, then LLM for generation
                return await self._generate_with_both(
                    tweet_data, template, short_url, campaign
                )

            else:
                logger.error(f"Unknown AI provider: {ai_provider}")
                return None

        except Exception as e:
            logger.error(f"Error generating reply: {e}")
            return None

    async def _generate_with_grok(
        self,
        tweet_data: Dict[str, Any],
        template: str,
        url: str,
        campaign: Dict[str, Any]
    ) -> Optional[str]:
        """Generate reply using Grok AI."""
        return await self.twitter.generate_reply_with_grok(
            tweet_text=tweet_data["text"],
            author=tweet_data["username"],
            template=template,
            url=url,
            model=campaign.get("reply_model", "grok-3")
        )

    async def _generate_with_llm(
        self,
        tweet_data: Dict[str, Any],
        template: str,
        url: str,
        campaign: Dict[str, Any],
        provider: str
    ) -> Optional[str]:
        """Generate reply using OpenAI or Anthropic."""
        llm = LLMService()

        prompt = f"""
Generate a personalized Twitter reply.

Original Tweet:
Author: @{tweet_data['username']}
Text: "{tweet_data['text']}"

Reply Template: "{template}"

Instructions:
1. Make it natural and conversational
2. Replace {{author}} with @{tweet_data['username']}
3. Replace {{url}} with {url}
4. Keep under 280 characters
5. Be friendly and relevant to the tweet
6. Don't be spammy

IMPORTANT: Return ONLY the reply text, no explanations or formatting.

Generated Reply:
"""

        reply_text = await llm.generate_text(
            prompt=prompt,
            model=campaign.get("reply_model", "gpt-4" if provider == "openai" else "claude-3-5-sonnet-20241022"),
            max_tokens=100,
            temperature=0.7
        )

        # Clean and validate
        reply_text = reply_text.strip().strip('"')

        if len(reply_text) > 280:
            reply_text = reply_text[:277] + "..."

        return reply_text

    async def _generate_with_both(
        self,
        tweet_data: Dict[str, Any],
        template: str,
        url: str,
        campaign: Dict[str, Any]
    ) -> Optional[str]:
        """
        Use Grok for approval, then LLM for generation.

        Returns:
            Generated reply or None if Grok rejects
        """
        # Step 1: Ask Grok if we should reply
        conversation = await self.twitter.client.create_grok_conversation()

        approval_prompt = f"""
Should we reply to this tweet with our product link?

Tweet: "{tweet_data['text']}"
Author: @{tweet_data['username']}
Engagement: {tweet_data.get('likes', 0)} likes, {tweet_data.get('retweets', 0)} retweets

Our product: {campaign.get('name', 'Product')}
Target URL: {campaign.get('target_url', '')}

Reply with ONLY: yes or no
"""

        response = await conversation.generate(approval_prompt, model='grok-3', debug=False)
        grok_decision = response.message.strip().lower()

        if "no" in grok_decision:
            logger.info("Grok AI decided to skip this tweet")
            return None

        # Step 2: Generate reply with LLM
        return await self._generate_with_llm(
            tweet_data, template, url, campaign, provider="openai"
        )

    async def post_reply(
        self,
        tweet_data: Dict[str, Any],
        campaign: Dict[str, Any],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Generate and post a reply.

        Args:
            tweet_data: Tweet information
            campaign: Campaign configuration
            dry_run: If True, don't actually post (test mode)

        Returns:
            Result dictionary
        """
        # Generate reply
        reply_text = await self.generate_reply(tweet_data, campaign)

        if reply_text is None:
            return {
                "success": False,
                "reason": "AI decided to skip or generation failed"
            }

        logger.info(f"Generated reply: {reply_text}")

        # Dry run mode - don't actually post
        if dry_run:
            logger.info("[DRY RUN] Would post reply but dry_run=True")
            return {
                "success": True,
                "dry_run": True,
                "reply_text": reply_text,
                "tweet_id": None
            }

        # Post the reply
        try:
            result = await self.twitter.create_tweet(
                text=reply_text,
                reply_to=tweet_data["tweet_id"]
            )

            if result["success"]:
                logger.info(f"✅ Reply posted: {result['url']}")
                return {
                    "success": True,
                    "dry_run": False,
                    "reply_text": reply_text,
                    "tweet_id": result["tweet_id"],
                    "url": result["url"]
                }
            else:
                logger.error(f"❌ Failed to post reply: {result.get('error')}")
                return {
                    "success": False,
                    "error": result.get("error"),
                    "reply_text": reply_text
                }

        except Exception as e:
            logger.error(f"Error posting reply: {e}")
            return {
                "success": False,
                "error": str(e),
                "reply_text": reply_text
            }
