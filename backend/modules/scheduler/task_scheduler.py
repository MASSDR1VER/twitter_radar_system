#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Task Scheduler - Manages scheduled campaign tasks.
Processes active campaigns and posts replies at regular intervals.
"""

import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from modules.campaign.campaign_manager import CampaignManager
from modules.scheduler.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class TaskScheduler:
    """
    Schedules and executes campaign tasks.
    """

    def __init__(self, db_client, campaign_manager: CampaignManager):
        """
        Initialize the task scheduler.

        Args:
            db_client: MongoDB client
            campaign_manager: CampaignManager instance
        """
        self.db = db_client
        self.campaign_manager = campaign_manager
        self.rate_limiter = RateLimiter(db_client)

        self.scheduler = AsyncIOScheduler()
        self.is_running = False

    def start(self):
        """
        Start the scheduler.
        """
        if self.is_running:
            logger.warning("Scheduler already running")
            return

        # Add campaign processing job (every 5 minutes)
        self.scheduler.add_job(
            self.process_all_campaigns,
            trigger=IntervalTrigger(minutes=5),
            id='process_campaigns',
            name='Process Active Campaigns',
            replace_existing=True
        )

        # Start scheduler
        self.scheduler.start()
        self.is_running = True

        logger.info("✅ Task scheduler started (processing every 5 minutes)")

    def stop(self):
        """
        Stop the scheduler.
        """
        if not self.is_running:
            return

        self.scheduler.shutdown()
        self.is_running = False

        logger.info("Task scheduler stopped")

    async def process_all_campaigns(self):
        """
        Process all active campaigns.
        This is called by the scheduler every 5 minutes.
        """
        logger.info("🔄 Processing active campaigns...")

        try:
            # Get all active campaigns
            active_campaigns = await self.db.campaigns.find({
                "status": "active"
            }).to_list(length=None)

            if not active_campaigns:
                logger.info("  No active campaigns found")
                return

            logger.info(f"  Found {len(active_campaigns)} active campaign(s)")

            # Process each campaign
            for campaign in active_campaigns:
                campaign_id = str(campaign["_id"])
                await self.process_campaign(campaign_id)

            logger.info("✅ Campaign processing completed")

        except Exception as e:
            logger.error(f"Error processing campaigns: {e}")

    async def process_campaign(self, campaign_id: str):
        """
        Process a single campaign (post one reply if possible).

        Args:
            campaign_id: Campaign ID
        """
        try:
            campaign = await self.db.campaigns.find_one({"_id": campaign_id if isinstance(campaign_id, object) else campaign_id})
            if not campaign:
                return

            campaign_name = campaign.get("name", campaign_id)

            logger.info(f"  Processing: {campaign_name}")

            # Check rate limits
            can_post, reason = await self.rate_limiter.can_post_reply(campaign_id)

            if not can_post:
                logger.info(f"    ⏸️  Rate limited: {reason}")
                return

            # Process one pending reply
            result = await self.campaign_manager.process_pending_reply(campaign_id)

            if result.get("success"):
                if result.get("dry_run"):
                    logger.info(f"    🧪 [DRY RUN] Reply generated (not posted)")
                else:
                    logger.info(f"    ✅ Reply posted successfully")
            else:
                reason = result.get("reason", result.get("error", "Unknown"))
                logger.info(f"    ⏭️  {reason}")

        except Exception as e:
            logger.error(f"  Error processing campaign {campaign_id}: {e}")

    async def trigger_campaign_analysis(self, campaign_id: str):
        """
        Manually trigger campaign analysis (for testing or initial setup).

        Args:
            campaign_id: Campaign ID
        """
        logger.info(f"Triggering analysis for campaign {campaign_id}...")

        try:
            result = await self.campaign_manager.analyze_campaign(campaign_id)

            if result.get("success"):
                logger.info(f"✅ Analysis completed")
                logger.info(f"  Top users found: {result.get('top_users_found', 0)}")
                logger.info(f"  Matching posts: {result.get('matching_posts_found', 0)}")
            else:
                logger.error(f"❌ Analysis failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error triggering analysis: {e}")
            return {"success": False, "error": str(e)}
