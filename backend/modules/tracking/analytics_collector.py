#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analytics Collector - Collects and aggregates campaign metrics.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from bson import ObjectId

logger = logging.getLogger(__name__)


class AnalyticsCollector:
    """
    Collects and processes campaign analytics.
    """

    def __init__(self, db_client):
        """
        Initialize the analytics collector.

        Args:
            db_client: MongoDB client
        """
        self.db = db_client

    async def get_campaign_analytics(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a campaign.

        Args:
            campaign_id: Campaign ID

        Returns:
            Analytics data dictionary
        """
        try:
            # Get campaign
            campaign = await self.db.campaigns.find_one({"_id": ObjectId(campaign_id)})
            if not campaign:
                return {"success": False, "error": "Campaign not found"}

            # 1. Total replies posted
            total_replies = await self.db.campaign_replies.count_documents({
                "campaign_id": ObjectId(campaign_id),
                "status": "posted",
                "dry_run": False
            })

            # 2. Total clicks
            total_clicks = await self.db.click_events.count_documents({
                "campaign_id": ObjectId(campaign_id)
            })

            # 3. CTR (Click-Through Rate)
            ctr = (total_clicks / total_replies * 100) if total_replies > 0 else 0

            # 4. Engagement metrics
            pipeline = [
                {
                    "$match": {
                        "campaign_id": ObjectId(campaign_id),
                        "status": "posted"
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_likes": {"$sum": "$likes"},
                        "total_retweets": {"$sum": "$retweets"},
                        "total_replies": {"$sum": "$replies"}
                    }
                }
            ]

            engagement_result = await self.db.campaign_replies.aggregate(pipeline).to_list(length=1)
            engagement = engagement_result[0] if engagement_result else {
                "total_likes": 0,
                "total_retweets": 0,
                "total_replies": 0
            }

            # 5. Top performing replies
            top_replies = await self.db.campaign_replies.find({
                "campaign_id": ObjectId(campaign_id),
                "status": "posted"
            }).sort("likes", -1).limit(5).to_list(length=5)

            # 6. Replies by date (last 30 days)
            replies_by_date = await self._get_replies_by_date(campaign_id, days=30)

            # 7. Clicks by date
            clicks_by_date = await self._get_clicks_by_date(campaign_id, days=30)

            # 8. Error rate
            failed_replies = await self.db.campaign_replies.count_documents({
                "campaign_id": ObjectId(campaign_id),
                "status": "failed"
            })

            total_attempts = total_replies + failed_replies
            error_rate = (failed_replies / total_attempts * 100) if total_attempts > 0 else 0

            # Build response
            return {
                "success": True,
                "campaign": {
                    "id": campaign_id,
                    "name": campaign["name"],
                    "status": campaign["status"],
                    "created_at": campaign["created_at"].isoformat() if isinstance(campaign["created_at"], datetime) else str(campaign["created_at"])
                },
                "metrics": {
                    "total_replies": total_replies,
                    "total_clicks": total_clicks,
                    "ctr": round(ctr, 2),
                    "total_likes": engagement.get("total_likes", 0),
                    "total_retweets": engagement.get("total_retweets", 0),
                    "total_reply_replies": engagement.get("total_replies", 0),
                    "failed_replies": failed_replies,
                    "error_rate": round(error_rate, 2)
                },
                "top_replies": [
                    {
                        "id": str(r["_id"]),
                        "text": r["reply_text"],
                        "target_user": r["target_user"],
                        "target_tweet_id": r.get("target_tweet_id"),
                        "target_tweet_url": f"https://twitter.com/{r['target_user']}/status/{r.get('target_tweet_id')}" if r.get("target_tweet_id") else None,
                        "reply_tweet_id": r.get("reply_tweet_id"),
                        "reply_tweet_url": f"https://twitter.com/i/web/status/{r.get('reply_tweet_id')}" if r.get("reply_tweet_id") else None,
                        "likes": r.get("likes", 0),
                        "retweets": r.get("retweets", 0),
                        "replies": r.get("replies", 0),
                        "posted_at": r["posted_at"].isoformat() if r.get("posted_at") and isinstance(r["posted_at"], datetime) else str(r.get("posted_at"))
                    }
                    for r in top_replies
                ],
                "charts": {
                    "replies_by_date": replies_by_date,
                    "clicks_by_date": clicks_by_date
                }
            }

        except Exception as e:
            logger.error(f"Error getting campaign analytics: {e}")
            return {"success": False, "error": str(e)}

    async def _get_replies_by_date(self, campaign_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get replies grouped by date."""
        pipeline = [
            {
                "$match": {
                    "campaign_id": ObjectId(campaign_id),
                    "status": "posted",
                    "posted_at": {"$exists": True}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$posted_at"
                        }
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]

        result = await self.db.campaign_replies.aggregate(pipeline).to_list(length=None)

        return [
            {"date": item["_id"], "count": item["count"]}
            for item in result
        ]

    async def _get_clicks_by_date(self, campaign_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get clicks grouped by date."""
        pipeline = [
            {
                "$match": {
                    "campaign_id": ObjectId(campaign_id),
                    "clicked_at": {"$exists": True}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$clicked_at"
                        }
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]

        result = await self.db.click_events.aggregate(pipeline).to_list(length=None)

        return [
            {"date": item["_id"], "count": item["count"]}
            for item in result
        ]

    async def record_click_event(
        self,
        campaign_id: str,
        short_code: str,
        ip_address: str,
        user_agent: str,
        referrer: str = None
    ) -> bool:
        """
        Record a click event.

        Args:
            campaign_id: Campaign ID
            short_code: Short URL code
            ip_address: Visitor IP
            user_agent: Browser user agent
            referrer: HTTP referrer

        Returns:
            True if successful
        """
        try:
            # Save click event
            await self.db.click_events.insert_one({
                "campaign_id": ObjectId(campaign_id) if campaign_id else None,
                "short_code": short_code,
                "clicked_at": datetime.now(),
                "ip_address": ip_address,
                "user_agent": user_agent,
                "referrer": referrer
            })

            # Update click counter in short_links
            await self.db.short_links.update_one(
                {"short_code": short_code},
                {"$inc": {"clicks": 1}}
            )

            # Update campaign total clicks
            if campaign_id:
                await self.db.campaigns.update_one(
                    {"_id": ObjectId(campaign_id)},
                    {"$inc": {"total_clicks": 1}}
                )

            return True

        except Exception as e:
            logger.error(f"Error recording click event: {e}")
            return False
