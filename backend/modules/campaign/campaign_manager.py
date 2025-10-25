#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Campaign Manager - Main orchestrator for campaign operations.
Handles campaign creation, execution, and coordination of all components.
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from bson import ObjectId

from modules.integrations.twitter_adapter import TwitterAdapter
from modules.campaign.interaction_mapper import InteractionMapper
from modules.campaign.post_filter import PostFilter
from modules.campaign.auto_replier import AutoReplier
from modules.campaign.campaign_logger import campaign_logger

logger = logging.getLogger(__name__)


class CampaignManager:
    """
    Manages campaign lifecycle and orchestrates all campaign operations.
    """

    def __init__(self, db_client, twitter_adapter: TwitterAdapter):
        """
        Initialize the campaign manager.

        Args:
            db_client: MongoDB client
            twitter_adapter: TwitterAdapter instance
        """
        self.db = db_client
        self.twitter = twitter_adapter

        # Initialize campaign components
        self.interaction_mapper = InteractionMapper(twitter_adapter)
        self.post_filter = PostFilter(twitter_adapter)
        self.auto_replier = AutoReplier(twitter_adapter)

    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new campaign.

        Args:
            campaign_data: Campaign configuration

        Returns:
            Created campaign with ID
        """
        try:
            # Prepare campaign document
            campaign = {
                "name": campaign_data["name"],
                "status": "draft",

                # Configuration
                "seed_users": campaign_data["seed_users"],
                "top_n_users": campaign_data.get("top_n_users", 50),
                "lookback_days": campaign_data.get("lookback_days", 7),
                "keywords": campaign_data["keywords"],
                "reply_template": campaign_data["reply_template"],
                "target_url": campaign_data["target_url"],
                "short_url": campaign_data["short_url"],

                # AI Configuration
                "ai_provider": campaign_data.get("ai_provider", "openai"),
                "reply_model": campaign_data.get("reply_model", "gpt-4"),
                "use_grok_filter": campaign_data.get("use_grok_filter", False),

                # Limits
                "daily_reply_limit": campaign_data.get("daily_reply_limit", 50),
                "dry_run": campaign_data.get("dry_run", False),

                # Stats
                "total_replies": 0,
                "total_clicks": 0,

                # Timestamps
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

            # Insert into database
            result = await self.db.campaigns.insert_one(campaign)
            campaign["_id"] = result.inserted_id

            logger.info(f"✅ Campaign created: {campaign['name']} (ID: {result.inserted_id})")

            return {
                "success": True,
                "campaign_id": str(result.inserted_id),
                "campaign": campaign
            }

        except Exception as e:
            logger.error(f"Error creating campaign: {e}")
            return {"success": False, "error": str(e)}

    async def start_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Start a campaign (activate it for processing).

        Args:
            campaign_id: Campaign ID

        Returns:
            Success status
        """
        try:
            # Check if Twitter client is authenticated
            if not self.twitter.is_authenticated:
                return {
                    "success": False,
                    "error": "Twitter account not configured. Please add your Twitter cookies in Settings."
                }

            # Update status to active
            await self.db.campaigns.update_one(
                {"_id": ObjectId(campaign_id)},
                {
                    "$set": {
                        "status": "active",
                        "updated_at": datetime.now()
                    }
                }
            )

            logger.info(f"✅ Campaign {campaign_id} started")

            # Trigger initial analysis in background
            # This prevents the API from blocking while analysis runs
            asyncio.create_task(self.analyze_campaign(campaign_id))

            return {"success": True, "campaign_id": campaign_id}

        except Exception as e:
            logger.error(f"Error starting campaign: {e}")
            return {"success": False, "error": str(e)}

    async def stop_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Stop/pause a campaign.

        Args:
            campaign_id: Campaign ID

        Returns:
            Success status
        """
        try:
            await self.db.campaigns.update_one(
                {"_id": ObjectId(campaign_id)},
                {
                    "$set": {
                        "status": "paused",
                        "updated_at": datetime.now()
                    }
                }
            )

            logger.info(f"Campaign {campaign_id} stopped")

            return {"success": True, "campaign_id": campaign_id}

        except Exception as e:
            logger.error(f"Error stopping campaign: {e}")
            return {"success": False, "error": str(e)}

    async def analyze_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Analyze campaign: map interactions and filter posts.

        This is the initial setup phase that:
        1. Finds top interacted users
        2. Filters their posts by keywords
        3. Stores matched posts for replying

        Args:
            campaign_id: Campaign ID

        Returns:
            Analysis results
        """
        try:
            # Get campaign
            campaign = await self.db.campaigns.find_one({"_id": ObjectId(campaign_id)})
            if not campaign:
                return {"success": False, "error": "Campaign not found"}

            logger.info(f"🔍 Analyzing campaign: {campaign['name']}")
            await campaign_logger.info(campaign_id, f"🔍 Starting analysis for campaign: {campaign['name']}")

            # Step 1: Interaction Mapping
            logger.info("  Step 1: Finding top interacted users...")
            await campaign_logger.info(campaign_id, "Step 1: Finding top interacted users from seed accounts...")

            top_users = await self.interaction_mapper.find_top_interacted_users(
                seed_users=campaign["seed_users"],
                top_n=campaign["top_n_users"],
                lookback_days=campaign["lookback_days"],
                campaign_id=campaign_id  # Pass campaign_id for logging
            )

            # Save interaction map
            for seed_user in campaign["seed_users"]:
                await self.db.interaction_map.insert_one({
                    "campaign_id": ObjectId(campaign_id),
                    "seed_user": seed_user,
                    "top_interacted_users": top_users,
                    "created_at": datetime.now()
                })

            logger.info(f"    Found {len(top_users)} top users")
            await campaign_logger.success(campaign_id, f"✅ Found {len(top_users)} top interacted users", top_users_count=len(top_users))

            # Step 2: Post Filtering
            logger.info("  Step 2: Filtering matching posts...")
            await campaign_logger.info(campaign_id, f"Step 2: Filtering posts by keywords: {', '.join(campaign['keywords'])}")

            usernames = [user["username"] for user in top_users]

            campaign_context = {
                "name": campaign["name"],
                "keywords": campaign["keywords"],
                "reply_template": campaign["reply_template"],
                "target_url": campaign["target_url"]
            }

            matching_posts = await self.post_filter.find_matching_posts(
                usernames=usernames,
                keywords=campaign["keywords"],
                lookback_days=campaign["lookback_days"],
                max_posts_per_user=5,
                use_grok_filter=campaign.get("use_grok_filter", False),
                campaign_context=campaign_context,
                campaign_id=campaign_id  # Pass campaign_id for logging
            )

            # Save matched posts
            for post in matching_posts:
                post["campaign_id"] = ObjectId(campaign_id)
                post["reply_status"] = "pending"
                post["found_at"] = datetime.now()
                await self.db.matched_posts.insert_one(post)

            logger.info(f"    Found {len(matching_posts)} matching posts")
            await campaign_logger.success(campaign_id, f"✅ Found {len(matching_posts)} matching posts ready for replies", matching_posts_count=len(matching_posts))

            # Update campaign status
            await self.db.campaigns.update_one(
                {"_id": ObjectId(campaign_id)},
                {
                    "$set": {
                        "analysis_completed": True,
                        "total_matched_posts": len(matching_posts),
                        "updated_at": datetime.now()
                    }
                }
            )

            logger.info(f"✅ Campaign analysis completed")
            await campaign_logger.success(campaign_id, "🎉 Campaign analysis completed successfully! Ready to start replying.")

            return {
                "success": True,
                "top_users_found": len(top_users),
                "matching_posts_found": len(matching_posts)
            }

        except Exception as e:
            logger.error(f"Error analyzing campaign: {e}")
            return {"success": False, "error": str(e)}

    async def process_pending_reply(self, campaign_id: str) -> Dict[str, Any]:
        """
        Process one pending reply for a campaign.

        This is called by the scheduler to gradually post replies.

        Args:
            campaign_id: Campaign ID

        Returns:
            Processing result
        """
        try:
            # Get campaign
            campaign = await self.db.campaigns.find_one({"_id": ObjectId(campaign_id)})
            if not campaign:
                return {"success": False, "error": "Campaign not found"}

            if campaign["status"] != "active":
                return {"success": False, "error": "Campaign not active"}

            # Get one pending post
            pending_post = await self.db.matched_posts.find_one({
                "campaign_id": ObjectId(campaign_id),
                "reply_status": "pending"
            })

            if not pending_post:
                logger.info(f"No pending posts for campaign {campaign_id}")
                return {"success": False, "reason": "No pending posts"}

            # Check for duplicate (already replied to this tweet?)
            existing_reply = await self.db.campaign_replies.find_one({
                "campaign_id": ObjectId(campaign_id),
                "target_tweet_id": pending_post["tweet_id"],
                "status": "posted"
            })

            if existing_reply:
                # Mark as duplicate
                await self.db.matched_posts.update_one(
                    {"_id": pending_post["_id"]},
                    {"$set": {"reply_status": "duplicate"}}
                )
                return {"success": False, "reason": "Duplicate tweet"}

            # Post reply
            logger.info(f"Processing reply to @{pending_post['username']}...")

            result = await self.auto_replier.post_reply(
                tweet_data=pending_post,
                campaign=campaign,
                dry_run=campaign.get("dry_run", False)
            )

            # Save reply log
            reply_doc = {
                "campaign_id": ObjectId(campaign_id),
                "target_user": pending_post["username"],
                "target_tweet_id": pending_post["tweet_id"],
                "target_tweet_text": pending_post["text"],
                "reply_text": result.get("reply_text"),
                "reply_tweet_id": result.get("tweet_id"),
                "short_url": campaign["short_url"],
                "status": "posted" if result["success"] else "failed",
                "error_message": result.get("error"),
                "dry_run": result.get("dry_run", False),
                "likes": 0,
                "retweets": 0,
                "replies": 0,
                "posted_at": datetime.now() if result["success"] else None,
                "created_at": datetime.now()
            }

            await self.db.campaign_replies.insert_one(reply_doc)

            # Update matched post status
            await self.db.matched_posts.update_one(
                {"_id": pending_post["_id"]},
                {"$set": {"reply_status": "posted" if result["success"] else "failed"}}
            )

            # Update campaign stats
            if result["success"] and not result.get("dry_run"):
                await self.db.campaigns.update_one(
                    {"_id": ObjectId(campaign_id)},
                    {"$inc": {"total_replies": 1}}
                )

            return result

        except Exception as e:
            logger.error(f"Error processing reply: {e}")
            return {"success": False, "error": str(e)}

    async def get_campaign_status(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get campaign status and statistics.

        Args:
            campaign_id: Campaign ID

        Returns:
            Campaign status info
        """
        try:
            campaign = await self.db.campaigns.find_one({"_id": ObjectId(campaign_id)})
            if not campaign:
                return {"success": False, "error": "Campaign not found"}

            # Count pending posts
            pending_count = await self.db.matched_posts.count_documents({
                "campaign_id": ObjectId(campaign_id),
                "reply_status": "pending"
            })

            # Count posted replies
            posted_count = await self.db.campaign_replies.count_documents({
                "campaign_id": ObjectId(campaign_id),
                "status": "posted"
            })

            return {
                "success": True,
                "campaign_id": str(campaign["_id"]),
                "name": campaign["name"],
                "status": campaign["status"],
                "total_matched_posts": campaign.get("total_matched_posts", 0),
                "pending_posts": pending_count,
                "posted_replies": posted_count,
                "total_clicks": campaign.get("total_clicks", 0),
                "dry_run": campaign.get("dry_run", False)
            }

        except Exception as e:
            logger.error(f"Error getting campaign status: {e}")
            return {"success": False, "error": str(e)}
