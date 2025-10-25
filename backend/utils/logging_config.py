#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Advanced Logging Configuration

This module provides comprehensive logging configuration for the AI Character
Agent System with support for structured logging, colored output, log rotation,
and environment-specific formatting.
"""

import logging
import logging.handlers
import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, Any
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """
    Enhanced colored console formatter for development environments.
    
    Provides color-coded log levels and context information with
    improved readability and structured context display.
    """
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green  
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m',       # Reset
        'BOLD': '\033[1m',        # Bold
        'DIM': '\033[90m'         # Dim gray
    }
    
    def __init__(self, show_context: bool = True, show_module: bool = True) -> None:
        """
        Initialize colored formatter.
        
        Args:
            show_context: Whether to show context information
            show_module: Whether to show module names
        """
        super().__init__()
        self.show_context = show_context
        self.show_module = show_module
    
    def format(self, record) -> str:
        """
        Format log record with colors and context.
        
        Args:
            record: Log record to format
            
        Returns:
            Formatted log message string
        """
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        dim = self.COLORS['DIM']
        
        record.asctime = self.formatTime(record, '%H:%M:%S')
        
        parts = [
            f"{color}{record.asctime}{reset}",
            f"{color}{record.levelname:<8}{reset}"
        ]
        
        if self.show_module:
            module_name = record.name.split('.')[-1] if '.' in record.name else record.name
            parts.append(f"{dim}{module_name:<15}{reset}")
        
        parts.append(record.getMessage())
        
        base_msg = " - ".join(parts)
        
        if self.show_context:
            context_parts = self._extract_context(record)
            if context_parts:
                context_str = f"{dim}[{', '.join(context_parts)}]{reset}"
                base_msg += f" {context_str}"
        
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            base_msg += f"\n{exc_text}"
        
        return base_msg
    
    def _extract_context(self, record) -> list:
        """
        Extract context information from log record.
        
        Args:
            record: Log record
            
        Returns:
            List of context strings
        """
        context_parts = []
        
        context_fields = {
            'user_id': 'user',
            'request_id': 'req',
            'character_id': 'char',
            'platform': 'platform',
            'operation': 'op',
            'duration_ms': 'duration'
        }
        
        for field, label in context_fields.items():
            if hasattr(record, field) and getattr(record, field):
                value = getattr(record, field)
                
                if field == 'character_id' and len(str(value)) > 8:
                    value = str(value)[:8]
                elif field == 'duration_ms':
                    value = f"{value:.1f}ms"
                
                context_parts.append(f"{label}:{value}")
        
        return context_parts

class JSONFormatter(logging.Formatter):
    """
    Advanced JSON formatter for production environments.
    
    Provides structured logging with comprehensive metadata,
    performance metrics, and standardized field names.
    """
    
    def __init__(self, include_location: bool = True, include_extra: bool = True) -> None:
        """
        Initialize JSON formatter.
        
        Args:
            include_location: Whether to include file location info
            include_extra: Whether to include extra fields
        """
        super().__init__()
        self.include_location = include_location
        self.include_extra = include_extra
    
    def format(self, record) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON string
        """
        log_entry = {
            "@timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "process_id": os.getpid(),
            "thread_id": record.thread,
            "thread_name": record.threadName
        }

        if self.include_location:
            log_entry.update({
                "module": record.module,
                "function": record.funcName,
                "line_number": record.lineno,
                "file_path": record.pathname
            })
        
        context_fields = [
            'character_id', 'user_id', 'platform', 'request_id',
            'operation', 'duration_ms', 'status_code', 'http_method',
            'url', 'db_operation', 'collection', 'document_count'
        ]
        
        for field in context_fields:
            if hasattr(record, field) and getattr(record, field) is not None:
                log_entry[field] = getattr(record, field)
        
        if self.include_extra and hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if (key not in log_entry and 
                    not key.startswith('_') and
                    key not in ['name', 'msg', 'args', 'levelname', 'levelno',
                                'pathname', 'filename', 'module', 'lineno',
                                'funcName', 'created', 'msecs', 'relativeCreated',
                                'thread', 'threadName', 'processName', 'process',
                                'message', 'exc_info', 'exc_text', 'stack_info']):
                    try:
                        json.dumps(value)
                        log_entry[key] = value
                    except (TypeError, ValueError):
                        log_entry[key] = str(value)
        
        if record.exc_info:
            log_entry["exception"] = {
                "class": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }
        
        if hasattr(record, 'stack_info') and record.stack_info:
            log_entry["stack_trace"] = record.stack_info
        
        return json.dumps(log_entry, default=str, separators=(',', ':'))

class LoggingConfiguration:
    """
    Comprehensive logging configuration manager.
    
    Handles setup of console handlers, file handlers, formatters,
    and logger levels based on environment and configuration.
    """
    
    DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize logging configuration."""
        self.config = config
        self.app_config = config.get("app", {})
        self.environment = self.app_config.get("environment", "development")
        self.log_level = self.app_config.get("log_level", "INFO").upper()
        
    def setup(self) -> logging.Logger:
        """
        Setup complete logging configuration.
        
        Returns:
            Configured logger instance
        """
        self._ensure_log_directory()
        
        self._clear_existing_handlers()
        
        root_logger = self._setup_root_logger()
        
        self._add_console_handler(root_logger)
        
        self._add_file_handlers(root_logger)
        
        self._configure_logger_levels()
        
        self._log_configuration_summary()
        
        return logging.getLogger(__name__)
    
    def _ensure_log_directory(self) -> None:
        """Create logs directory if it doesn't exist."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different log types
        for subdir in ["app", "error", "performance", "audit"]:
            (log_dir / subdir).mkdir(exist_ok=True)
    
    def _clear_existing_handlers(self) -> None:
        """Remove all existing handlers from root logger."""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    
    def _setup_root_logger(self) -> logging.Logger:
        """Setup and configure root logger."""
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.log_level, logging.INFO))
        return root_logger
    
    def _add_console_handler(self, root_logger: logging.Logger) -> None:
        """Add console handler with appropriate formatter."""
        console_handler = logging.StreamHandler(sys.stdout)
        
        if self.environment == "production":
            formatter = JSONFormatter(include_location=False)
        else:
            formatter = ColoredFormatter(
                show_context=True,
                show_module=True
            )
        
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, self.log_level, logging.INFO))
        root_logger.addHandler(console_handler)
    
    def _add_file_handlers(self, root_logger: logging.Logger) -> None:
        """Add file handlers with rotation."""
        # Application log (all logs)
        app_handler = logging.handlers.RotatingFileHandler(
            "logs/app/application.log",
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=10
        )
        app_handler.setFormatter(JSONFormatter())
        app_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(app_handler)
        
        # Error log (errors and critical only)
        error_handler = logging.handlers.RotatingFileHandler(
            "logs/error/errors.log",
            maxBytes=20 * 1024 * 1024,  # 20MB
            backupCount=5
        )
        error_handler.setFormatter(JSONFormatter(include_extra=True))
        error_handler.setLevel(logging.ERROR)
        root_logger.addHandler(error_handler)
        
        # Performance log (performance metrics)
        performance_handler = logging.handlers.RotatingFileHandler(
            "logs/performance/performance.log",
            maxBytes=30 * 1024 * 1024,  # 30MB
            backupCount=7
        )
        performance_handler.setFormatter(JSONFormatter())
        performance_handler.setLevel(logging.INFO)
        
        # Add filter for performance logs
        performance_handler.addFilter(
            lambda record: hasattr(record, 'duration_ms') or 
                          hasattr(record, 'operation')
        )
        root_logger.addHandler(performance_handler)
    
    def _configure_logger_levels(self) -> None:
        """Configure levels for specific loggers."""
        logger_configs = {
            "uvicorn.access": logging.WARNING,
            "uvicorn.error": logging.INFO,
            "fastapi": logging.INFO,
            "aiohttp": logging.WARNING,
            
            # Database loggers
            "database.mongodb": logging.INFO,
            "motor": logging.WARNING,
            "pymongo": logging.WARNING,
            
            # Application modules
            "modules.memory": logging.INFO,
            "modules.character": logging.INFO,
            "modules.behavior": logging.INFO,
            "modules.llm": logging.INFO,
            "modules.research": logging.INFO,
            "modules.reflection": logging.INFO,
            
            # API layers
            "api.auth": logging.INFO,
            "api.character": logging.INFO,
            "api.behavior": logging.INFO,
            
            # External services
            "platforms.twitter": logging.INFO,
            "utils.auth": logging.INFO,
            "utils.logger": logging.WARNING
        }
        
        config_loggers = self.config.get("logging", {})
        
        for logger_name, default_level in logger_configs.items():
            config_level = config_loggers.get(logger_name.split('.')[-1])
            if config_level:
                level = getattr(logging, config_level.upper(), default_level)
            else:
                level = default_level
            
            logging.getLogger(logger_name).setLevel(level)
    
    def _log_configuration_summary(self) -> None:
        """Log a summary of the logging configuration."""
        logger = logging.getLogger(__name__)
        logger.info(
            "Logging configuration initialized",
            extra={
                "environment": self.environment,
                "log_level": self.log_level,
                "handlers_count": len(logging.getLogger().handlers)
            }
        )


def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """
    Setup comprehensive logging configuration.
    
    Args:
        config: Application configuration dictionary
        
    Returns:
        Configured logger instance
    """
    logging_config = LoggingConfiguration(config)
    return logging_config.setup()

def setup_file_handlers(root_logger: logging.Logger) -> None:
    """
    Legacy function for setting up file handlers (deprecated).
    
    Args:
        root_logger: Root logger instance
        
    Note:
        This function is deprecated. Use LoggingConfiguration.setup() instead.
    """
    import warnings
    warnings.warn(
        "setup_file_handlers is deprecated. Use LoggingConfiguration.setup() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    app_handler = logging.handlers.RotatingFileHandler(
        "logs/app.log",
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=5
    )
    app_handler.setFormatter(JSONFormatter())
    app_handler.setLevel(logging.INFO)
    root_logger.addHandler(app_handler)
    
    error_handler = logging.handlers.RotatingFileHandler(
        "logs/error.log", 
        maxBytes=20 * 1024 * 1024,  # 20MB
        backupCount=3
    )
    error_handler.setFormatter(JSONFormatter())
    error_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_handler)

def setup_logger_levels(config: Dict[str, Any]) -> None:
    """
    Legacy function for configuring logger levels (deprecated).
    
    Args:
        config: Configuration dictionary
        
    Note:
        This function is deprecated. Use LoggingConfiguration.setup() instead.
    """
    import warnings
    warnings.warn(
        "setup_logger_levels is deprecated. Use LoggingConfiguration.setup() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    log_config = config.get("logging", {})
    
    loggers = {
        "uvicorn.access": logging.WARNING,
        "database.mongodb": getattr(logging, log_config.get("database", "INFO").upper()),
        "modules.memory": getattr(logging, log_config.get("memory", "WARNING").upper()),
        "modules.character": getattr(logging, log_config.get("character", "INFO").upper()),
        "modules.behavior": getattr(logging, log_config.get("behavior", "INFO").upper()),
        "modules.llm": getattr(logging, log_config.get("llm", "WARNING").upper()),
    }
    
    for logger_name, level in loggers.items():
        logging.getLogger(logger_name).setLevel(level)


def get_performance_logger() -> logging.Logger:
    """Get logger specifically for performance metrics."""
    logger = logging.getLogger("performance")
    return logger


def get_audit_logger() -> logging.Logger:
    """Get logger specifically for audit events."""
    logger = logging.getLogger("audit")
    return logger


def get_security_logger() -> logging.Logger:
    """Get logger specifically for security events."""
    logger = logging.getLogger("security")
    return logger 