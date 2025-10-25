#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MongoDB Database Connection

This module provides async MongoDB connection management for the AI Character
Agent System using the Motor driver. It handles connection initialization,
collection setup, and index creation for optimal database performance.
"""

import logging
from typing import Dict, List, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, TEXT

from utils.config import get_config

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    pass


class MongoDBManager:
    """
    MongoDB connection and management class.
    
    Handles database connection, collection management, and index creation
    for the AI Character Agent System.
    """
    
    # Required collections for the application
    REQUIRED_COLLECTIONS = [
        'users', 'campaigns', 'replies', 'tracked_links', 'clicks', 'analytics'
    ]
    
    def __init__(self):
        """Initialize MongoDB manager with configuration."""
        config = get_config()
        self.mongodb_config = config["mongodb"]
        self.uri = self.mongodb_config["uri"]
        self.db_name = self.mongodb_config["db_name"]
        self.client = None
        self.database = None
    
    async def connect(self) -> AsyncIOMotorDatabase:
        """
        Establish connection to MongoDB and initialize database.
        
        Returns:
            MongoDB database instance
            
        Raises:
            DatabaseError: If connection fails
        """
        try:
            self.client = AsyncIOMotorClient(self.uri)
            self.database = self.client[self.db_name]
            
            # Test connection
            await self._test_connection()
            
            # Initialize database structure
            await self._initialize_database()
            
            logger.info(f"Successfully connected to MongoDB: {self.db_name}")
            return self.database
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise DatabaseError(f"Database connection failed: {e}")
    
    async def _test_connection(self) -> None:
        """Test database connection by pinging the server."""
        try:
            await self.client.admin.command('ping')
        except Exception as e:
            raise DatabaseError(f"Database ping failed: {e}")
    
    async def _initialize_database(self) -> None:
        """Initialize database collections and indexes."""
        await self._create_collections()
        await self._create_indexes()
    
    async def _create_collections(self) -> None:
        """Create required collections if they don't exist."""
        existing_collections = await self.database.list_collection_names()
        
        for collection_name in self.REQUIRED_COLLECTIONS:
            if collection_name not in existing_collections:
                await self.database.create_collection(collection_name)
                logger.info(f"Created collection: {collection_name}")
    
    async def _create_indexes(self) -> None:
        """Create necessary indexes for optimal database performance."""
        index_definitions = self._get_index_definitions()
        
        for collection_name, indexes in index_definitions.items():
            collection = self.database[collection_name]
            
            try:
                if indexes:
                    await collection.create_indexes(indexes)
                    logger.debug(f"Created {len(indexes)} indexes for {collection_name}")
            except Exception as e:
                logger.warning(f"Failed to create indexes for {collection_name}: {e}")
    
    def _get_index_definitions(self) -> Dict[str, List[IndexModel]]:
        """
        Define indexes for all collections.
        
        Returns:
            Dictionary mapping collection names to their index definitions
        """
        return {
            'users': [
                IndexModel([("wallet_address", ASCENDING), ("chain_type", ASCENDING)], unique=True),
                IndexModel([("email", ASCENDING)], unique=True, sparse=True),
                IndexModel([("created_at", ASCENDING)]),
            ],
            'campaigns': [
                IndexModel([("status", ASCENDING)]),
                IndexModel([("created_at", ASCENDING)]),
                IndexModel([("name", TEXT)]),
            ],
            'replies': [
                IndexModel([("campaign_id", ASCENDING), ("created_at", ASCENDING)]),
                IndexModel([("campaign_id", ASCENDING), ("target_tweet_id", ASCENDING)]),
                IndexModel([("reply_tweet_id", ASCENDING)], unique=True, sparse=True),
                IndexModel([("target_user", ASCENDING)]),
            ],
            'tracked_links': [
                IndexModel([("short_code", ASCENDING)], unique=True),
                IndexModel([("campaign_id", ASCENDING)]),
                IndexModel([("created_at", ASCENDING)]),
            ],
            'clicks': [
                IndexModel([("short_code", ASCENDING), ("timestamp", ASCENDING)]),
                IndexModel([("campaign_id", ASCENDING), ("timestamp", ASCENDING)]),
                IndexModel([("ip_address", ASCENDING)]),
            ],
            'analytics': [
                IndexModel([("campaign_id", ASCENDING), ("date", ASCENDING)]),
                IndexModel([("date", ASCENDING)]),
            ]
        }
    
    async def close(self) -> None:
        """Close database connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get database and collection statistics.
        
        Returns:
            Dictionary containing database statistics
        """
        try:
            stats = {}
            
            # Database stats
            db_stats = await self.database.command("dbStats")
            stats["database"] = {
                "name": self.db_name,
                "collections": db_stats.get("collections", 0),
                "indexes": db_stats.get("indexes", 0),
                "data_size": db_stats.get("dataSize", 0),
                "storage_size": db_stats.get("storageSize", 0)
            }
            
            # Collection stats
            stats["collections"] = {}
            for collection_name in self.REQUIRED_COLLECTIONS:
                try:
                    collection_stats = await self.database.command("collStats", collection_name)
                    stats["collections"][collection_name] = {
                        "count": collection_stats.get("count", 0),
                        "size": collection_stats.get("size", 0),
                        "total_index_size": collection_stats.get("totalIndexSize", 0)
                    }
                except Exception as e:
                    stats["collections"][collection_name] = {"error": str(e)}
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {"error": str(e)}


# Global database manager instance
_db_manager = None


async def get_database() -> AsyncIOMotorDatabase:
    """
    Get MongoDB database instance (singleton pattern).
    
    Returns:
        MongoDB database instance
        
    Raises:
        DatabaseError: If connection fails
    """
    global _db_manager
    
    if _db_manager is None:
        _db_manager = MongoDBManager()
    
    if _db_manager.database is None:
        await _db_manager.connect()
    
    return _db_manager.database


async def close_database() -> None:
    """Close database connection."""
    global _db_manager
    
    if _db_manager:
        await _db_manager.close()
        _db_manager = None


async def get_database_stats() -> Dict[str, Any]:
    """
    Get database statistics.
    
    Returns:
        Dictionary containing database statistics
    """
    global _db_manager
    
    if _db_manager and _db_manager.database:
        return await _db_manager.get_collection_stats()
    
    return {"error": "Database not connected"}


# Backward compatibility functions
async def create_collections_if_not_exist(db: AsyncIOMotorDatabase) -> None:
    """Legacy function for backward compatibility."""
    logger.warning("create_collections_if_not_exist is deprecated, use MongoDBManager instead")


async def create_indexes(db: AsyncIOMotorDatabase) -> None:
    """Legacy function for backward compatibility."""
    logger.warning("create_indexes is deprecated, use MongoDBManager instead")