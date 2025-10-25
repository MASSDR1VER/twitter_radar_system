#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Link Shortener - Creates short URLs for tracking clicks.
Supports Bitly API or internal shortening.
"""

import logging
import string
import random
import os
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class LinkShortener:
    """
    Creates and manages short URLs for click tracking.
    """

    def __init__(self, db_client=None):
        """
        Initialize the link shortener.

        Args:
            db_client: MongoDB client (for internal shortener)
        """
        self.db = db_client
        self.bitly_token = os.getenv("BITLY_API_KEY")
        self.base_url = os.getenv("BASE_URL", "http://localhost:8000")

    async def shorten(
        self,
        long_url: str,
        campaign_id: Optional[str] = None
    ) -> str:
        """
        Shorten a URL using Bitly or internal shortener.

        Args:
            long_url: Original URL to shorten
            campaign_id: Optional campaign ID for tracking

        Returns:
            Shortened URL
        """
        # Try Bitly first if API key available
        if self.bitly_token:
            try:
                return await self._shorten_with_bitly(long_url)
            except Exception as e:
                logger.warning(f"Bitly failed, falling back to internal: {e}")

        # Use internal shortener
        return await self._shorten_internal(long_url, campaign_id)

    async def _shorten_with_bitly(self, long_url: str) -> str:
        """
        Shorten URL using Bitly API.

        Args:
            long_url: URL to shorten

        Returns:
            Bitly short URL
        """
        import httpx

        headers = {
            "Authorization": f"Bearer {self.bitly_token}",
            "Content-Type": "application/json"
        }

        data = {
            "long_url": long_url,
            "domain": "bit.ly"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api-ssl.bitly.com/v4/shorten",
                headers=headers,
                json=data
            )

            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                short_url = result["link"]
                logger.info(f"Bitly shortened: {long_url} -> {short_url}")
                return short_url
            else:
                raise Exception(f"Bitly API error: {response.status_code}")

    async def _shorten_internal(
        self,
        long_url: str,
        campaign_id: Optional[str] = None
    ) -> str:
        """
        Create short URL using internal shortener.

        Args:
            long_url: URL to shorten
            campaign_id: Optional campaign ID

        Returns:
            Internal short URL
        """
        # Generate short code
        short_code = self._generate_short_code()

        # Save to database
        if self.db is not None:
            await self.db.short_links.insert_one({
                "short_code": short_code,
                "long_url": long_url,
                "campaign_id": campaign_id,
                "clicks": 0,
                "provider": "internal",
                "created_at": datetime.now()
            })

        short_url = f"{self.base_url}/r/{short_code}"
        logger.info(f"Internal shortened: {long_url} -> {short_url}")

        return short_url

    def _generate_short_code(self, length: int = 6) -> str:
        """
        Generate a random short code.

        Args:
            length: Length of short code

        Returns:
            Random alphanumeric string
        """
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    async def get_click_stats(self, short_url: str) -> dict:
        """
        Get click statistics for a short URL.

        Args:
            short_url: Short URL

        Returns:
            Click statistics
        """
        if "bit.ly" in short_url and self.bitly_token:
            return await self._get_bitly_stats(short_url)
        else:
            return await self._get_internal_stats(short_url)

    async def _get_bitly_stats(self, short_url: str) -> dict:
        """Get stats from Bitly API."""
        import httpx

        headers = {"Authorization": f"Bearer {self.bitly_token}"}

        # Extract bitlink ID
        link_id = short_url.replace("https://", "").replace("http://", "")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api-ssl.bitly.com/v4/bitlinks/{link_id}/clicks",
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "total_clicks": data.get("link_clicks", 0),
                    "provider": "bitly"
                }

        return {"total_clicks": 0, "provider": "bitly"}

    async def _get_internal_stats(self, short_url: str) -> dict:
        """Get stats from internal database."""
        if self.db is None:
            return {"total_clicks": 0, "provider": "internal"}

        # Extract short code
        short_code = short_url.split("/")[-1]

        link = await self.db.short_links.find_one({"short_code": short_code})

        if link:
            return {
                "total_clicks": link.get("clicks", 0),
                "provider": "internal"
            }

        return {"total_clicks": 0, "provider": "internal"}
