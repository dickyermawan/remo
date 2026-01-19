# REMO - Dashboard Authentication Module

import asyncio
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable
from functools import wraps
from collections import defaultdict

from aiohttp import web
from itsdangerous import URLSafeSerializer, BadSignature
from loguru import logger

import config


# =============================================================================
# SESSION MANAGEMENT
# =============================================================================

_serializer = URLSafeSerializer(config.DASHBOARD_SECRET_KEY)


def create_session_token(user_data: Dict[str, Any]) -> str:
    """Create a signed session token."""
    session_data = {
        "user": user_data,
        "created_at": datetime.now().timestamp(),
    }
    return _serializer.dumps(session_data)


def verify_session_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode session token."""
    try:
        session_data = _serializer.loads(token)
        
        # Check expiration
        created_at = datetime.fromtimestamp(session_data["created_at"])
        if datetime.now() - created_at > timedelta(seconds=config.DASHBOARD_SESSION_TIMEOUT):
            return None
        
        return session_data["user"]
    except (BadSignature, KeyError, ValueError):
        return None


def set_session_cookie(response: web.Response, user_data: Dict[str, Any]) -> None:
    """Set session cookie on response."""
    token = create_session_token(user_data)
    response.set_cookie(
        "session",
        token,
        max_age=config.DASHBOARD_SESSION_TIMEOUT,
        httponly=True,  # Prevent JavaScript access
        secure=False,   # Set to True in production with HTTPS
        samesite="Strict",  # CSRF protection
    )


def get_session(request: web.Request) -> Optional[Dict[str, Any]]:
    """Get session data from request."""
    token = request.cookies.get("session")
    if not token:
        return None
    return verify_session_token(token)


def clear_session(response: web.Response) -> None:
    """Clear session cookie."""
    response.del_cookie("session")


# =============================================================================
# PASSWORD HASHING & VERIFICATION
# =============================================================================

def hash_password(password: str) -> bytes:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def verify_password(password: str, hashed: bytes) -> bool:
    """Verify password against hash using constant-time comparison."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    except Exception:
        return False


# For simplicity, we'll compare against plaintext password from .env
# In production, you'd store hashed passwords in database
def validate_credentials(username: str, password: str) -> bool:
    """Validate username and password against config."""
    # Constant-time comparison for username
    username_match = secrets.compare_digest(username, config.DASHBOARD_USERNAME)
    
    # Constant-time comparison for password
    password_match = secrets.compare_digest(password, config.DASHBOARD_PASSWORD)
    
    return username_match and password_match


# =============================================================================
# RATE LIMITING
# =============================================================================

class LoginRateLimiter:
    """Rate limiter for login attempts."""
    
    def __init__(self):
        self.attempts: Dict[str, list[float]] = defaultdict(list)
    
    def is_allowed(self, ip: str) -> bool:
        """Check if IP is allowed to attempt login."""
        now = datetime.now().timestamp()
        cutoff = now - config.DASHBOARD_LOGIN_WINDOW
        
        # Remove old attempts
        self.attempts[ip] = [t for t in self.attempts[ip] if t > cutoff]
        
        # Check if under limit
        if len(self.attempts[ip]) < config.DASHBOARD_MAX_LOGIN_ATTEMPTS:
            self.attempts[ip].append(now)
            return True
        
        return False
    
    def reset(self, ip: str) -> None:
        """Reset attempts for IP (on successful login)."""
        self.attempts[ip] = []


# Global rate limiter
login_rate_limiter = LoginRateLimiter()


# =============================================================================
# CSRF PROTECTION
# =============================================================================

def generate_csrf_token() -> str:
    """Generate CSRF token."""
    return secrets.token_urlsafe(32)


def verify_csrf_token(request: web.Request, token: str) -> bool:
    """Verify CSRF token from request."""
    session = get_session(request)
    if not session:
        return False
    
    expected = session.get("csrf_token")
    if not expected:
        return False
    
    return secrets.compare_digest(token, expected)


# =============================================================================
# DECORATORS
# =============================================================================

def login_required(handler: Callable) -> Callable:
    """Decorator to require login for route."""
    
    @wraps(handler)
    async def wrapper(request: web.Request) -> web.Response:
        session = get_session(request)
        
        if not session:
            # Redirect to login
            return web.HTTPFound("/")
        
        # Add session to request for handler to use
        request["session"] = session
        
        return await handler(request)
    
    return wrapper


def get_client_ip(request: web.Request) -> str:
    """Get client IP address from request."""
    # Check X-Forwarded-For header (from Cloudflare)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # Fallback to peer name
    peername = request.transport.get_extra_info("peername")
    if peername:
        return peername[0]
    
    return "unknown"
