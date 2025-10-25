#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Request middleware for logging and context management.
"""

import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from utils.logger import get_logger
from utils.auth import SecurityUtils

logger = get_logger(__name__)

class RequestMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging and context management."""
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]
        
        # Extract user info from token if present
        user_id = None
        try:
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                payload = SecurityUtils.verify_token(token)
                if payload:
                    user_id = payload.get("sub")
        except Exception:
            pass  # Ignore auth errors in middleware
        
        # Add context to request state
        request.state.request_id = request_id
        request.state.user_id = user_id
        
        # Start time
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log request with user context
        method = request.method
        url = request.url.path
        status_code = response.status_code
        
        # Create access logger
        access_logger = get_logger("access")
        
        # Log with context - show full user ID
        log_message = f"{method} {url} -> {status_code} ({process_time:.3f}s)"
        if user_id:
            log_message += f" [user:{user_id}, req:{request_id}]"
        else:
            log_message += f" [req:{request_id}]"
        
        access_logger.info(log_message)
        
        return response 