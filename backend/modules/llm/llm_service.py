#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Large Language Model Service

This module provides a unified interface for interacting with different LLM providers
(OpenAI, Anthropic) and handles text generation, embeddings, and error management.
"""

import json
import aiohttp
import requests
from typing import List, Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

from utils.config import get_config
from utils.logger import get_logger

logger = get_logger(__name__)


class LLMServiceError(Exception):
    """Base exception for LLM service errors."""
    def __init__(self, message: str, original_error: str = None, provider: str = None):
        self.message = message
        self.original_error = original_error
        self.provider = provider
        super().__init__(self.message)


class LLMServiceInitError(LLMServiceError):
    """LLM Service initialization error."""
    pass


class QuotaExceededError(LLMServiceError):
    """Error raised when API quota is exceeded."""
    pass


class AuthenticationError(LLMServiceError):
    """Error raised when API authentication fails."""
    pass


class LLMService:
    """
    Service for handling interactions with language models.
    
    This service provides a unified interface for multiple LLM providers,
    handling text generation, embeddings, and comprehensive error management.
    """
    
    OPENAI_BASE_URL = "https://api.openai.com/v1"
    ANTHROPIC_BASE_URL = "https://api.anthropic.com/v1"
    REQUEST_TIMEOUT = 10
    
    def __init__(self):
        """Initialize the LLM service with configuration validation."""
        self._load_configuration()
        self._validate_configuration()
        self._initialize_services()
        
        logger.info("LLM Service successfully initialized")
    
    def _load_configuration(self) -> None:
        """Load configuration from config module."""
        config = get_config()
        llm_config = config["llm"]
        
        self.openai_api_key = llm_config.get("openai_api_key")
        self.anthropic_api_key = llm_config.get("anthropic_api_key")
        self.default_embedding_model = llm_config.get("default_embedding_model", "text-embedding-3-small")
        self.default_provider = llm_config.get("default_provider", "openai")
        self.default_model = llm_config.get("default_model", "gpt-4")
    
    def _validate_configuration(self) -> None:
        """Validate basic configuration and API credentials."""
        if self.default_provider not in ["openai", "anthropic"]:
            raise LLMServiceInitError(f"Unsupported LLM provider: {self.default_provider}")
        
        if self.default_provider == "openai" and not self.openai_api_key:
            raise LLMServiceInitError("OpenAI API key not found in configuration")
        
        if self.default_provider == "anthropic" and not self.anthropic_api_key:
            raise LLMServiceInitError("Anthropic API key not found in configuration")
    
    def _initialize_services(self) -> None:
        """Initialize and validate API services."""
        try:
            if self.default_provider == "openai" and self.openai_api_key:
                self._validate_openai_service()
            
            if self.default_provider == "anthropic" and self.anthropic_api_key:
                self._validate_anthropic_service()
                
        except Exception as e:
            logger.error(f"Service initialization failed: {str(e)}")
            raise LLMServiceInitError(f"Service validation failed: {str(e)}")
    
    def _validate_openai_service(self) -> None:
        """Validate OpenAI API key and service availability."""
        if not self._is_valid_api_key_format(self.openai_api_key, "openai"):
            raise LLMServiceInitError("Invalid OpenAI API key format")
        
        if not self._test_api_connection("openai"):
            raise LLMServiceInitError("OpenAI API connection test failed")
    
    def _validate_anthropic_service(self) -> None:
        """Validate Anthropic API key and service availability."""
        if not self._is_valid_api_key_format(self.anthropic_api_key, "anthropic"):
            raise LLMServiceInitError("Invalid Anthropic API key format")
        
        if not self._test_api_connection("anthropic"):
            raise LLMServiceInitError("Anthropic API connection test failed")
    
    def _is_valid_api_key_format(self, api_key: str, provider: str) -> bool:
        """Check if API key has valid format for the specified provider."""
        if not api_key:
            return False
        
        if provider == "openai":
            return api_key.startswith("sk-") and len(api_key) > 20
        elif provider == "anthropic":
            return len(api_key) > 20
        
        return False
    
    def _test_api_connection(self, provider: str) -> bool:
        """Test API connection for the specified provider."""
        try:
            if provider == "openai":
                return self._test_openai_connection()
            elif provider == "anthropic":
                return self._test_anthropic_connection()
            
            return False
        except Exception as e:
            logger.warning(f"API connection test failed for {provider}: {e}")
            return False
    
    def _test_openai_connection(self) -> bool:
        """Test OpenAI API connection."""
        response = requests.get(
            f"{self.OPENAI_BASE_URL}/models",
            headers=self._get_openai_headers(),
            timeout=self.REQUEST_TIMEOUT
        )
        return response.status_code == 200
    
    def _test_anthropic_connection(self) -> bool:
        """Test Anthropic API connection with minimal request."""
        response = requests.post(
            f"{self.ANTHROPIC_BASE_URL}/messages",
            headers=self._get_anthropic_headers(),
            json={
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1,
                "messages": [{"role": "user", "content": "Hi"}]
            },
            timeout=self.REQUEST_TIMEOUT
        )
        return response.status_code == 200
    
    def _get_openai_headers(self) -> Dict[str, str]:
        """Get OpenAI API headers."""
        return {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
    
    def _get_anthropic_headers(self) -> Dict[str, str]:
        """Get Anthropic API headers."""
        return {
            "x-api-key": self.anthropic_api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
    
    async def _make_api_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        json_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Make an HTTP API request with error handling."""
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_text = await response.text()
                
                if response.status != 200:
                    self._handle_api_error(response.status, response_text)
                
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    raise LLMServiceError(f"Invalid JSON response: {response_text}")
    
    def _handle_api_error(self, status_code: int, response_text: str) -> None:
        """Handle API errors with appropriate exception types."""
        try:
            error_data = json.loads(response_text)
            error_info = error_data.get("error", {})
            error_type = error_info.get("type", "")
            error_message = error_info.get("message", "Unknown error")
            
            if "insufficient_quota" in error_type or "quota" in error_message.lower():
                raise QuotaExceededError(
                    "API quota exceeded. Please check your billing details.",
                    original_error=response_text
                )
            elif "invalid_api_key" in error_type or "authentication" in error_message.lower():
                raise AuthenticationError(
                    "API authentication failed. Please check your API key.",
                    original_error=response_text
                )
            else:
                raise LLMServiceError(f"API Error: {error_message}", original_error=response_text)
                
        except json.JSONDecodeError:
            raise LLMServiceError(f"HTTP {status_code}: {response_text}")
    
    @staticmethod
    def _should_retry_exception(exception) -> bool:
        """Determine if an exception should trigger a retry."""
        if isinstance(exception, (QuotaExceededError, AuthenticationError)):
            return False
        
        error_msg = str(exception).lower()
        non_retryable_errors = ["insufficient_quota", "invalid_api_key", "invalid_request_error"]
        
        return not any(err in error_msg for err in non_retryable_errors)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=lambda retry_state: (
            retry_state.outcome.failed and 
            LLMService._should_retry_exception(retry_state.outcome.exception())
        )
    )
    async def get_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """
        Generate embedding vector for the given text.
        
        Args:
            text: Text to generate embedding for
            model: Embedding model to use (defaults to configured model)
            
        Returns:
            List of float values representing the text embedding
            
        Raises:
            LLMServiceError: On API errors or configuration issues
        """
        if not self.openai_api_key:
            raise LLMServiceError("OpenAI API key not configured for embedding generation")
        
        model = model or self.default_embedding_model
        
        request_data = {
            "input": text,
            "model": model
        }
        
        response = await self._make_api_request(
            method="POST",
            url=f"{self.OPENAI_BASE_URL}/embeddings",
            headers=self._get_openai_headers(),
            json_data=request_data
        )
        
        try:
            return response["data"][0]["embedding"]
        except (KeyError, IndexError) as e:
            raise LLMServiceError(f"Invalid embedding response format: {e}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=lambda retry_state: (
            retry_state.outcome.failed and 
            LLMService._should_retry_exception(retry_state.outcome.exception())
        )
    )
    async def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate text using the specified or default LLM provider.
        
        Args:
            prompt: User prompt for text generation
            system_message: Optional system message for context
            model: Model to use (defaults to configured model)
            provider: Provider to use (defaults to configured provider)
            temperature: Sampling temperature (0.0 to 1.0)
            top_p: Nucleus sampling parameter (0.0 to 1.0)
            frequency_penalty: Frequency penalty (-2.0 to 2.0)
            presence_penalty: Presence penalty (-2.0 to 2.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text string
            
        Raises:
            LLMServiceError: On API errors or configuration issues
        """
        provider = provider or self.default_provider
        model = model or self.default_model
        
        if provider == "openai":
            return await self._generate_openai_text(
                prompt, system_message, model, temperature, top_p, frequency_penalty, presence_penalty, max_tokens
            )
        elif provider == "anthropic":
            return await self._generate_anthropic_text(
                prompt, system_message, model, temperature, top_p, frequency_penalty, presence_penalty, max_tokens
            )
        else:
            raise LLMServiceError(f"Unsupported provider: {provider}")
    
    async def _generate_openai_text(
        self,
        prompt: str,
        system_message: Optional[str],
        model: str,
        temperature: float,
        top_p: float,
        frequency_penalty: float,
        presence_penalty: float,
        max_tokens: int
    ) -> str:
        """Generate text using OpenAI API."""
        if not self.openai_api_key:
            raise LLMServiceError("OpenAI API key not configured")
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        request_data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "max_tokens": max_tokens
        }
        
        response = await self._make_api_request(
            method="POST",
            url=f"{self.OPENAI_BASE_URL}/chat/completions",
            headers=self._get_openai_headers(),
            json_data=request_data
        )
        
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise LLMServiceError(f"Invalid OpenAI response format: {e}")
    
    async def _generate_anthropic_text(
        self,
        prompt: str,
        system_message: Optional[str],
        model: str,
        temperature: float,
        top_p: float,
        frequency_penalty: float,
        presence_penalty: float,
        max_tokens: int
    ) -> str:
        """Generate text using Anthropic API."""
        if not self.anthropic_api_key:
            raise LLMServiceError("Anthropic API key not configured")
        
        request_data = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        # Note: Anthropic doesn't support frequency_penalty and presence_penalty
        
        if system_message:
            request_data["system"] = system_message
        
        response = await self._make_api_request(
            method="POST",
            url=f"{self.ANTHROPIC_BASE_URL}/messages",
            headers=self._get_anthropic_headers(),
            json_data=request_data
        )
        
        try:
            return response["content"][0]["text"]
        except (KeyError, IndexError) as e:
            raise LLMServiceError(f"Invalid Anthropic response format: {e}")
    
    def get_available_models(self, provider: Optional[str] = None) -> List[str]:
        """
        Get list of available models for the specified provider.
        
        Args:
            provider: Provider name (defaults to configured provider)
            
        Returns:
            List of available model names
        """
        provider = provider or self.default_provider
        
        if provider == "openai":
            return [
                "gpt-4",
                "gpt-4-turbo-preview",
                "gpt-3.5-turbo",
                "text-embedding-3-small",
                "text-embedding-3-large"
            ]
        elif provider == "anthropic":
            return [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ]
        else:
            return []
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get current service status and configuration.
        
        Returns:
            Dictionary containing service status information
        """
        return {
            "default_provider": self.default_provider,
            "default_model": self.default_model,
            "default_embedding_model": self.default_embedding_model,
            "openai_configured": bool(self.openai_api_key),
            "anthropic_configured": bool(self.anthropic_api_key),
            "available_providers": ["openai", "anthropic"]
        }
    
    async def health_check(self):
        """
        Health check for LLM service.
        This method checks if the LLM service is configured and available. 
        It does not check if the LLM service is actually working, just that it is configured.
        This is used to check if the LLM service is available in the dashboard.
        """
        try:
            if not self.openai_api_key and not self.anthropic_api_key:
                raise Exception("API key not configured")
            return {"status": "healthy"}
        except Exception as e:
            raise Exception(f"LLM service health check failed: {e}") 