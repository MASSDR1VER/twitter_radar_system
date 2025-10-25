#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tracking API - Click tracking and URL redirection.
"""

import logging
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/r", tags=["tracking"])


@router.get("/{short_code}")
async def redirect_and_track(short_code: str, req: Request):
    """
    Redirect short URL and track the click.

    Flow:
    1. Look up short code in database
    2. Record click event (IP, user-agent, timestamp)
    3. Update click counters
    4. Redirect to original URL
    """
    try:
        db = req.app.state.db
        analytics_collector = req.app.state.analytics_collector

        # Find short link
        link = await db.short_links.find_one({"short_code": short_code})

        if not link:
            raise HTTPException(status_code=404, detail="Short link not found")

        # Get request info
        ip_address = req.client.host if req.client else "unknown"
        user_agent = req.headers.get("user-agent", "unknown")
        referrer = req.headers.get("referer", "")

        # Record click event
        await analytics_collector.record_click_event(
            campaign_id=link.get("campaign_id"),
            short_code=short_code,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer
        )

        logger.info(f"Click tracked: {short_code} -> {link['long_url']}")

        # Redirect to original URL
        return RedirectResponse(url=link["long_url"], status_code=302)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in redirect: {e}")
        raise HTTPException(status_code=500, detail=str(e))
