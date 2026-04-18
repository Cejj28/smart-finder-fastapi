"""
Token authentication dependency — verifies Django's DRF Token against
the shared authtoken_token table. FastAPI accepts the same
'Authorization: Token <key>' header that the frontends already use.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import AuthToken, AuthUser

# We use APIKeyHeader to read the raw "Authorization" header.
# This prevents FastAPI from rejecting the Django "Token <key>" format.
security = APIKeyHeader(name="Authorization", auto_error=False)


async def get_current_user(
    auth_header: str = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> AuthUser:
    """
    Validates a Django DRF token from the Authorization header.
    Returns the associated user or raises 401.
    """
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header. Format should be: Token <key>"
        )

    # Allow formats: "Token <key>", "Bearer <key>", or just "<key>" from Swagger UI
    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() in ("token", "bearer"):
        token_key = parts[1]
    elif len(parts) == 1:
        token_key = parts[0]
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format. Expected: Token <key>"
        )

    # Look up the token in Django's authtoken_token table
    result = await db.execute(
        select(AuthToken).where(AuthToken.key == token_key)
    )
    token = result.scalar_one_or_none()

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    # Fetch the associated user
    user_result = await db.execute(
        select(AuthUser).where(AuthUser.id == token.user_id)
    )
    user = user_result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive.",
        )

    return user


async def get_current_admin(
    current_user: AuthUser = Depends(get_current_user),
) -> AuthUser:
    """Extends get_current_user — requires is_staff=True."""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required.",
        )
    return current_user
