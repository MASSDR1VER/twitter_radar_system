#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API package for InteractRadar.
Contains all REST API endpoints.
"""

from .campaigns import router as campaigns_router
from .analytics import router as analytics_router
from .tracking import router as tracking_router
from .settings import router as settings_router

__all__ = [
    "campaigns_router",
    "analytics_router",
    "tracking_router",
    "settings_router"
]
