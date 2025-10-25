#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Authentication and Security Utilities

This module provides comprehensive authentication and security utilities
for the AI Character Agent System. It handles JWT token management,
password hashing, email validation, rate limiting, and security utilities.
"""

import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass, field

from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext
from email_validator import validate_email, EmailNotValidError

from utils.config import get_config
from utils.logger import get_logger

logger = get_logger(__name__)


class AuthenticationError(Exception):
    """Base authentication error."""
    def __init__(self, message: str, error_code: str = None) -> None:
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class TokenError(AuthenticationError):
    """JWT token-related errors."""
    pass


class PasswordError(AuthenticationError):
    """Password validation errors."""
    pass


class RateLimitError(AuthenticationError):
    """Rate limiting errors."""
    pass


@dataclass
class LoginAttempt:
    """Track login attempts for rate limiting."""
    count: int = 0
    last_attempt: datetime = field(default_factory=datetime.now)
    locked_until: Optional[datetime] = None


@dataclass
class TokenPayload:
    """Structured token payload data."""
    user_id: str
    username: str
    email: str
    role: str
    token_type: str
    issued_at: datetime
    expires_at: datetime
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TokenPayload':
        """Create TokenPayload from dictionary."""
        return cls(
            user_id=data.get("sub", ""),
            username=data.get("username", ""),
            email=data.get("email", ""),
            role=data.get("role", "user"),
            token_type=data.get("type", "access"),
            issued_at=datetime.fromtimestamp(data.get("iat", 0)),
            expires_at=datetime.fromtimestamp(data.get("exp", 0))
        )

class SecurityUtils:
    """
    Comprehensive security utilities for authentication and authorization.
    
    Provides methods for password hashing, token generation, email validation,
    input sanitization, and other security-related operations.
    """
    
    _pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    PASSWORD_PATTERNS = {
        "uppercase": r"[A-Z]",
        "lowercase": r"[a-z]",
        "digit": r"\d",
        "special": r"[!@#$%^&*(),.?\":{}|<>]"
    }
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        """
        Hash password using bcrypt with salt.
        
        Args:
            password: Plain text password
            
        Returns:
            Bcrypt hashed password
        """
        if not password:
            raise PasswordError("Password cannot be empty")
        
        return cls._pwd_context.hash(password)
    
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against bcrypt hash.
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Bcrypt hash to verify against
            
        Returns:
            True if password matches hash, False otherwise
        """
        if not plain_password or not hashed_password:
            return False
        
        try:
            return cls._pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    @classmethod
    def validate_password_strength(cls, password: str) -> Tuple[bool, List[str]]:
        """
        Validate password strength with detailed feedback.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        config = get_config()
        min_length = config["auth"]["password_min_length"]
        issues = []
        
        if not password:
            return False, ["Password is required"]
        
        if len(password) < min_length:
            issues.append(f"Password must be at least {min_length} characters long")
        
        for pattern_name, pattern in cls.PASSWORD_PATTERNS.items():
            if not re.search(pattern, password):
                issues.append(f"Password must contain at least one {pattern_name} character")
        
        if re.search(r"(.)\1{2,}", password):
            issues.append("Password should not contain repeated characters")
        
        if password.lower() in ["password", "123456", "qwerty", "admin"]:
            issues.append("Password is too common")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def validate_email_format(email: str) -> Tuple[bool, str]:
        """
        Validate email format using comprehensive validation.
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, normalized_email_or_error_message)
        """
        if not email:
            return False, "Email is required"
        
        try:
            valid_email = validate_email(email)
            return True, valid_email.email
        except EmailNotValidError as e:
            return False, str(e)
        except Exception as e:
            logger.error(f"Email validation error: {e}")
            return False, "Invalid email format"
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """
        Generate cryptographically secure random token.
        
        Args:
            length: Token length in bytes (will be base64 encoded)
            
        Returns:
            URL-safe base64 encoded token
        """
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """
        Generate numeric OTP for two-factor authentication.
        
        Args:
            length: Number of digits in OTP
            
        Returns:
            Numeric OTP string
        """
        return ''.join(secrets.choice('0123456789') for _ in range(length))
    
    @staticmethod
    def create_access_token(
        user_id: str,
        username: str = "",
        email: str = "",
        role: str = "user",
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create JWT access token with user information.
        
        Args:
            user_id: Unique user identifier
            username: Username
            email: User email
            role: User role/permission level
            additional_claims: Optional additional JWT claims
            
        Returns:
            JWT access token string
        """
        config = get_config()
        now = datetime.now(timezone.utc)
        
        claims = {
            "sub": user_id,
            "username": username,
            "email": email,
            "role": role,
            "iat": now,
            "exp": now + timedelta(minutes=config["auth"]["access_token_expire_minutes"]),
            "type": "access",
            "jti": secrets.token_hex(16)
        }
        
        if additional_claims:
            claims.update(additional_claims)
        
        return jwt.encode(claims, config["auth"]["jwt_secret"], algorithm=config["auth"]["jwt_algorithm"])
    
    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """
        Create JWT refresh token.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            JWT refresh token string
        """
        config = get_config()
        now = datetime.now(timezone.utc)
        
        claims = {
            "sub": user_id,
            "iat": now,
            "exp": now + timedelta(days=config["auth"]["refresh_token_expire_days"]),
            "type": "refresh",
            "jti": secrets.token_hex(16)
        }
        
        return jwt.encode(claims, config["auth"]["jwt_secret"], algorithm=config["auth"]["jwt_algorithm"])
    
    @staticmethod
    def verify_token(token: str) -> Optional[TokenPayload]:
        """
        Verify JWT token and return structured payload.
        
        Args:
            token: JWT token string
            
        Returns:
            TokenPayload object if valid, None if invalid
        """
        try:
            config = get_config()
            payload = jwt.decode(
                token,
                config["auth"]["jwt_secret"],
                algorithms=[config["auth"]["jwt_algorithm"]]
            )
            
            if payload.get("type") not in ["access", "refresh"]:
                raise TokenError("Invalid token type")
            
            return TokenPayload.from_dict(payload)
            
        except JWTError as e:
            logger.debug(f"Token verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in token verification: {e}")
            return None
    
    @staticmethod
    def verify_token_dict(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and return dictionary payload (backward compatibility).
        
        Args:
            token: JWT token string
            
        Returns:
            Dictionary payload if valid, None if invalid
        """
        try:
            config = get_config()
            return jwt.decode(
                token,
                config["auth"]["jwt_secret"],
                algorithms=[config["auth"]["jwt_algorithm"]]
            )
        except JWTError as e:
            logger.debug(f"Token verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in token verification: {e}")
            return None
    
    @staticmethod
    def extract_token_from_header(auth_header: str) -> Optional[str]:
        """
        Extract JWT token from Authorization header.
        
        Args:
            auth_header: Authorization header value
            
        Returns:
            JWT token if valid format, None otherwise
        """
        if not auth_header or not isinstance(auth_header, str):
            return None
        
        if not auth_header.startswith("Bearer "):
            return None
        
        try:
            return auth_header.split(" ", 1)[1]
        except IndexError:
            return None
    
    @staticmethod
    def sanitize_input(input_string: str, max_length: int = 255, allow_html: bool = False) -> str:
        """
        Sanitize user input to prevent injection attacks.
        
        Args:
            input_string: Input string to sanitize
            max_length: Maximum allowed length
            allow_html: Whether to allow HTML tags
            
        Returns:
            Sanitized string
        """
        if not input_string:
            return ""
        
        if not isinstance(input_string, str):
            input_string = str(input_string)
        
        sanitized = ''.join(
            char for char in input_string 
            if ord(char) >= 32 or char in ['\n', '\t']
        )
        
        if not allow_html:
            sanitized = re.sub(r'<[^>]+>', '', sanitized)
        
        sanitized = sanitized[:max_length]
        
        sanitized = sanitized.strip()
        
        return sanitized
    
    @staticmethod
    def is_token_expired(token_payload: Dict[str, Any]) -> bool:
        """
        Check if token is expired.
        
        Args:
            token_payload: Decoded JWT payload
            
        Returns:
            True if token is expired, False otherwise
        """
        exp_timestamp = token_payload.get("exp")
        if not exp_timestamp:
            return True
        
        return datetime.now(timezone.utc).timestamp() > exp_timestamp

class LoginAttemptTracker:
    """
    Track and manage user login attempts for security purposes.
    
    Implements account lockout after failed attempts and tracks
    login patterns for security monitoring.
    """
    
    def __init__(self):
        """Initialize login attempt tracker."""
        self._attempts: Dict[str, LoginAttempt] = {}
    
    def record_attempt(self, identifier: str, success: bool) -> None:
        """
        Record a login attempt for the given identifier.
        
        Args:
            identifier: User identifier (email, username, IP)
            success: Whether the login attempt was successful
        """
        config = get_config()
        now = datetime.now()
        
        if identifier not in self._attempts:
            self._attempts[identifier] = LoginAttempt()
        
        attempt = self._attempts[identifier]
        
        if success:
            attempt.count = 0
            attempt.locked_until = None
        else:
            attempt.count += 1
            
            if attempt.count >= config["auth"]["max_login_attempts"]:
                lockout_duration = timedelta(minutes=config["auth"]["lockout_duration_minutes"])
                attempt.locked_until = now + lockout_duration
                
                logger.warning(
                    f"Account locked due to {attempt.count} failed attempts",
                    extra={"identifier": identifier, "lockout_until": attempt.locked_until}
                )
        
        attempt.last_attempt = now
    
    def is_locked(self, identifier: str) -> bool:
        """
        Check if identifier is currently locked.
        
        Args:
            identifier: User identifier to check
            
        Returns:
            True if locked, False otherwise
        """
        if identifier not in self._attempts:
            return False
        
        attempt = self._attempts[identifier]
        
        if not attempt.locked_until:
            return False
        
        if datetime.now() > attempt.locked_until:
            attempt.locked_until = None
            attempt.count = 0
            return False
        
        return True
    
    def get_remaining_attempts(self, identifier: str) -> int:
        """
        Get remaining login attempts before lockout.
        
        Args:
            identifier: User identifier
            
        Returns:
            Number of remaining attempts
        """
        config = get_config()
        max_attempts = config["auth"]["max_login_attempts"]
        
        if identifier not in self._attempts:
            return max_attempts
        
        return max(0, max_attempts - self._attempts[identifier].count)
    
    def cleanup_old_attempts(self, max_age_hours: int = 24) -> None:
        """
        Clean up old login attempts to prevent memory bloat.
        
        Args:
            max_age_hours: Maximum age of attempts to keep
        """
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        expired_keys = [
            key for key, attempt in self._attempts.items()
            if attempt.last_attempt < cutoff and not attempt.locked_until
        ]
        
        for key in expired_keys:
            del self._attempts[key]


class RateLimiter:
    """
    Advanced rate limiter with sliding window and burst protection.
    
    Implements rate limiting using a sliding window approach with
    configurable limits and time windows.
    """
    
    def __init__(self):
        """Initialize rate limiter."""
        self._windows: Dict[str, List[datetime]] = {}
    
    def is_allowed(
        self,
        key: str,
        limit: int,
        window_seconds: int = 60,
        burst_limit: Optional[int] = None
    ) -> bool:
        """
        Check if request is allowed under rate limit.
        
        Args:
            key: Identifier for rate limiting (IP, user ID, etc.)
            limit: Maximum requests allowed in window
            window_seconds: Time window in seconds
            burst_limit: Optional burst limit for short periods
            
        Returns:
            True if request is allowed, False if rate limited
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=window_seconds)
        
        if key not in self._windows:
            self._windows[key] = []
        
        self._windows[key] = [
            req_time for req_time in self._windows[key]
            if req_time > cutoff
        ]
        
        current_count = len(self._windows[key])
        
        if current_count >= limit:
            logger.warning(f"Rate limit exceeded for key: {key}")
            return False
        
        if burst_limit:
            burst_cutoff = now - timedelta(seconds=10)
            burst_count = sum(1 for req_time in self._windows[key] if req_time > burst_cutoff)
            
            if burst_count >= burst_limit:
                logger.warning(f"Burst limit exceeded for key: {key}")
                return False
        
        self._windows[key].append(now)
        return True
    
    def get_current_usage(self, key: str, window_seconds: int = 60) -> int:
        """
        Get current usage count for a key.
        
        Args:
            key: Identifier to check
            window_seconds: Time window in seconds
            
        Returns:
            Current request count in window
        """
        if key not in self._windows:
            return 0
        
        cutoff = datetime.now() - timedelta(seconds=window_seconds)
        return sum(1 for req_time in self._windows[key] if req_time > cutoff)
    
    def reset_key(self, key: str) -> None:
        """
        Reset rate limit for a specific key.
        
        Args:
            key: Identifier to reset
        """
        if key in self._windows:
            del self._windows[key]
    
    def cleanup_old_windows(self, max_age_hours: int = 1) -> None:
        """
        Clean up old rate limit windows to prevent memory bloat.
        
        Args:
            max_age_hours: Maximum age of windows to keep
        """
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        for key in list(self._windows.keys()):
            self._windows[key] = [
                req_time for req_time in self._windows[key]
                if req_time > cutoff
            ]
            
            if not self._windows[key]:
                del self._windows[key]


login_tracker = LoginAttemptTracker()
rate_limiter = RateLimiter()

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify JWT token (backward compatibility).
    
    Args:
        token: JWT token string
        
    Returns:
        Dictionary payload if valid, None if invalid
    """
    return SecurityUtils.verify_token_dict(token)


def hash_password(password: str) -> str:
    """
    Hash password.
    
    Args:
        password: Plain text password
        
    Returns:
        Bcrypt hashed password
    """
    return SecurityUtils.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password.
    
    Args:
        plain_password: Plain text password
        hashed_password: Bcrypt hash
        
    Returns:
        True if password matches, False otherwise
    """
    return SecurityUtils.verify_password(plain_password, hashed_password)


def create_access_token(
    user_id: str,
    role: str = "user",
    additional_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Global function to create access token (backward compatibility).
    
    Args:
        user_id: User identifier
        role: User role
        additional_claims: Optional additional claims
        
    Returns:
        JWT access token string
    """
    return SecurityUtils.create_access_token(
        user_id=user_id,
        role=role,
        additional_claims=additional_claims
    )


def create_refresh_token(user_id: str) -> str:
    """
    Global function to create refresh token.
    
    Args:
        user_id: User identifier
        
    Returns:
        JWT refresh token string
    """
    return SecurityUtils.create_refresh_token(user_id)


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Global function to validate password strength (backward compatibility).
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, first_error_message)
    """
    is_valid, issues = SecurityUtils.validate_password_strength(password)
    return is_valid, issues[0] if issues else "Password is strong"

