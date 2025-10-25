#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integrations package for the AI Character Agent System.
Provides social media platform integrations for character agents.
"""

from .twitter_adapter import TwitterAdapter
from .integrations_manager import IntegrationsManager

__all__ = ["TwitterAdapter", "IntegrationsManager"]
