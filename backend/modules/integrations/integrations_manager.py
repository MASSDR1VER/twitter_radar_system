#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integrations Manager for the AI Character Agent System.
Manages all external platform integrations for character social presence.
"""

import logging
import asyncio
import os
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from .twitter_adapter import TwitterAdapter

logger = logging.getLogger(__name__)

class IntegrationsManager:
    """
    Manager for all platform integrations.
    Acts as a central point for interacting with various social media platforms.
    """
    
    def __init__(self, db_client):
        """
        Initialize the integrations manager.
        
        Args:
            db_client: Database client for storing integration data
            config: Configuration dictionary for all platform adapters
        """
        self.db = db_client
        self.twitter_adapter = TwitterAdapter(db_client)
        # Other adapters to be added in the future can be defined here
        # self.instagram_adapter = InstagramAdapter(db_client)
        # self.facebook_adapter = FacebookAdapter(db_client)
        
        # Initialize platform adapters
        self.platform_adapters = {
            "twitter": self.twitter_adapter
            # As new platforms are added, they will be added here.
            # "instagram": self.instagram_adapter,
            # "facebook": self.facebook_adapter
        }
        
        logger.info("Integrations manager initialized")
        
        # Future adapters can be added here
        # "instagram": InstagramAdapter(self.config.get("instagram", {})),
        # "facebook": FacebookAdapter(self.config.get("facebook", {})),
        # "linkedin": LinkedInAdapter(self.config.get("linkedin", {})),

    async def _get_character_update_query(self, character_id: str):
        """
        Get the appropriate database query for updating a character.
        Handles both character_id (UUID) and _id (ObjectId) formats.
        """
        # First try character_id field
        character = await self.db.characters.find_one({"character_id": character_id})
        if character:
            return {"character_id": character_id}
        
        # If not found and looks like ObjectId, try _id field
        if len(character_id) == 24:
            try:
                from bson import ObjectId
                character = await self.db.characters.find_one({"_id": ObjectId(character_id)})
                if character:
                    return {"_id": ObjectId(character_id)}
            except:
                pass
        
        return None
    
    async def initialize(self):
        """
        Initialize all platform adapters and load existing connections
        """
        
        # Twitter bağlantılarını yükle
        await self.twitter_adapter.initialize_connections()
        
        # Gelecekte eklenecek diğer platform bağlantıları
        # await self.instagram_adapter.initialize_connections()
        # await self.facebook_adapter.initialize_connections()

        # Start periodic connection check task
        asyncio.create_task(self._periodic_connection_check())
        
        logger.info("Platform connections initialized successfully")

    async def _periodic_connection_check(self, interval_minutes=30):
        """
        Periodically checks all platform connections
        Args:
            interval_minutes: Interval in minutes for checking connections
        """
        while True:
            try:
                # Get all characters with social accounts from database
                characters = await self.db.characters.find(
                    {"social_accounts": {"$exists": True}}
                ).to_list(length=None)
                
                for character in characters:
                    character_id = character["_id"] # type: ignore
                    
                    # If Twitter account exists, check connection
                    if "twitter" in character.get("social_accounts", {}):
                        # If account is not active and there is no auth error, try to reconnect
                        twitter_account = character["social_accounts"]["twitter"] # type: ignore
                        if not twitter_account.get("is_active", False) and not twitter_account.get("auth_error", False):
                            # If time since error is less than 1 hour, try to reconnect
                            last_error_time = twitter_account.get("last_error_time")
                            if last_error_time:
                                if isinstance(last_error_time, str):
                                    last_error_time = datetime.fromisoformat(last_error_time.replace("Z", "+00:00"))
                                
                                time_since_error = (datetime.now() - last_error_time).total_seconds()
                                if time_since_error < 3600:  # 1 hour (in seconds)
                                    continue
                            
                            # Try to reconnect
                            if "cookies" in twitter_account:
                                await self.twitter_adapter.authenticate(
                                    character_id=character_id,
                                    cookies=twitter_account["cookies"],
                                    language=twitter_account.get("language", "en"),
                                    proxy=twitter_account.get("proxy"),
                                    captcha_solver=twitter_account.get("captcha_solver")
                                )
                
                # Wait for next check
                await asyncio.sleep(interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Error in periodic connection check: {e}")
                await asyncio.sleep(60)  # If error, wait 1 minute

    async def connect_platform(
        self, 
        character_id: str, 
        platform: str, 
        credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Connect a character to a social media platform.
        
        Args:
            character_id: Character ID
            platform: Platform name (twitter, instagram, etc.)
            credentials: Platform-specific authentication credentials
            
        Returns:
            Connection result with success status
        """
        try:
            # Check if platform is supported
            if platform not in self.platform_adapters:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform}"
                }
            
            adapter = self.platform_adapters[platform]
            
            logger.info(f"integrations_manager.connect_platform: looking for character_id={character_id}")
            
            # First try to find by character_id (UUID format)
            character = await self.db.characters.find_one({"character_id": character_id})
            
            # If not found and it looks like a MongoDB ObjectId, try _id
            if not character and len(character_id) == 24:
                try:
                    from bson import ObjectId
                    character = await self.db.characters.find_one({"_id": ObjectId(character_id)})
                except:
                    # If ObjectId conversion fails, character remains None
                    pass
            
            logger.info(f"integrations_manager.connect_platform: character found = {character is not None}")
            if not character:
                logger.error(f"integrations_manager.connect_platform: Character not found for ID {character_id}")
                return {"success": False, "error": "Character not found"}
                
            # if social_accounts field is not in character, create it
            if "social_accounts" not in character:
                update_query = await self._get_character_update_query(character_id)
                if update_query:
                    await self.db.characters.update_one(
                        update_query,
                        {"$set": {"social_accounts": {}}}
                    )
            # if social_accounts is a list, convert it to a dictionary
            elif isinstance(character["social_accounts"], list): # type: ignore
                # convert from old format to new format
                new_social_accounts = {}
                for account in character["social_accounts"]: # type: ignore
                    if "platform" in account:
                        platform_name = account["platform"]
                        new_social_accounts[platform_name] = account
                        
                update_query = await self._get_character_update_query(character_id)
                if update_query:
                    await self.db.characters.update_one(
                        update_query,
                        {"$set": {"social_accounts": new_social_accounts}}
                    )

            # Authenticate with the platform
            # Each platform adapter requires different credentials
            if platform == "twitter":
                auth_result = await adapter.authenticate(
                    character_id,
                    credentials.get("cookies"),
                    credentials.get("language"),
                    credentials.get("proxy"),
                    credentials.get("captcha_solver")
                )
            else:
                # Generic authentication pattern for other platforms
                auth_result = await adapter.authenticate(character_id, credentials)
            
            if not auth_result["success"]:
                return auth_result
            
            # Store platform connection in database
            # Use flexible lookup for character data
            character_data = await self.db.characters.find_one({"character_id": character_id})
            if not character_data and len(character_id) == 24:
                try:
                    from bson import ObjectId
                    character_data = await self.db.characters.find_one({"_id": ObjectId(character_id)})
                except:
                    pass

            social_accounts = {}
            if character_data and "social_accounts" in character_data:
                if isinstance(character_data.get("social_accounts"), list):
                    # Listedeki her hesabı platforma göre nesneye dönüştür
                    for account in character_data.get("social_accounts"):
                        if "platform" in account and account.get("platform"):
                            social_accounts[account.get("platform")] = account
                else:
                    social_accounts = character_data.get("social_accounts")

            social_accounts[platform] = {
                "platform": platform,
                "connected_at": datetime.now(),
                "username": auth_result.get("username"),
                "user_id": auth_result.get("user_id"),
                "display_name": auth_result.get("display_name"),
                "profile_image_url": auth_result.get("profile_image_url"),
                "bio": auth_result.get("bio"),
                "location": auth_result.get("location"),
                "url": auth_result.get("url"),
                "created_at": auth_result.get("created_at"),
                "verified": auth_result.get("verified"),
                "followers_count": auth_result.get("followers_count"),
                "following_count": auth_result.get("following_count"),
                "profile_banner_url": auth_result.get("profile_banner_url"),
                "profile_image_url": auth_result.get("profile_image_url"),
                "is_active": True,
                "cookies": auth_result.get("cookies"),
                "language": auth_result.get("language"),
                "proxy": auth_result.get("proxy"),
                "captcha_solver": auth_result.get("captcha_solver"),
                "auth_error": auth_result.get("auth_error"),
                "last_error": auth_result.get("last_error"),
            }
            
            # Update using the helper function
            update_query = await self._get_character_update_query(character_id)
            if update_query:
                await self.db.characters.update_one(
                    update_query,
                    {"$set": {"social_accounts": social_accounts}}
                )

            logger.debug(f"Character {character_id} connected to {platform}")
            
            return {
                "success": True,
                "platform": platform,
                "username": auth_result.get("username"),
                "display_name": auth_result.get("display_name")
            }
            
        except Exception as e:
            logger.error(f"Error connecting character {character_id} to {platform}: {e}")
            return {
                "success": False,
                "error": f"Connection error: {str(e)}"
            }
    
    async def disconnect_platform(self, character_id: str, platform: str) -> Dict[str, Any]:
        """
        Disconnect a character from a social media platform.
        
        Args:
            character_id: Character ID
            platform: Platform name (twitter, instagram, etc.)
            
        Returns:
            Disconnection result with success status
        """
        try:
            # Check if platform is supported
            if platform not in self.platform_adapters:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform}"
                }
            
            # Update database to mark connection as inactive
            update_query = await self._get_character_update_query(character_id)
            if not update_query:
                return {"success": False, "error": "Character not found"}
            
            result = await self.db.characters.update_one(
                update_query,
                {"$set": {f"social_accounts.{platform}.is_active": False}}
            )
            
            if result.modified_count == 0:
                return {
                    "success": False,
                    "error": f"Character is not connected to {platform} or doesn't exist"
                }
            
            logger.debug(f"Character {character_id} disconnected from {platform}")
            
            return {
                "success": True,
                "platform": platform
            }
            
        except Exception as e:
            logger.error(f"Error disconnecting character {character_id} from {platform}: {e}")
            return {
                "success": False,
                "error": f"Disconnection error: {str(e)}"
            }
    
    async def create_post(
        self,
        character_id: str,
        platform: str,
        content: str = '',
        media_ids: list[str] = None,
        scheduled_time: datetime = None,
        **platform_options
    ) -> Dict[str, Any]:
        """
        Create a post on a social media platform.
        
        Args:
            character_id: Character ID
            platform: Platform name (twitter, instagram, etc.)
            content: Post content
            media_ids: Optional list of media IDs
            scheduled_time: Optional scheduled time
            **platform_options: Platform-specific options
            
        Returns:
            Dictionary with post creation result
        """
        try:
            # Check if platform is supported
            if platform not in self.platform_adapters:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform}"
                }
            
            adapter = self.platform_adapters[platform]
            
            # Handle scheduled posts
            if scheduled_time and scheduled_time > datetime.now():
                # TODO: Implement scheduled posts
                pass
                
                return {
                    "success": True,
                    "scheduled": True,
                    "post_id": post_id,
                    "scheduled_time": scheduled_time.isoformat()
                }
            
            # Publish immediately
            if platform == "twitter":
                result = await adapter.create_tweet(
                character_id,
                text=content,
                media_ids=media_ids,
                **platform_options
            )

            
            if not result["success"]:
                return result
            
            # Store published post in database
            post_id = await self._store_published_post(
                character_id,
                platform,
                content,
                media_ids,
                result
            )
            
            return {
                "success": True,
                "post_id": post_id,
                "platform_post_id": result.get("tweet_id") or result.get("post_id"),
                "url": result.get("url"),
                "platform": platform
            }
            
        except Exception as e:
            logger.error(f"Error creating post on {platform} through integrations manager: {e}")
            return {"success": False, "error": f"Error creating post: {str(e)}"}
        

    async def search_content(
        self,
        character_id: str,
        platform: str,
        query: str,
        count: int = 20,
        analyze: bool = True,
        **platform_options
    ) -> Dict[str, Any]:
        """
        Search for content on a social platform.
        
        Args:
            character_id: Character ID
            platform: Platform name (twitter, instagram, etc.)
            query: Search query
            count: Number of results to retrieve
            analyze: Whether to analyze the search results with AI
            **platform_options: Platform-specific options
            
        Returns:
            Dictionary with search results
        """
        try:
            # Check if platform is supported
            if platform not in self.platform_adapters:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform}"
                }
                
            # Get platform adapter
            adapter = self.platform_adapters[platform]
            
            # Platform-specific search
            if platform == "twitter":
                return await adapter.search_tweet(
                    character_id,
                    query=query,
                    count=count,
                    analyze=analyze,
                    **platform_options
                )

        except Exception as e:
            logger.error(f"Error searching on {platform} through integrations manager: {e}")
            return {"success": False, "error": f"Error searching content: {str(e)}"}
    
    async def get_feed(
        self,
        character_id: str,
        platform: str,
        count: int = 20,
        analyze: bool = True,
        **platform_options
    ) -> Dict[str, Any]:
        """
        Get the content feed from a platform.
        
        Args:
            character_id: Character ID
            platform: Platform name (twitter, instagram, etc.)
            count: Number of items to retrieve
            analyze: Whether to analyze the feed with AI
            **platform_options: Platform-specific options
            
        Returns:
            Dictionary with feed items
        """
        try:
            # Check if platform is supported
            if platform not in self.platform_adapters:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform}"
                }
                
            # Get platform adapter
            adapter = self.platform_adapters[platform]
            
            # Platform-specific feed retrieval
            if platform == "twitter":
                return await adapter.get_timeline(
                    character_id,
                    count=count,
                    analyze=analyze,
                    **platform_options
                )
                
        except Exception as e:
            logger.error(f"Error getting feed from {platform} through integrations manager: {e}")
            return {"success": False, "error": f"Error getting feed: {str(e)}"}


    async def like_content(
        self,
        character_id: str,
        platform: str,
        content_id: str
    ) -> Dict[str, Any]:
        """
        Like content on a platform.
        
        Args:
            character_id: Character ID
            platform: Platform name (twitter, instagram, etc.)
            content_id: ID of the content to like
            
        Returns:
            Dictionary with like result
        """
        try:
            # Check if platform is supported
            if platform not in self.platform_adapters:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform}"
                }
                
            # Get platform adapter
            adapter = self.platform_adapters[platform]
            
            # Platform-specific like action
            result = None
            if platform == "twitter":
                result = await adapter.favorite_tweet(
                    character_id,
                    tweet_id=content_id
                )
                
            if not result or not result["success"]:
                return result or {"success": False, "error": "Unknown error"}
            
            # Log the action in database
            action_log = {
                "_id": str(uuid.uuid4()),
                "character_id": character_id,
                "platform": platform,
                "action_type": "like",
                "target_id": content_id,
                "created_at": datetime.now()
            }
            
            await self.db.social_actions.insert_one(action_log)
            
            return {
                "success": True,
                "content_id": content_id,
                "platform": platform,
                "action": "like"
            }
            
        except Exception as e:
            logger.error(f"Error liking content on {platform} through integrations manager: {e}")
            return {"success": False, "error": f"Error liking content: {str(e)}"}
    

    async def share_content(
        self,
        character_id: str,
        platform: str,
        content_id: str,
        **platform_options
    ) -> Dict[str, Any]:
        """
        Share/repost content on a platform.
        
        Args:
            character_id: Character ID
            platform: Platform name (twitter, instagram, etc.)
            content_id: ID of the content to share
            **platform_options: Platform-specific options
            
        Returns:
            Dictionary with share result
        """
        try:
            # Check if platform is supported
            if platform not in self.platform_adapters:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform}"
                }
                
            # Get platform adapter
            adapter = self.platform_adapters[platform]
            
            # Platform-specific share action
            result = None
            if platform == "twitter":
                result = await adapter.retweet(
                    character_id,
                    tweet_id=content_id
                )
                
            if not result or not result["success"]:
                return result or {"success": False, "error": "Unknown error"}
            
            # Log the action and create a post record
            action_log = {
                "_id": str(uuid.uuid4()),
                "character_id": character_id,
                "platform": platform,
                "action_type": "share",
                "target_id": content_id,
                "created_at": datetime.now()
            }
            
            await self.db.social_actions.insert_one(action_log)
            
            # Create post record for the share/repost
            post_id = str(uuid.uuid4())
            post_data = {
                "_id": post_id,
                "character_id": character_id,
                "platform": platform,
                "platform_post_id": content_id,
                "content": "",  # Shares don't typically have content
                "created_at": datetime.now(),
                "status": "published",
                "post_type": "share",
                "metrics": {
                    "likes": 0,
                    "shares": 0,
                    "comments": 0
                },
                "metadata": {
                    "original_content_id": content_id
                }
            }
            
            await self.db.social_posts.insert_one(post_data)
            
            # Update result to include post_id
            result["post_id"] = post_id
            result["platform"] = platform
            
            return result
            
        except Exception as e:
            logger.error(f"Error sharing content on {platform} through integrations manager: {e}")
            return {"success": False, "error": f"Error sharing content: {str(e)}"}
    

    async def upload_media(
        self,
        character_id: str,
        platform: str,
        source: str,
        **platform_options
    ) -> Dict[str, Any]:
        """
        Upload media to a platform.
        
        Args:
            character_id: Character ID
            platform: Platform name (twitter, instagram, etc.)
            source: Path to the media file
            **platform_options: Platform-specific options
            
        Returns:
            Dictionary with upload result and media ID
        """
        try:
            # Check if platform is supported
            if platform not in self.platform_adapters:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform}"
                }
                
            # Get platform adapter
            adapter = self.platform_adapters[platform]
            
            # Platform-specific upload
            if platform == "twitter":
                result = await adapter.upload_media(
                    character_id,
                    source=source,
                    alt_text=platform_options.get("alt_text"),
                    wait_for_completion=platform_options.get("wait_for_completion", True),
                    is_long_video=platform_options.get("is_long_video", False)
                )

                
            return result
            
        except Exception as e:
            logger.error(f"Error uploading media to {platform} through integrations manager: {e}")
            return {"success": False, "error": f"Error uploading media: {str(e)}"}


    async def delete_content(
        self,
        character_id: str,
        platform: str,
        content_id: str
    ) -> Dict[str, Any]:
        """
        Delete content from a platform.
        
        Args:
            character_id: Character ID
            platform: Platform name (twitter, instagram, etc.)
            content_id: ID of the content to delete
            
        Returns:
            Dictionary with deletion result
        """
        try:
            # Check if platform is supported
            if platform not in self.platform_adapters:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform}"
                }
                
            # Get platform adapter
            adapter = self.platform_adapters[platform]
            
            # Platform-specific deletion
            result = None
            if platform == "twitter":
                result = await adapter.delete_tweet(
                    character_id,
                    tweet_id=content_id
                )

                
            if not result or not result["success"]:
                return result or {"success": False, "error": "Unknown error"}
            
            # Update post status in database
            await self.db.social_posts.update_one(
                {"character_id": character_id, "platform": platform, "platform_post_id": content_id},
                {"$set": {"status": "deleted", "deleted_at": datetime.now()}}
            )
            
            return {
                "success": True,
                "content_id": content_id,
                "platform": platform,
                "action": "delete"
            }
            
        except Exception as e:
            logger.error(f"Error deleting content from {platform} through integrations manager: {e}")
            return {"success": False, "error": f"Error deleting content: {str(e)}"}

    async def get_platform_metrics(
        self,
        character_id: str,
        platform: str,
        post_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get metrics for a character's social media presence or specific post.
        
        Args:
            character_id: Character ID
            platform: Platform name (twitter, instagram, etc.)
            post_id: Optional specific post ID to get metrics for
            
        Returns:
            Metrics data with engagement statistics
        """
        try:
            # Check if platform is supported
            if platform not in self.platform_adapters:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform}"
                }
            
            adapter = self.platform_adapters[platform]
            
            # Get metrics for a specific post if ID provided
            if post_id:
                # Get the post from database to find platform-specific ID
                post_data = await self.db.social_posts.find_one({
                    "platform_post_id": post_id,
                    "character_id": character_id,
                    "platform": platform
                })
                
                if not post_data:
                    return {
                        "success": False,
                        "error": "Post not found"
                    }
                
                platform_post_id = post_data.get("platform_post_id")
                
                if platform == "twitter":
                    metrics_result = await adapter.get_tweet_metrics(
                        character_id,
                        platform_post_id
                    )
                else:
                    # Generic metrics pattern for other platforms
                    metrics_result = await adapter.get_post_metrics(
                        character_id,
                        platform_post_id
                    )
                
                if not metrics_result["success"]:
                    return metrics_result
                
                # Update metrics in database
                await self.db.social_posts.update_one(
                    {"_id": post_id},
                    {"$set": {"platform_metrics": metrics_result["metrics"]}}
                )
                
                return {
                    "success": True,
                    "post_id": post_id,
                    "platform": platform,
                    "metrics": metrics_result["metrics"]
                }
            
            # Get overall account metrics if no post ID provided
            # Implement platform-specific account metrics retrieval
            
            return {
                "success": True,
                "character_id": character_id,
                "platform": platform,
                "metrics": {
                    "followers": 0,  # Placeholder
                    "following": 0,  # Placeholder
                    "total_posts": 0,  # Placeholder
                    "total_engagement": 0  # Placeholder
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting metrics from {platform} for character {character_id}: {e}")
            return {
                "success": False,
                "error": f"Metrics error: {str(e)}"
            }
    
    async def get_social_feed(
        self, 
        character_id: str,
        platform: str, 
        count: int = 20
    ) -> Dict[str, Any]:
        """
        Get the latest posts and interactions from a platform feed.
        
        Args:
            character_id: Character ID
            platform: Platform name (twitter, instagram, etc.)
            count: Number of items to retrieve
            
        Returns:
            Feed items with content and interaction data
        """
        try:
            # Check if platform is supported
            if platform not in self.platform_adapters:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform}"
                }
            
            adapter = self.platform_adapters[platform]
            
            # Get platform-specific feed
            if platform == "twitter":
                # Implement timeline retrieval
                # This would be implemented in the TwitterAdapter
                pass
            
            # Return placeholder data
            return {
                "success": True,
                "platform": platform,
                "feed_items": []  # Placeholder
            }
            
        except Exception as e:
            logger.error(f"Error getting feed from {platform} for character {character_id}: {e}")
            return {
                "success": False,
                "error": f"Feed retrieval error: {str(e)}"
            }
    
    async def _schedule_post(
        self,
        character_id: str,
        platform: str,
        content: str,
        media_paths: Optional[List[str]] = None,
        scheduled_time: Optional[datetime] = None
    ) -> str:
        """
        Schedule a post for future publishing.
        
        Args:
            character_id: Character ID
            platform: Platform name
            content: Post content
            media_paths: Optional paths to media files
            scheduled_time: Time to publish the post
            
        Returns:
            Scheduled post ID
        """
        # Create post document
        post = {
            "character_id": character_id,
            "platform": platform,
            "content": content,
            "media_paths": media_paths or [],
            "created_at": datetime.now(),
            "scheduled_for": scheduled_time,
            "published_at": None,
            "status": "scheduled",
            "platform_post_id": None,
            "url": None,
            "platform_metrics": {
                "likes": 0,
                "shares": 0,
                "comments": 0,
                "views": 0
            }
        }
        
        # Insert into database
        result = await self.db.social_posts.insert_one(post)
        return str(result.inserted_id)
    
    async def _store_published_post(
        self,
        character_id: str,
        platform: str,
        content: str,
        media_paths: Optional[List[str]],
        publish_result: Dict[str, Any]
    ) -> str:
        """
        Store published post details in database.
        
        Args:
            character_id: Character ID
            platform: Platform name
            content: Post content
            media_paths: Paths to media files
            publish_result: Result from platform adapter
            
        Returns:
            Stored post ID
        """
        # Create post document
        post = {
            "character_id": character_id,
            "platform": platform,
            "content": content,
            "media_paths": media_paths or [],
            "created_at": datetime.now(),
            "scheduled_for": None,
            "published_at": datetime.now(),
            "status": "published",
            "platform_post_id": publish_result.get("tweet_id") or publish_result.get("post_id"),
            "url": publish_result.get("url"),
            "platform_metrics": {
                "likes": 0,
                "shares": 0,
                "comments": 0,
                "views": 0
            }
        }
        
        # Insert into database
        result = await self.db.social_posts.insert_one(post)
        return str(result.inserted_id)


    async def research_topic(
        self,
        character_id: str,
        platform: str,
        topic: str,
        starting_query: str = None
    ) -> Dict[str, Any]:
        """
        Research a topic on a social platform.
        
        Args:
            character_id: Character ID
            platform: Platform name (twitter, instagram, etc.)
            topic: Topic to research
            starting_query: Starting query (if not provided, platform adapter will create one)
            
        Returns:
            Research results
        """
        try:
            # Check if platform is supported
            if platform not in self.platform_adapters:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform}"
                }
                
            # Get platform adapter
            adapter = self.platform_adapters[platform]
            
            # Platform-specific research
            if platform == "twitter":
                return await adapter.research_twitter_topic(
                    character_id,
                    topic=topic,
                    starting_query=starting_query
                )
                
        except Exception as e:
            logger.error(f"Error researching on {platform} through integrations manager: {e}")
            return {"success": False, "error": f"Error researching topic: {str(e)}"}

    async def get_mentions(
        self,
        character_id: str,
        platform: str,
        count: int = 20,
        **platform_options
    ) -> Dict[str, Any]:
        """
        Get mentions for a character on a platform.
        
        Args:
            character_id: Character ID
            platform: Platform name (twitter, instagram, etc.)
            count: Number of mentions to retrieve
            **platform_options: Platform-specific options
            
        Returns:
            Dictionary with mentions
        """
        try:
            # Check if platform is supported
            if platform not in self.platform_adapters:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform}"
                }
            
            # Get platform adapter
            adapter = self.platform_adapters[platform]
            
            # Platform-specific mentions retrieval
            if platform == "twitter":
                return await adapter.get_mentions(
                    character_id,
                    count=count,
                    **platform_options
                )
            
        except Exception as e:
            logger.error(f"Error getting mentions from {platform} through integrations manager: {e}")
            return {"success": False, "error": f"Error getting mentions: {str(e)}"}

    def get_available_platforms(self):
        """Get list of available platforms."""
        try:
            return list(self.platform_adapters.keys()) if hasattr(self, 'platform_adapters') else []
        except Exception as e:
            raise Exception(f"Platform list failed: {e}")