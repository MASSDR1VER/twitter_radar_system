#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Context-Aware Logging Utilities

This module provides enhanced logging capabilities for the AI Character Agent
System with automatic context injection, structured logging, and performance
monitoring features.
"""

import logging
import time
from contextvars import ContextVar
from typing import Optional, Dict, Any, Callable
from functools import wraps
from dataclasses import dataclass


request_id_context: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_context: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
character_id_context: ContextVar[Optional[str]] = ContextVar('character_id', default=None)
platform_context: ContextVar[Optional[str]] = ContextVar('platform', default=None)


@dataclass
class LogContext:
    """Structured logging context data."""
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    character_id: Optional[str] = None
    platform: Optional[str] = None
    operation: Optional[str] = None
    duration_ms: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


class ContextLogger:
    """
    Enhanced logger with automatic context injection and structured logging.
    
    Provides context-aware logging with automatic injection of request IDs,
    user IDs, character IDs, and other contextual information. Supports
    performance monitoring and error tracking.
    """
    
    def __init__(self, logger: logging.Logger) -> None:
        """Initialize context logger with base logger."""
        self.logger = logger
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Setup logger with appropriate level and formatting."""
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
    
    def _build_context(self, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Build comprehensive logging context.
        
        Args:
            extra: Additional context to include
            
        Returns:
            Dictionary containing all available context
        """
        context = extra.copy() if extra else {}
        
        context_vars = {
            'request_id': request_id_context,
            'user_id': user_id_context,
            'character_id': character_id_context,
            'platform': platform_context
        }
        
        for key, context_var in context_vars.items():
            try:
                value = context_var.get()
                if value:
                    context[key] = value
            except LookupError:
                continue
        
        return context
    
    def _log(self, level: int, message: str, **kwargs) -> None:
        """
        Internal logging method with context injection.
        
        Args:
            level: Logging level
            message: Log message
            **kwargs: Additional context and parameters
        """
        character_id = kwargs.pop('character_id', None)
        platform = kwargs.pop('platform', None)
        operation = kwargs.pop('operation', None)
        duration_ms = kwargs.pop('duration_ms', None)
        exc_info = kwargs.pop('exc_info', None)
        
        extra = self._build_context(kwargs)
        
        if character_id:
            extra['character_id'] = character_id
        if platform:
            extra['platform'] = platform
        if operation:
            extra['operation'] = operation
        if duration_ms is not None:
            extra['duration_ms'] = duration_ms
        
        self.logger.log(level, message, extra=extra, exc_info=exc_info)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with context."""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message with context."""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with context."""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message with context."""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message with context."""
        self._log(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        """
        Log exception with full traceback and context.
        
        Args:
            message: Exception message
            **kwargs: Additional context
        """
        kwargs['exc_info'] = True
        self._log(logging.ERROR, message, **kwargs)
    
    def log_operation_start(self, operation: str, **kwargs) -> float:
        """
        Log the start of an operation and return start time.
        
        Args:
            operation: Name of the operation
            **kwargs: Additional context
            
        Returns:
            Start time for duration calculation
        """
        start_time = time.time()
        self.debug(f"Starting operation: {operation}", operation=operation, **kwargs)
        return start_time
    
    def log_operation_end(
        self,
        operation: str,
        start_time: float,
        success: bool = True,
        **kwargs
    ) -> None:
        """
        Log the end of an operation with duration.
        
        Args:
            operation: Name of the operation
            start_time: Start time from log_operation_start
            success: Whether operation was successful
            **kwargs: Additional context
        """
        duration_ms = (time.time() - start_time) * 1000
        
        level = logging.INFO if success else logging.ERROR
        status = "completed" if success else "failed"
        
        self._log(
            level,
            f"Operation {operation} {status} in {duration_ms:.2f}ms",
            operation=operation,
            duration_ms=duration_ms,
            success=success,
            **kwargs
        )
    
    def log_performance(self, operation: str, duration_ms: float, **kwargs) -> None:
        """
        Log performance metrics for an operation.
        
        Args:
            operation: Name of the operation
            duration_ms: Duration in milliseconds
            **kwargs: Additional metrics
        """
        level = logging.WARNING if duration_ms > 1000 else logging.INFO
        
        self._log(
            level,
            f"Performance: {operation} took {duration_ms:.2f}ms",
            operation=operation,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def log_api_call(
        self,
        method: str,
        url: str,
        status_code: int,
        duration_ms: float,
        **kwargs
    ) -> None:
        """
        Log external API calls with comprehensive details.
        
        Args:
            method: HTTP method
            url: Request URL
            status_code: Response status code
            duration_ms: Request duration
            **kwargs: Additional context
        """
        level = logging.ERROR if status_code >= 400 else logging.INFO
        
        self._log(
            level,
            f"API {method} {url} -> {status_code} ({duration_ms:.2f}ms)",
            operation="api_call",
            http_method=method,
            url=url,
            status_code=status_code,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def log_database_operation(
        self,
        operation: str,
        collection: str,
        duration_ms: float,
        document_count: Optional[int] = None,
        **kwargs
    ) -> None:
        """
        Log database operations with performance metrics.
        
        Args:
            operation: Database operation type
            collection: Collection name
            duration_ms: Operation duration
            document_count: Number of documents affected
            **kwargs: Additional context
        """
        message_parts = [f"DB {operation} on {collection}", f"({duration_ms:.2f}ms)"]
        if document_count is not None:
            message_parts.insert(1, f"[{document_count} docs]")
        
        level = logging.WARNING if duration_ms > 500 else logging.DEBUG
        
        self._log(
            level,
            " ".join(message_parts),
            operation="database",
            db_operation=operation,
            collection=collection,
            duration_ms=duration_ms,
            document_count=document_count,
            **kwargs
        )


def get_logger(name: str) -> ContextLogger:
    """
    Get a context-aware logger for the specified module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        ContextLogger instance
    """
    return ContextLogger(logging.getLogger(name))


def set_request_context(
    request_id: str,
    user_id: Optional[str] = None,
    character_id: Optional[str] = None,
    platform: Optional[str] = None
) -> None:
    """
    Set request context for automatic logging injection.
    
    Args:
        request_id: Unique request identifier
        user_id: User identifier
        character_id: Character identifier
        platform: Platform name
    """
    request_id_context.set(request_id)
    if user_id:
        user_id_context.set(user_id)
    if character_id:
        character_id_context.set(character_id)
    if platform:
        platform_context.set(platform)


def clear_request_context() -> None:
    """Clear all request context variables."""
    for context_var in [request_id_context, user_id_context, character_id_context, platform_context]:
        try:
            context_var.set(None)
        except LookupError:
            pass


def log_execution_time(operation: str = None) -> Callable:
    """
    Decorator to automatically log function execution time.
    
    Args:
        operation: Custom operation name (defaults to function name)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = get_logger(func.__module__)
            op_name = operation or f"{func.__name__}"
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.log_performance(op_name, duration_ms)
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"Operation {op_name} failed after {duration_ms:.2f}ms: {str(e)}",
                    operation=op_name,
                    duration_ms=duration_ms,
                    exc_info=True
                )
                raise
        return wrapper
    return decorator


def log_api_errors(func: Callable) -> Callable:
    """
    Decorator to automatically log API errors with context.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        logger = get_logger(func.__module__)
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(
                f"API error in {func.__name__}: {str(e)}",
                operation="api_error",
                function=func.__name__
            )
            raise
    return wrapper