# REMO - Bot Middleware
# Authentication, rate limiting, and logging

from functools import wraps
from typing import Callable, Any
from collections import defaultdict
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger

import config


class RateLimiter:
    """Simple rate limiter for commands."""
    
    def __init__(self, max_calls: int, window_seconds: int):
        self.max_calls = max_calls
        self.window = timedelta(seconds=window_seconds)
        self.calls: dict[int, list[datetime]] = defaultdict(list)
    
    def is_allowed(self, user_id: int) -> bool:
        """Check if user is allowed to make a call."""
        now = datetime.now()
        cutoff = now - self.window
        
        # Remove old calls
        self.calls[user_id] = [
            call_time for call_time in self.calls[user_id]
            if call_time > cutoff
        ]
        
        # Check if under limit
        if len(self.calls[user_id]) < self.max_calls:
            self.calls[user_id].append(now)
            return True
        
        return False
    
    def reset(self, user_id: int):
        """Reset rate limit for a user."""
        self.calls[user_id] = []


# Global rate limiter instance
rate_limiter = RateLimiter(
    max_calls=config.RATE_LIMIT_COMMANDS,
    window_seconds=config.RATE_LIMIT_WINDOW
)


def authorized_only(func: Callable) -> Callable:
    """Decorator to restrict access to authorized user only."""
    
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs) -> Any:
        user = update.effective_user
        
        if user is None:
            logger.warning("Received update without user")
            return
        
        # Check if user is authorized
        if user.id != config.TELEGRAM_USER_ID:
            logger.warning(
                f"Unauthorized access attempt from user {user.id} (@{user.username})"
            )
            await update.message.reply_text(
                "⛔ Access denied. You are not authorized to use this bot."
            )
            return
        
        # Check rate limit
        if not rate_limiter.is_allowed(user.id):
            logger.warning(f"Rate limit exceeded for user {user.id}")
            await update.message.reply_text(
                "⚠️ Too many commands. Please wait a moment."
            )
            return
        
        # Log command
        command = update.message.text if update.message else "callback"
        logger.info(f"Command from {user.id} (@{user.username}): {command}")
        
        return await func(update, context, *args, **kwargs)
    
    return wrapper


def log_callback(func: Callable) -> Callable:
    """Decorator to log callback queries."""
    
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs) -> Any:
        query = update.callback_query
        user = update.effective_user
        
        if user is None or query is None:
            return
        
        # Check authorization
        if user.id != config.TELEGRAM_USER_ID:
            logger.warning(
                f"Unauthorized callback from user {user.id} (@{user.username})"
            )
            await query.answer("⛔ Access denied", show_alert=True)
            return
        
        logger.info(f"Callback from {user.id}: {query.data}")
        
        return await func(update, context, *args, **kwargs)
    
    return wrapper
