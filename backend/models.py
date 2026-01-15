from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class UserRole(str, Enum):
    RESIDENT = "resident"
    BOARD_MEMBER = "board_member"
    ADMIN = "admin"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PaymentMethod(str, Enum):
    GCASH = "gcash"
    STRIPE = "stripe"
    PAYPAL = "paypal"


class NotificationType(str, Enum):
    PAYMENT_REMINDER = "payment_reminder"
    PAYMENT_SUCCESS = "payment_success"
    ANNOUNCEMENT = "announcement"
    EVENT = "event"
    DISCUSSION = "discussion"
    SYSTEM = "system"


# User Models
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole = UserRole.RESIDENT
    unit_number: Optional[str] = None
    phone: Optional[str] = None
    picture: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    unit_number: Optional[str] = None
    phone: Optional[str] = None
    picture: Optional[str] = None


class User(UserBase):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    created_at: datetime
    updated_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class SessionData(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    session_token: str


# Payment Models
class PaymentCreate(BaseModel):
    amount: float = Field(..., gt=0)
    payment_method: PaymentMethod
    description: Optional[str] = None
    metadata: Optional[dict] = {}


class Payment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    payment_id: str
    user_id: str
    amount: float
    payment_method: PaymentMethod
    status: PaymentStatus
    transaction_id: Optional[str] = None
    description: Optional[str] = None
    metadata: dict = {}
    created_at: datetime
    updated_at: datetime


# Receipt Models
class ReceiptCreate(BaseModel):
    payment_id: str
    file_url: str
    file_name: str
    file_size: int
    notes: Optional[str] = None


class Receipt(BaseModel):
    model_config = ConfigDict(extra="ignore")
    receipt_id: str
    payment_id: str
    user_id: str
    file_url: str
    file_name: str
    file_size: int
    notes: Optional[str] = None
    created_at: datetime


# Announcement Models
class AnnouncementCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=10)
    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")
    tags: List[str] = []


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None


class Announcement(BaseModel):
    model_config = ConfigDict(extra="ignore")
    announcement_id: str
    title: str
    content: str
    priority: str
    tags: List[str]
    author_id: str
    author_name: str
    created_at: datetime
    updated_at: datetime


class AIAnnouncementRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=500)


# Document Models
class DocumentCreate(BaseModel):
    title: str
    category: str
    file_url: str
    file_name: str
    file_size: int
    description: Optional[str] = None


class Document(BaseModel):
    model_config = ConfigDict(extra="ignore")
    document_id: str
    title: str
    category: str
    file_url: str
    file_name: str
    file_size: int
    description: Optional[str] = None
    uploaded_by: str
    created_at: datetime


# Event Models
class EventCreate(BaseModel):
    title: str
    description: str
    event_date: datetime
    location: Optional[str] = None
    max_attendees: Optional[int] = None


class Event(BaseModel):
    model_config = ConfigDict(extra="ignore")
    event_id: str
    title: str
    description: str
    event_date: datetime
    location: Optional[str] = None
    max_attendees: Optional[int] = None
    attendees: List[str] = []
    created_by: str
    created_at: datetime


# Discussion Models
class DiscussionCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=10)
    category: str = Field(default="general")


class DiscussionReply(BaseModel):
    content: str = Field(..., min_length=1)


class Reply(BaseModel):
    reply_id: str
    user_id: str
    user_name: str
    content: str
    created_at: datetime


class Discussion(BaseModel):
    model_config = ConfigDict(extra="ignore")
    discussion_id: str
    title: str
    content: str
    category: str
    author_id: str
    author_name: str
    replies: List[Reply] = []
    created_at: datetime
    updated_at: datetime


# Notification Models
class NotificationCreate(BaseModel):
    title: str
    message: str
    notification_type: NotificationType
    recipient_ids: Optional[List[str]] = None  # None means all users


class Notification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    notification_id: str
    title: str
    message: str
    notification_type: NotificationType
    recipient_id: str
    read: bool = False
    created_at: datetime
