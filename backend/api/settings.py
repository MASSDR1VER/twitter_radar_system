#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Settings API - Manage system settings, API keys, and Twitter account.
"""

import logging
import json
import os
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settings")


class TwitterCookiesRequest(BaseModel):
    """Request model for Twitter cookies."""
    ct0: Optional[str] = None
    auth_token: Optional[str] = None
    kdt: Optional[str] = None


class APIKeysRequest(BaseModel):
    """Request model for API keys."""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    bitly_api_key: Optional[str] = None


@router.post("/twitter/validate")
async def validate_twitter_cookies(request: Request):
    """
    Validate Twitter cookies and save if valid.

    Accepts either:
    1. Simple format: {"ct0": "...", "auth_token": "...", "kdt": "..."}
    2. Cookie array format: [{"name": "ct0", "value": "..."}, ...]

    Returns:
        Validation status and user info
    """
    try:
        twitter_adapter = request.app.state.twitter_adapter

        # Parse request body
        body = await request.json()

        # Extract cookies from either format
        cookie_dict = {}

        if isinstance(body, list):
            # Cookie array format from browser extension
            for cookie in body:
                if cookie.get("name") in ["ct0", "auth_token", "kdt"]:
                    cookie_dict[cookie["name"]] = cookie["value"]
        elif isinstance(body, dict):
            # Simple format
            cookie_dict = {
                "ct0": body.get("ct0"),
                "auth_token": body.get("auth_token"),
                "kdt": body.get("kdt")
            }

        # Validate required fields
        if not all([cookie_dict.get("ct0"), cookie_dict.get("auth_token"), cookie_dict.get("kdt")]):
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON format. Must contain ct0, auth_token, and kdt"
            )

        # Try to authenticate with cookies
        from modules.integrations.twitter_adapter import TwitterAdapter
        temp_adapter = TwitterAdapter()

        # Load cookies into client
        from platforms.twitter import Client
        temp_client = Client(language='en-US')
        temp_client.load_cookies(cookie_dict)

        # Try to get user info
        try:
            user = await temp_client.user()

            if user:
                # Cookies are valid, save to file
                cookie_file = os.path.join(os.path.dirname(__file__), "..", "cookie.json")
                with open(cookie_file, 'w') as f:
                    json.dump(cookie_dict, f, indent=2)

                # Update the main twitter adapter
                await twitter_adapter.initialize_from_file(cookie_file)

                return {
                    "success": True,
                    "message": "Twitter cookies validated and saved successfully",
                    "user": {
                        "id": user.id,
                        "username": user.screen_name,
                        "name": user.name,
                        "avatar_url": getattr(user, 'profile_image_url', None) or getattr(user, 'profile_image_url_https', None),
                        "followers_count": user.followers_count,
                        "following_count": getattr(user, 'friends_count', 0) or getattr(user, 'following_count', 0),
                        "verified": getattr(user, 'verified', False)
                    }
                }
            else:
                raise HTTPException(status_code=401, detail="Failed to authenticate with provided cookies")

        except Exception as e:
            logger.error(f"Twitter authentication failed: {e}")
            raise HTTPException(status_code=401, detail=f"Invalid Twitter cookies: {str(e)}")

    except Exception as e:
        logger.error(f"Error validating Twitter cookies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/twitter/account")
async def get_twitter_account(request: Request):
    """
    Get current Twitter account information.

    Returns:
        Twitter account details if authenticated
    """
    try:
        twitter_adapter = request.app.state.twitter_adapter

        if not twitter_adapter.is_authenticated:
            return {
                "authenticated": False,
                "message": "No Twitter account configured"
            }

        user = twitter_adapter.user

        if user:
            return {
                "authenticated": True,
                "user": {
                    "id": user.id,
                    "username": user.screen_name,
                    "name": user.name,
                    "avatar_url": getattr(user, 'profile_image_url', None) or getattr(user, 'profile_image_url_https', None),
                    "followers_count": user.followers_count,
                    "following_count": getattr(user, 'friends_count', 0) or getattr(user, 'following_count', 0),
                    "verified": getattr(user, 'verified', False)
                }
            }
        else:
            return {
                "authenticated": False,
                "message": "Twitter authentication failed"
            }

    except Exception as e:
        logger.error(f"Error getting Twitter account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api-keys")
async def save_api_keys(keys: APIKeysRequest):
    """
    Save API keys to environment.

    Args:
        keys: API keys to save

    Returns:
        Success status
    """
    try:
        # Update environment variables
        if keys.openai_api_key:
            os.environ["OPENAI_API_KEY"] = keys.openai_api_key

        if keys.anthropic_api_key:
            os.environ["ANTHROPIC_API_KEY"] = keys.anthropic_api_key

        if keys.bitly_api_key:
            os.environ["BITLY_API_KEY"] = keys.bitly_api_key

        # Optionally save to .env file
        env_file = os.path.join(os.path.dirname(__file__), "..", ".env")

        # Read existing .env
        env_lines = []
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                env_lines = f.readlines()

        # Update or add keys
        keys_to_update = {}
        if keys.openai_api_key:
            keys_to_update["OPENAI_API_KEY"] = keys.openai_api_key
        if keys.anthropic_api_key:
            keys_to_update["ANTHROPIC_API_KEY"] = keys.anthropic_api_key
        if keys.bitly_api_key:
            keys_to_update["BITLY_API_KEY"] = keys.bitly_api_key

        # Update existing lines or add new ones
        updated_keys = set()
        new_lines = []

        for line in env_lines:
            line_stripped = line.strip()
            if '=' in line_stripped and not line_stripped.startswith('#'):
                key = line_stripped.split('=')[0]
                if key in keys_to_update:
                    new_lines.append(f"{key}={keys_to_update[key]}\n")
                    updated_keys.add(key)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        # Add keys that weren't in the file
        for key, value in keys_to_update.items():
            if key not in updated_keys:
                new_lines.append(f"{key}={value}\n")

        # Write back to .env
        with open(env_file, 'w') as f:
            f.writelines(new_lines)

        return {
            "success": True,
            "message": "API keys saved successfully"
        }

    except Exception as e:
        logger.error(f"Error saving API keys: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api-keys/status")
async def get_api_keys_status():
    """
    Get status of configured API keys (without revealing the keys).

    Returns:
        Status of each API key
    """
    try:
        return {
            "openai": {
                "configured": bool(os.getenv("OPENAI_API_KEY")),
                "key_preview": os.getenv("OPENAI_API_KEY", "")[:10] + "..." if os.getenv("OPENAI_API_KEY") else None
            },
            "anthropic": {
                "configured": bool(os.getenv("ANTHROPIC_API_KEY")),
                "key_preview": os.getenv("ANTHROPIC_API_KEY", "")[:10] + "..." if os.getenv("ANTHROPIC_API_KEY") else None
            },
            "bitly": {
                "configured": bool(os.getenv("BITLY_API_KEY")),
                "key_preview": os.getenv("BITLY_API_KEY", "")[:10] + "..." if os.getenv("BITLY_API_KEY") else None
            }
        }

    except Exception as e:
        logger.error(f"Error getting API keys status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
