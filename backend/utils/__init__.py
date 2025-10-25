#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utilities Package

This package provides essential utilities and helper functions for the
AI Character Agent System, including configuration management, logging,
authentication, and security utilities.
"""

from .config import get_config, get_config_manager
from .logger import get_logger, set_request_context, clear_request_context
from .auth import (
    SecurityUtils,
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    validate_password,
    validate_email,
    rate_limiter,
    login_tracker
)
from .logging_config import setup_logging

__all__ = [
    # Configuration
    "get_config",
    "get_config_manager",

    # Logging
    "get_logger",
    "set_request_context",
    "clear_request_context",
    "setup_logging",

    # Authentication & Security
    "SecurityUtils",
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "validate_password",
    "validate_email",
    "rate_limiter",
    "login_tracker"
] 