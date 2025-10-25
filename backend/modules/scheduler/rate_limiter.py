#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Rate Limiter - Prevents spam and enforces posting limits.
"""

import logging
from datetime import datetime, timedelta
from typing import Tuple
from bson import ObjectId

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Enforces rate limits for campaign replies.
    """

    def __init__(self, db_client):
        """
        Initialize the rate limiter.

        Args:
            db_client: MongoDB client
        """
        self.db = db_client

        # Default limits
        self.limits = {
            "replies_per_hour": 30,
            "min_delay_between_replies_seconds": 120  # 2 minutes
        }

    async def can_post_reply(self, campaign_id: str) -> Tuple[bool, str]:
        """
        Check if a reply can be posted for this campaign.

        Checks:
        1. Daily limit (from campaign config)
        2. Hourly limit (global)
        3. Minimum delay between replies

        Args:
            campaign_id: Campaign ID

        Returns:
            (can_post, reason) tuple
        """
        try:
            # Get campaign
            campaign = await self.db.campaigns.find_one({"_id": ObjectId(campaign_id)})
            if not campaign:
                return False, "Campaign not found"

            # 1. Daily limit check
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

            replies_today = await self.db.campaign_replies.count_documents({
                "campaign_id": ObjectId(campaign_id),
                "posted_at": {"$gte": today_start},
                "status": "posted",
                "dry_run": False
            })

            max_per_day = campaign.get("max_replies_per_day", 50)

            if replies_today >= max_per_day:
                return False, f"Daily limit reached ({replies_today}/{max_per_day})"

            # 2. Hourly limit check
            hour_ago = datetime.now() - timedelta(hours=1)

            replies_last_hour = await self.db.campaign_replies.count_documents({
                "campaign_id": ObjectId(campaign_id),
                "posted_at": {"$gte": hour_ago},
                "status": "posted",
                "dry_run": False
            })

            max_per_hour = self.limits["replies_per_hour"]

            if replies_last_hour >= max_per_hour:
                return False, f"Hourly limit reached ({replies_last_hour}/{max_per_hour})"

            # 3. Minimum delay check
            last_reply = await self.db.campaign_replies.find_one(
                {
                    "campaign_id": ObjectId(campaign_id),
                    "status": "posted",
                    "dry_run": False,
                    "posted_at": {"$exists": True}
                },
                sort=[("posted_at", -1)]
            )

            if last_reply and last_reply.get("posted_at"):
                time_since_last = (datetime.now() - last_reply["posted_at"]).total_seconds()
                min_delay = self.limits["min_delay_between_replies_seconds"]

                if time_since_last < min_delay:
                    wait_time = int(min_delay - time_since_last)
                    return False, f"Too soon since last reply. Wait {wait_time}s"

            # All checks passed
            return True, "OK"

        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return False, f"Error: {str(e)}"

    async def get_wait_time(self, campaign_id: str) -> int:
        """
        Get how many seconds to wait before next reply.

        Args:
            campaign_id: Campaign ID

        Returns:
            Seconds to wait (0 if can post now)
        """
        can_post, reason = await self.can_post_reply(campaign_id)

        if can_post:
            return 0

        # Parse wait time from reason if available
        if "Wait" in reason and "s" in reason:
            import re
            match = re.search(r'Wait (\d+)s', reason)
            if match:
                return int(match.group(1))

        # Default to minimum delay
        return self.limits["min_delay_between_replies_seconds"]
