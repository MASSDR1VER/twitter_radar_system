#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration Management

This module provides centralized configuration management for the AI Character
Agent System. It handles environment variable loading, validation, and provides
typed access to configuration settings with proper defaults.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing required values."""
    pass


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    uri: str
    db_name: str
    connection_timeout: int = 10
    server_selection_timeout: int = 5


@dataclass
class LLMConfig:
    """LLM service configuration settings."""
    openai_api_key: Optional[str]
    anthropic_api_key: Optional[str]
    default_provider: str
    default_model: str
    default_embedding_model: str
    request_timeout: int = 30
    max_retries: int = 3


@dataclass
class AuthConfig:
    """Authentication configuration settings."""
    jwt_secret: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    password_min_length: int
    rate_limit_per_minute: int
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30


@dataclass
class CorsConfig:
    """CORS configuration settings."""
    origins: List[str]
    allow_credentials: bool
    allow_methods: List[str]
    allow_headers: List[str]


@dataclass
class ApplicationConfig:
    """Application configuration settings."""
    environment: str
    log_level: str
    host: str
    port: int
    version: str
    debug: bool = False
    worker_count: int = 1


class ConfigurationManager:
    """
    Centralized configuration manager for the AI Character Agent System.
    
    Provides typed access to configuration settings with validation
    and environment-specific defaults.
    """
    
    SUPPORTED_ENVIRONMENTS = ["development", "staging", "production", "test"]
    SUPPORTED_LLM_PROVIDERS = ["openai", "anthropic"]
    SUPPORTED_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    def __init__(self):
        """Initialize configuration manager with environment validation."""
        self._config = self._load_configuration()
        self._validate_configuration()
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load configuration from environment variables with defaults."""
        return {
            "database": self._load_database_config(),
            "llm": self._load_llm_config(),
            "auth": self._load_auth_config(),
            "cors": self._load_cors_config(),
            "app": self._load_app_config()
        }
    
    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration."""
        return DatabaseConfig(
            uri=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
            db_name=os.getenv("MONGODB_DB_NAME", "character_agent_system"),
            connection_timeout=int(os.getenv("MONGODB_CONNECTION_TIMEOUT", "10")),
            server_selection_timeout=int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT", "5"))
        )
    
    def _load_llm_config(self) -> LLMConfig:
        """Load LLM service configuration."""
        return LLMConfig(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            default_provider=os.getenv("DEFAULT_LLM_PROVIDER", "openai"),
            default_model=os.getenv("DEFAULT_LLM_MODEL", "gpt-4o"),
            default_embedding_model=os.getenv("DEFAULT_EMBEDDING_MODEL", "text-embedding-3-small"),
            request_timeout=int(os.getenv("LLM_REQUEST_TIMEOUT", "30")),
            max_retries=int(os.getenv("LLM_MAX_RETRIES", "3"))
        )
    
    def _load_auth_config(self) -> AuthConfig:
        """Load authentication configuration."""
        return AuthConfig(
            jwt_secret=os.getenv("JWT_SECRET", "development-secret-key-please-change-in-production"),
            jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            access_token_expire_minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
            refresh_token_expire_days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")),
            password_min_length=int(os.getenv("PASSWORD_MIN_LENGTH", "8")),
            rate_limit_per_minute=int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60")),
            max_login_attempts=int(os.getenv("MAX_LOGIN_ATTEMPTS", "5")),
            lockout_duration_minutes=int(os.getenv("LOCKOUT_DURATION_MINUTES", "30"))
        )
    
    def _load_cors_config(self) -> CorsConfig:
        """Load CORS configuration."""
        origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080")
        methods_str = os.getenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,OPTIONS,PATCH")
        headers_str = os.getenv("CORS_ALLOW_HEADERS", "*")
        
        return CorsConfig(
            origins=[origin.strip() for origin in origins_str.split(",")],
            allow_credentials=os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true",
            allow_methods=[method.strip() for method in methods_str.split(",")],
            allow_headers=[header.strip() for header in headers_str.split(",")]
        )
    
    def _load_app_config(self) -> ApplicationConfig:
        """Load application configuration."""
        environment = os.getenv("ENVIRONMENT", "development")
        
        return ApplicationConfig(
            environment=environment,
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            host=os.getenv("APP_HOST", "0.0.0.0"),
            port=int(os.getenv("APP_PORT", "8000")),
            version=os.getenv("APP_VERSION", "1.0.0"),
            debug=environment == "development",
            worker_count=int(os.getenv("WORKER_COUNT", "1"))
        )
    
    def _validate_configuration(self) -> None:
        """Validate configuration settings and raise errors for critical issues."""
        app_config = self._config["app"]
        llm_config = self._config["llm"]
        auth_config = self._config["auth"]
        
        if app_config.environment not in self.SUPPORTED_ENVIRONMENTS:
            raise ConfigurationError(
                f"Invalid environment '{app_config.environment}'. "
                f"Supported: {', '.join(self.SUPPORTED_ENVIRONMENTS)}"
            )
        
        if llm_config.default_provider not in self.SUPPORTED_LLM_PROVIDERS:
            raise ConfigurationError(
                f"Invalid LLM provider '{llm_config.default_provider}'. "
                f"Supported: {', '.join(self.SUPPORTED_LLM_PROVIDERS)}"
            )
        
        if app_config.log_level.upper() not in self.SUPPORTED_LOG_LEVELS:
            raise ConfigurationError(
                f"Invalid log level '{app_config.log_level}'. "
                f"Supported: {', '.join(self.SUPPORTED_LOG_LEVELS)}"
            )
        
        if app_config.environment != "test":
            self._validate_production_requirements(app_config, llm_config, auth_config)
    
    def _validate_production_requirements(self, app_config, llm_config, auth_config) -> None:
        """Validate production-specific requirements."""
        if llm_config.default_provider == "openai" and not llm_config.openai_api_key:
            logger.warning("OpenAI API key not set but OpenAI is the default provider")
        
        if llm_config.default_provider == "anthropic" and not llm_config.anthropic_api_key:
            logger.warning("Anthropic API key not set but Anthropic is the default provider")
        
        if app_config.environment == "production":
            if auth_config.jwt_secret == "development-secret-key-please-change-in-production":
                raise ConfigurationError(
                    "CRITICAL: Using default JWT secret in production! "
                    "Please set JWT_SECRET environment variable."
                )
            
            if app_config.debug:
                logger.warning("Debug mode is enabled in production environment")
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration."""
        return self._config["database"]
    
    def get_llm_config(self) -> LLMConfig:
        """Get LLM service configuration."""
        return self._config["llm"]
    
    def get_auth_config(self) -> AuthConfig:
        """Get authentication configuration."""
        return self._config["auth"]
    
    def get_cors_config(self) -> CorsConfig:
        """Get CORS configuration."""
        return self._config["cors"]
    
    def get_app_config(self) -> ApplicationConfig:
        """Get application configuration."""
        return self._config["app"]
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self._config["app"].environment == "development"
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self._config["app"].environment == "production"
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary for backward compatibility."""
        return {
            "database": {
                "uri": self._config["database"].uri,
                "db_name": self._config["database"].db_name,
                "connection_timeout": self._config["database"].connection_timeout,
                "server_selection_timeout": self._config["database"].server_selection_timeout
            },
            "mongodb": {
                "uri": self._config["database"].uri,
                "db_name": self._config["database"].db_name
            },
            "llm": {
                "openai_api_key": self._config["llm"].openai_api_key,
                "anthropic_api_key": self._config["llm"].anthropic_api_key,
                "default_provider": self._config["llm"].default_provider,
                "default_model": self._config["llm"].default_model,
                "default_embedding_model": self._config["llm"].default_embedding_model,
                "request_timeout": self._config["llm"].request_timeout,
                "max_retries": self._config["llm"].max_retries
            },
            "auth": {
                "jwt_secret": self._config["auth"].jwt_secret,
                "jwt_algorithm": self._config["auth"].jwt_algorithm,
                "access_token_expire_minutes": self._config["auth"].access_token_expire_minutes,
                "refresh_token_expire_days": self._config["auth"].refresh_token_expire_days,
                "password_min_length": self._config["auth"].password_min_length,
                "rate_limit_per_minute": self._config["auth"].rate_limit_per_minute,
                "max_login_attempts": self._config["auth"].max_login_attempts,
                "lockout_duration_minutes": self._config["auth"].lockout_duration_minutes
            },
            "cors": {
                "origins": self._config["cors"].origins,
                "allow_credentials": self._config["cors"].allow_credentials,
                "allow_methods": self._config["cors"].allow_methods,
                "allow_headers": self._config["cors"].allow_headers
            },
            "app": {
                "environment": self._config["app"].environment,
                "log_level": self._config["app"].log_level,
                "host": self._config["app"].host,
                "port": self._config["app"].port,
                "version": self._config["app"].version,
                "debug": self._config["app"].debug,
                "worker_count": self._config["app"].worker_count
            }
        }


_config_manager = None


def get_config() -> Dict[str, Any]:
    """
    Get configuration settings as dictionary (backward compatibility).
    
    Returns:
        Dictionary containing configuration settings
    """
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    
    return _config_manager.get_config_dict()


def get_config_manager() -> ConfigurationManager:
    """
    Get the configuration manager instance.
    
    Returns:
        ConfigurationManager instance
    """
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    
    return _config_manager