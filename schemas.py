"""
Database Schemas for Healthy Living Support App

Each Pydantic model below represents a collection in MongoDB.
Collection name is the lowercase of the class name (e.g., Group -> "group").
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List


class User(BaseModel):
    """
    Users collection schema
    Collection name: "user"
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    avatar_url: Optional[str] = Field(None, description="Profile image URL")
    is_active: bool = Field(True, description="Whether user is active")


class Group(BaseModel):
    """
    Support groups for healthy living / weight loss
    Collection name: "group"
    """
    name: str = Field(..., description="Group name")
    topic: str = Field(..., description="Main focus, e.g., 'ירידה במשקל' or 'חיים בריאים'")
    description: Optional[str] = Field(None, description="Short description")
    members_count: int = Field(0, ge=0, description="Number of members (counter)")


class Message(BaseModel):
    """
    Messages inside a support group
    Collection name: "message"
    """
    group_id: str = Field(..., description="ID of the group this message belongs to")
    author_name: str = Field(..., description="Display name of the author")
    content: str = Field(..., description="Message content")


# You can extend with Goal/Progress later if needed
