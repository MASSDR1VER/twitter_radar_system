#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Campaigns API - REST endpoints for campaign management.
"""

import logging
import asyncio
import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


# ==================== REQUEST MODELS ====================

class CreateCampaignRequest(BaseModel):
    """Request model for creating a campaign."""
    name: str = Field(..., description="Campaign name")
    seed_users: List[str] = Field(..., description="List of seed usernames (e.g., ['@elonmusk', '@sama'])")
    top_n_users: int = Field(50, description="Number of top interacted users to find", ge=1, le=200)
    lookback_days: int = Field(7, description="Days to look back for tweets", ge=1, le=30)
    keywords: List[str] = Field(..., description="Keywords to match in tweets")
    reply_template: str = Field(..., description="Reply message template (use {author} and {url} placeholders)")
    target_url: str = Field(..., description="URL to include in replies")
    ai_provider: str = Field("openai", description="AI provider: openai, anthropic, grok, or both")
    reply_model: Optional[str] = Field(None, description="Specific model to use (e.g., gpt-4, claude-3-5-sonnet-20241022)")
    use_grok_filter: bool = Field(False, description="Use Grok AI for post filtering")
    daily_reply_limit: int = Field(50, description="Maximum replies per day", ge=1, le=300)
    dry_run: bool = Field(False, description="Test mode - don't actually post tweets")


class UpdateCampaignStatusRequest(BaseModel):
    """Request model for updating campaign status."""
    status: str = Field(..., description="New status: active, paused, completed")


# ==================== ENDPOINTS ====================

@router.post("/create")
async def create_campaign(request: CreateCampaignRequest, req: Request):
    """
    Create a new campaign.

    This will:
    1. Create the campaign in database
    2. Shorten the target URL
    3. Return campaign ID

    The campaign starts in 'draft' status.
    """
    try:
        # Get dependencies from app state
        link_shortener = req.app.state.link_shortener
        campaign_manager = req.app.state.campaign_manager

        # Shorten URL
        short_url = await link_shortener.shorten(request.target_url)

        # Prepare campaign data
        campaign_data = {
            **request.dict(),
            "short_url": short_url
        }

        # Create campaign
        result = await campaign_manager.create_campaign(campaign_data)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create campaign"))

        return {
            "success": True,
            "campaign_id": result["campaign_id"],
            "short_url": short_url,
            "message": "Campaign created successfully. Use /campaigns/{id}/start to activate it."
        }

    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_campaigns(
    req: Request,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    List all campaigns.

    Query parameters:
    - status: Filter by status (active, paused, draft, completed)
    - limit: Number of campaigns to return
    - offset: Number of campaigns to skip
    """
    try:
        db = req.app.state.db

        # Build query
        query = {}
        if status:
            query["status"] = status

        # Get campaigns
        campaigns = await db.campaigns.find(query).sort("created_at", -1).skip(offset).limit(limit).to_list(length=limit)

        # Format response
        campaigns_list = []
        for campaign in campaigns:
            campaigns_list.append({
                "id": str(campaign["_id"]),
                "name": campaign["name"],
                "status": campaign["status"],
                "seed_users": campaign.get("seed_users", []),
                "keywords": campaign.get("keywords", []),
                "total_replies": campaign.get("total_replies", 0),
                "total_clicks": campaign.get("total_clicks", 0),
                "dry_run": campaign.get("dry_run", False),
                "ai_provider": campaign.get("ai_provider", "openai"),
                "created_at": campaign["created_at"].isoformat() if hasattr(campaign["created_at"], 'isoformat') else str(campaign["created_at"])
            })

        return {
            "success": True,
            "campaigns": campaigns_list,
            "total": len(campaigns_list)
        }

    except Exception as e:
        logger.error(f"Error listing campaigns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{campaign_id}")
async def get_campaign(campaign_id: str, req: Request):
    """
    Get campaign details.
    """
    try:
        campaign_manager = req.app.state.campaign_manager

        result = await campaign_manager.get_campaign_status(campaign_id)

        if not result["success"]:
            raise HTTPException(status_code=404, detail=result.get("error", "Campaign not found"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{campaign_id}/start")
async def start_campaign(campaign_id: str, req: Request, background_tasks: BackgroundTasks):
    """
    Start (activate) a campaign.

    This will:
    1. Set campaign status to 'active'
    2. Trigger initial analysis in background (find top users and matching posts)
    3. Begin automatic reply processing
    """
    try:
        campaign_manager = req.app.state.campaign_manager

        # Just start the campaign (sets status to active)
        # but don't run the analysis yet - we'll do that in background
        result = await campaign_manager.start_campaign(campaign_id)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to start campaign"))

        # Note: start_campaign already triggers analysis, but it's blocking
        # We return immediately to show the user it started
        return {
            "success": True,
            "campaign_id": campaign_id,
            "message": "Campaign started successfully. Analysis in progress..."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{campaign_id}/stop")
async def stop_campaign(campaign_id: str, req: Request):
    """
    Stop/pause a campaign.
    """
    try:
        campaign_manager = req.app.state.campaign_manager

        result = await campaign_manager.stop_campaign(campaign_id)

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to stop campaign"))

        return {
            "success": True,
            "campaign_id": campaign_id,
            "message": "Campaign stopped successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{campaign_id}/logs")
async def campaign_logs_stream(campaign_id: str, req: Request):
    """
    SSE endpoint for real-time campaign logs.

    Connect to this endpoint to receive live updates about campaign progress.
    """
    from modules.campaign.campaign_logger import campaign_logger

    async def event_generator():
        """Generate SSE events from campaign logs."""
        queue = await campaign_logger.subscribe(campaign_id)

        try:
            while True:
                # Wait for new log entry
                log_entry = await queue.get()

                # Format as SSE
                yield f"data: {json.dumps(log_entry)}\n\n"

        except asyncio.CancelledError:
            # Client disconnected
            await campaign_logger.unsubscribe(campaign_id, queue)
            raise

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.delete("/{campaign_id}")
async def delete_campaign(campaign_id: str, req: Request):
    """
    Delete a campaign.

    Warning: This will also delete all associated data (replies, matched posts, etc.)
    """
    try:
        from bson import ObjectId
        db = req.app.state.db

        # Delete campaign and all related data
        await db.campaigns.delete_one({"_id": ObjectId(campaign_id)})
        await db.matched_posts.delete_many({"campaign_id": ObjectId(campaign_id)})
        await db.campaign_replies.delete_many({"campaign_id": ObjectId(campaign_id)})
        await db.interaction_map.delete_many({"campaign_id": ObjectId(campaign_id)})

        logger.info(f"Campaign {campaign_id} deleted")

        return {
            "success": True,
            "campaign_id": campaign_id,
            "message": "Campaign deleted successfully"
        }

    except Exception as e:
        logger.error(f"Error deleting campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{campaign_id}/matched-posts")
async def get_matched_posts(
    campaign_id: str,
    req: Request,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    Get matched posts for a campaign.

    Query parameters:
    - status: Filter by reply status (pending, replied, failed)
    - limit: Number of posts to return
    - offset: Number of posts to skip
    """
    try:
        from bson import ObjectId
        db = req.app.state.db

        # Build query
        query = {"campaign_id": ObjectId(campaign_id)}
        if status:
            query["reply_status"] = status

        # Get posts
        cursor = db.matched_posts.find(query).sort("found_at", -1).skip(offset).limit(limit)
        posts = await cursor.to_list(length=limit)

        # Get total count
        total = await db.matched_posts.count_documents(query)

        # Convert ObjectId to string
        for post in posts:
            post["_id"] = str(post["_id"])
            post["campaign_id"] = str(post["campaign_id"])

        return {
            "success": True,
            "posts": posts,
            "total": total,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error getting matched posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))
