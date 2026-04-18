"""
SQLAlchemy models that MIRROR Django's existing table structure.

IMPORTANT:
  - Django owns all migrations. Do NOT add Alembic here.
  - Table/column names must exactly match Django's generated names.
  - Django's auth_user table and api_item table are the two we query.
  - authtoken_token is used to verify Django token auth.

Django table name conventions:
  - User model  → auth_user
  - Item model  → api_item   (app_label + model_name)
  - Token model → authtoken_token
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean,
    DateTime, ForeignKey
)
from database import Base


class AuthUser(Base):
    """Mirrors Django's built-in auth_user table."""
    __tablename__ = "auth_user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(254), nullable=False, default="")
    first_name = Column(String(150), nullable=False, default="")
    last_name = Column(String(150), nullable=False, default="")
    is_staff = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_superuser = Column(Boolean, nullable=False, default=False)
    date_joined = Column(DateTime(timezone=True), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    password = Column(String(128), nullable=False)  # hashed — never expose


class ApiItem(Base):
    """Mirrors the api_item table created by Django's api app."""
    __tablename__ = "api_item"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(10), nullable=False)          # 'Lost' | 'Found'
    item_name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    contact_info = Column(String(255), nullable=True)
    image = Column(String(100), nullable=True)          # File path stored by Django
    status = Column(String(20), nullable=False, default="Pending Review")
    reporter_id = Column(Integer, ForeignKey("auth_user.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)


class AuthToken(Base):
    """Mirrors DRF's authtoken_token table — used to verify Django tokens."""
    __tablename__ = "authtoken_token"

    key = Column(String(40), primary_key=True)
    created = Column(DateTime(timezone=True), nullable=False)
    user_id = Column(Integer, ForeignKey("auth_user.id"), nullable=False, unique=True)
