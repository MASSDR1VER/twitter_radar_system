#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenAI API Token Usage and Cost Tracker

This module tracks token usage and calculates costs for OpenAI API calls.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
import tiktoken
from pymongo import MongoClient
from utils.logger import get_logger

logger = get_logger(__name__)


class TokenTracker:
    """
    Tracks OpenAI API token usage and calculates costs.
    """
    
    # Pricing per 1K tokens (USD)
    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4.1-nano-2025-04-14": {"input": 0.005, "output": 0.015},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "text-embedding-3-small": {"input": 0.00002, "output": 0},
        "text-embedding-3-large": {"input": 0.00013, "output": 0}
    }
    
    def __init__(self, db_client):
        """Initialize token tracker with database connection."""
        self.db = db_client
        self.usage_collection = self.db["api_usage"]
        self.encoders = {}
        
    def get_encoder(self, model: str):
        """Get tiktoken encoder for model."""
        if model not in self.encoders:
            try:
                if "gpt-4" in model:
                    self.encoders[model] = tiktoken.encoding_for_model("gpt-4")
                elif "gpt-3.5" in model:
                    self.encoders[model] = tiktoken.encoding_for_model("gpt-3.5-turbo")
                else:
                    self.encoders[model] = tiktoken.get_encoding("cl100k_base")
            except:
                self.encoders[model] = tiktoken.get_encoding("cl100k_base")
        return self.encoders[model]
    
    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text for given model."""
        try:
            encoder = self.get_encoder(model)
            return len(encoder.encode(text))
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Fallback estimation: ~4 chars per token
            return len(text) // 4
    
    async def track_usage(
        self,
        character_id: str,
        model: str,
        input_text: str,
        output_text: str,
        usage_type: str = "text_generation",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track API usage and calculate cost.
        
        Args:
            character_id: Character making the request
            model: Model used
            input_text: Input prompt text
            output_text: Generated output text
            usage_type: Type of usage (text_generation, embedding)
            metadata: Additional metadata
            
        Returns:
            Usage statistics and cost
        """
        try:
            # Count tokens
            input_tokens = self.count_tokens(input_text, model)
            output_tokens = self.count_tokens(output_text, model) if output_text else 0
            
            # Get pricing
            model_key = model
            if model not in self.PRICING:
                # Default to GPT-4 pricing if model not found
                model_key = "gpt-4"
                logger.warning(f"Model {model} not in pricing table, using GPT-4 pricing")
            
            pricing = self.PRICING[model_key]
            
            # Calculate costs (per 1K tokens)
            input_cost = (input_tokens / 1000) * pricing["input"]
            output_cost = (output_tokens / 1000) * pricing["output"]
            total_cost = input_cost + output_cost
            
            # Create usage record
            usage_record = {
                "character_id": character_id,
                "timestamp": datetime.now(),
                "model": model,
                "usage_type": usage_type,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "input_cost_usd": input_cost,
                "output_cost_usd": output_cost,
                "total_cost_usd": total_cost,
                "metadata": metadata or {}
            }
            
            # Store in database
            await self.usage_collection.insert_one(usage_record)
            
            logger.debug(f"Tracked usage: {input_tokens} in, {output_tokens} out, ${total_cost:.6f}")
            
            return {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "cost_usd": total_cost
            }
            
        except Exception as e:
            logger.error(f"Error tracking usage: {e}")
            return {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "cost_usd": 0
            }
    
    async def get_usage_stats(
        self,
        character_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get usage statistics for character or all characters.
        
        Args:
            character_id: Optional character ID to filter
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            Usage statistics
        """
        try:
            # Build query
            query = {}
            if character_id:
                query["character_id"] = character_id
            
            if start_date or end_date:
                query["timestamp"] = {}
                if start_date:
                    query["timestamp"]["$gte"] = start_date
                if end_date:
                    query["timestamp"]["$lte"] = end_date
            
            # Aggregate statistics
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": {
                            "character_id": "$character_id",
                            "model": "$model",
                            "usage_type": "$usage_type"
                        },
                        "count": {"$sum": 1},
                        "total_input_tokens": {"$sum": "$input_tokens"},
                        "total_output_tokens": {"$sum": "$output_tokens"},
                        "total_tokens": {"$sum": "$total_tokens"},
                        "total_cost_usd": {"$sum": "$total_cost_usd"}
                    }
                },
                {
                    "$group": {
                        "_id": "$_id.character_id",
                        "models": {
                            "$push": {
                                "model": "$_id.model",
                                "usage_type": "$_id.usage_type",
                                "count": "$count",
                                "tokens": "$total_tokens",
                                "cost": "$total_cost_usd"
                            }
                        },
                        "total_requests": {"$sum": "$count"},
                        "total_tokens": {"$sum": "$total_tokens"},
                        "total_cost_usd": {"$sum": "$total_cost_usd"}
                    }
                }
            ]
            
            results = await self.usage_collection.aggregate(pipeline).to_list(None)
            
            # Calculate totals
            total_cost = sum(r.get("total_cost_usd", 0) for r in results)
            total_tokens = sum(r.get("total_tokens", 0) for r in results)
            total_requests = sum(r.get("total_requests", 0) for r in results)
            
            return {
                "summary": {
                    "total_cost_usd": total_cost,
                    "total_tokens": total_tokens,
                    "total_requests": total_requests,
                    "average_cost_per_request": total_cost / total_requests if total_requests > 0 else 0
                },
                "by_character": results,
                "period": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting usage stats: {e}")
            return {
                "summary": {
                    "total_cost_usd": 0,
                    "total_tokens": 0,
                    "total_requests": 0
                },
                "error": str(e)
            }
    
    async def get_daily_cost(self, character_id: Optional[str] = None) -> float:
        """Get today's total cost in USD."""
        from datetime import datetime, timedelta
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        stats = await self.get_usage_stats(
            character_id=character_id,
            start_date=today
        )
        return stats["summary"]["total_cost_usd"]