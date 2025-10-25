#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analytics API - Endpoints for campaign analytics and metrics.
"""

import logging
from fastapi import APIRouter, HTTPException, Request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/campaign/{campaign_id}")
async def get_campaign_analytics(campaign_id: str, req: Request):
    """
    Get comprehensive analytics for a campaign.

    Returns:
    - Total replies, clicks, CTR
    - Engagement metrics (likes, retweets)
    - Top performing replies
    - Time-series data (replies/clicks by date)
    - Error rate
    """
    try:
        analytics_collector = req.app.state.analytics_collector

        result = await analytics_collector.get_campaign_analytics(campaign_id)

        if not result["success"]:
            raise HTTPException(status_code=404, detail=result.get("error", "Campaign not found"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_dashboard_analytics(req: Request):
    """
    Get overall dashboard analytics across all campaigns.
    """
    try:
        db = req.app.state.db

        # Get total stats across all campaigns
        total_campaigns = await db.campaigns.count_documents({})
        active_campaigns = await db.campaigns.count_documents({"status": "active"})

        total_replies = await db.campaign_replies.count_documents({"status": "posted", "dry_run": False})
        total_clicks = await db.click_events.count_documents({})

        # CTR
        ctr = (total_clicks / total_replies * 100) if total_replies > 0 else 0

        # Get recent campaigns
        recent_campaigns = await db.campaigns.find().sort("created_at", -1).limit(5).to_list(length=5)

        campaigns_list = []
        for campaign in recent_campaigns:
            campaigns_list.append({
                "id": str(campaign["_id"]),
                "name": campaign["name"],
                "status": campaign["status"],
                "total_replies": campaign.get("total_replies", 0),
                "total_clicks": campaign.get("total_clicks", 0)
            })

        return {
            "success": True,
            "stats": {
                "total_campaigns": total_campaigns,
                "active_campaigns": active_campaigns,
                "total_replies": total_replies,
                "total_clicks": total_clicks,
                "ctr": round(ctr, 2)
            },
            "recent_campaigns": campaigns_list
        }

    except Exception as e:
        logger.error(f"Error getting dashboard analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
