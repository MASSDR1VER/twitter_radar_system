#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Campaign Logger - Centralized logging with SSE broadcasting.
Allows real-time campaign progress updates to be sent to frontend.
"""

import logging
import asyncio
from typing import Dict, Set
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class CampaignLogger:
    """
    Manages campaign-specific logging with SSE broadcasting capability.
    """

    def __init__(self):
        """Initialize the campaign logger."""
        # Store active SSE connections per campaign
        # campaign_id -> set of queues
        self._subscribers: Dict[str, Set[asyncio.Queue]] = defaultdict(set)

        # Store recent logs per campaign (last 100 messages)
        self._log_history: Dict[str, list] = defaultdict(list)
        self._max_history = 100

    async def subscribe(self, campaign_id: str) -> asyncio.Queue:
        """
        Subscribe to campaign logs.

        Args:
            campaign_id: Campaign ID to subscribe to

        Returns:
            Queue that will receive log messages
        """
        queue = asyncio.Queue()
        self._subscribers[campaign_id].add(queue)

        logger.info(f"New SSE subscriber for campaign {campaign_id}")

        # Send log history to new subscriber
        for log_entry in self._log_history[campaign_id]:
            await queue.put(log_entry)

        return queue

    async def unsubscribe(self, campaign_id: str, queue: asyncio.Queue):
        """
        Unsubscribe from campaign logs.

        Args:
            campaign_id: Campaign ID
            queue: Queue to remove
        """
        if campaign_id in self._subscribers:
            self._subscribers[campaign_id].discard(queue)
            logger.info(f"SSE subscriber removed for campaign {campaign_id}")

    async def log(self, campaign_id: str, level: str, message: str, data: dict = None):
        """
        Log a message for a campaign and broadcast to subscribers.

        Args:
            campaign_id: Campaign ID
            level: Log level (info, warning, error, success)
            message: Log message
            data: Optional additional data
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "data": data or {}
        }

        # Add to history
        self._log_history[campaign_id].append(log_entry)

        # Keep only last N messages
        if len(self._log_history[campaign_id]) > self._max_history:
            self._log_history[campaign_id] = self._log_history[campaign_id][-self._max_history:]

        # Broadcast to all subscribers
        if campaign_id in self._subscribers:
            dead_queues = set()
            for queue in self._subscribers[campaign_id]:
                try:
                    await queue.put(log_entry)
                except Exception as e:
                    logger.error(f"Failed to send to subscriber: {e}")
                    dead_queues.add(queue)

            # Remove dead queues
            for queue in dead_queues:
                self._subscribers[campaign_id].discard(queue)

    async def info(self, campaign_id: str, message: str, **data):
        """Log info message."""
        await self.log(campaign_id, "info", message, data)

    async def warning(self, campaign_id: str, message: str, **data):
        """Log warning message."""
        await self.log(campaign_id, "warning", message, data)

    async def error(self, campaign_id: str, message: str, **data):
        """Log error message."""
        await self.log(campaign_id, "error", message, data)

    async def success(self, campaign_id: str, message: str, **data):
        """Log success message."""
        await self.log(campaign_id, "success", message, data)

    def get_subscriber_count(self, campaign_id: str) -> int:
        """Get number of active subscribers for a campaign."""
        return len(self._subscribers.get(campaign_id, set()))


# Global instance
campaign_logger = CampaignLogger()
