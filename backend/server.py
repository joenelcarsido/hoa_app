from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Request, Response, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone
import uuid
from typing import List, Optional

from models import (
    User, UserCreate, UserLogin, UserUpdate, UserRole,
    Payment, PaymentCreate, PaymentStatus, PaymentMethod,
    Receipt, ReceiptCreate,
    Announcement, AnnouncementCreate, AnnouncementUpdate, AIAnnouncementRequest,
    Document, DocumentCreate,
    Event, EventCreate,
    Discussion, DiscussionCreate, DiscussionReply, Reply,
    Notification, NotificationCreate, NotificationType,
    SessionData
)
from auth import (
    verify_password, get_password_hash, create_access_token,
    get_current_user, require_role, exchange_session_id_for_token
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Barangay Connect API")

# Create API router
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== AUTH ROUTES ====================
@api_router.post("/auth/register")
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    hashed_password = get_password_hash(user_data.password)
    
    user_doc = {
        "user_id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "role": user_data.role,
        "unit_number": user_data.unit_number,
        "phone": user_data.phone,
        "picture": user_data.picture,
        "password_hash": hashed_password,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_doc)
    
    # Create access token
    access_token = create_access_token(data={"sub": user_id})
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "password_hash": 0})
    
    return {
        "user": user,
        "access_token": access_token,
        "token_type": "bearer"
    }


@api_router.post("/auth/login")
async def login(credentials: UserLogin, response: Response):
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    
    if not user or not verify_password(credentials.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user["user_id"]})
    
    # Create session in database
    session_token = f"session_{uuid.uuid4().hex}"
    session_doc = {
        "user_id": user["user_id"],
        "session_token": session_token,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.user_sessions.insert_one(session_doc)
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7 * 24 * 60 * 60,
        path="/"
    )
    
    user_data = {k: v for k, v in user.items() if k != "password_hash"}
    
    return {
        "user": user_data,
        "access_token": access_token,
        "token_type": "bearer"
    }


@api_router.post("/auth/google/callback")
async def google_auth_callback(request: Request, response: Response):
    """REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH"""
    body = await request.json()
    session_id = body.get("session_id")
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_id is required"
        )
    
    # Exchange session_id for user data
    user_data = await exchange_session_id_for_token(session_id)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session_id"
        )
    
    # Check if user exists
    user = await db.users.find_one({"email": user_data["email"]}, {"_id": 0})
    
    if not user:
        # Create new user
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        user_doc = {
            "user_id": user_id,
            "email": user_data["email"],
            "name": user_data["name"],
            "picture": user_data.get("picture"),
            "role": UserRole.RESIDENT,
            "unit_number": None,
            "phone": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(user_doc)
        user = user_doc
    else:
        # Update user info
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$set": {
                "name": user_data["name"],
                "picture": user_data.get("picture"),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
    
    # Create session
    session_token = user_data["session_token"]
    session_doc = {
        "user_id": user["user_id"],
        "session_token": session_token,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.user_sessions.insert_one(session_doc)
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7 * 24 * 60 * 60,
        path="/"
    )
    
    user_response = {k: v for k, v in user.items() if k != "password_hash"}
    
    return {"user": user_response}


@api_router.get("/auth/me")
async def get_me(request: Request):
    user = await get_current_user(request, db)
    user_data = {k: v for k, v in user.items() if k != "password_hash"}
    return {"user": user_data}


@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    token = request.cookies.get("session_token")
    
    if token:
        await db.user_sessions.delete_one({"session_token": token})
    
    response.delete_cookie(key="session_token", path="/")
    
    return {"message": "Logged out successfully"}


@api_router.put("/users/profile")
async def update_profile(update_data: UserUpdate, request: Request):
    user = await get_current_user(request, db)
    
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": update_dict}
    )
    
    updated_user = await db.users.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0, "password_hash": 0}
    )
    
    return {"user": updated_user}


# ==================== PAYMENT ROUTES ====================
@api_router.post("/payments/create")
async def create_payment(payment_data: PaymentCreate, request: Request):
    user = await get_current_user(request, db)
    
    from emergentintegrations.payments.stripe.checkout import (
        StripeCheckout, CheckoutSessionRequest
    )
    
    payment_id = f"pay_{uuid.uuid4().hex[:12]}"
    
    # Create payment record
    payment_doc = {
        "payment_id": payment_id,
        "user_id": user["user_id"],
        "amount": payment_data.amount,
        "payment_method": payment_data.payment_method,
        "status": PaymentStatus.PENDING,
        "transaction_id": None,
        "description": payment_data.description or "HOA Dues Payment",
        "metadata": payment_data.metadata,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.payments.insert_one(payment_doc)
    
    # For Stripe payments
    if payment_data.payment_method == PaymentMethod.STRIPE:
        api_key = os.getenv("STRIPE_API_KEY")
        host_url = str(request.base_url).rstrip("/")
        webhook_url = f"{host_url}/api/webhook/stripe"
        
        stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
        
        success_url = f"{host_url.replace('/api', '')}/payment-success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{host_url.replace('/api', '')}/payments"
        
        checkout_request = CheckoutSessionRequest(
            amount=float(payment_data.amount),
            currency="php",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "payment_id": payment_id,
                "user_id": user["user_id"]
            }
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Update payment with session info
        await db.payments.update_one(
            {"payment_id": payment_id},
            {"$set": {
                "transaction_id": session.session_id,
                "metadata.checkout_url": session.url
            }}
        )
        
        return {
            "payment_id": payment_id,
            "checkout_url": session.url,
            "session_id": session.session_id
        }
    
    return {"payment_id": payment_id, "status": "pending"}


@api_router.get("/payments")
async def get_payments(request: Request, limit: int = 50):
    user = await get_current_user(request, db)
    
    payments = await db.payments.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return {"payments": payments}


@api_router.get("/payments/{payment_id}")
async def get_payment(payment_id: str, request: Request):
    user = await get_current_user(request, db)
    
    payment = await db.payments.find_one(
        {"payment_id": payment_id, "user_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return {"payment": payment}


@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    from emergentintegrations.payments.stripe.checkout import StripeCheckout
    
    api_key = os.getenv("STRIPE_API_KEY")
    webhook_url = str(request.base_url).rstrip("/") + "/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
    
    body = await request.body()
    signature = request.headers.get("Stripe-Signature", "")
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Update payment status
        if webhook_response.event_type == "checkout.session.completed":
            await db.payments.update_one(
                {"transaction_id": webhook_response.session_id},
                {"$set": {
                    "status": PaymentStatus.SUCCESSFUL,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ==================== RECEIPT ROUTES ====================
@api_router.post("/receipts/upload")
async def upload_receipt(
    payment_id: str,
    file: UploadFile = File(...),
    notes: Optional[str] = None,
    request: Request = None
):
    user = await get_current_user(request, db)
    
    # Verify payment belongs to user
    payment = await db.payments.find_one(
        {"payment_id": payment_id, "user_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # In production, upload to cloud storage (S3, etc.)
    # For now, we'll store file info
    receipt_id = f"receipt_{uuid.uuid4().hex[:12]}"
    file_url = f"/uploads/receipts/{receipt_id}_{file.filename}"
    
    receipt_doc = {
        "receipt_id": receipt_id,
        "payment_id": payment_id,
        "user_id": user["user_id"],
        "file_url": file_url,
        "file_name": file.filename,
        "file_size": file.size if hasattr(file, 'size') else 0,
        "notes": notes,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.receipts.insert_one(receipt_doc)
    
    return {"receipt": {k: v for k, v in receipt_doc.items() if k != "_id"}}


@api_router.get("/receipts")
async def get_receipts(request: Request):
    user = await get_current_user(request, db)
    
    receipts = await db.receipts.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return {"receipts": receipts}


# ==================== ANNOUNCEMENT ROUTES ====================
@api_router.post("/announcements")
async def create_announcement(announcement_data: AnnouncementCreate, request: Request):
    user = await get_current_user(request, db)
    await require_role(user, [UserRole.ADMIN, UserRole.BOARD_MEMBER])
    
    announcement_id = f"ann_{uuid.uuid4().hex[:12]}"
    
    announcement_doc = {
        "announcement_id": announcement_id,
        "title": announcement_data.title,
        "content": announcement_data.content,
        "priority": announcement_data.priority,
        "tags": announcement_data.tags,
        "author_id": user["user_id"],
        "author_name": user["name"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.announcements.insert_one(announcement_doc)
    
    return {"announcement": {k: v for k, v in announcement_doc.items() if k != "_id"}}


@api_router.get("/announcements")
async def get_announcements(limit: int = 50):
    announcements = await db.announcements.find(
        {},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return {"announcements": announcements}


@api_router.post("/announcements/ai-draft")
async def ai_draft_announcement(ai_request: AIAnnouncementRequest, request: Request):
    user = await get_current_user(request, db)
    await require_role(user, [UserRole.ADMIN, UserRole.BOARD_MEMBER])
    
    from emergentintegrations.ai.llm_chat_engine import LlmChat, UserMessage
    
    api_key = os.getenv("EMERGENT_LLM_KEY")
    
    chat = LlmChat(
        api_key=api_key,
        session_id=f"announcement_{user['user_id']}",
        system_message="You are a professional HOA announcement writer. Create clear, friendly, and professional announcements for homeowners association members."
    ).with_model("openai", "gpt-5.2")
    
    message = UserMessage(text=f"Create a professional HOA announcement about: {ai_request.prompt}")
    
    response = await chat.send_message(message)
    
    return {"draft": response.text}


# ==================== DOCUMENT ROUTES ====================
@api_router.post("/documents")
async def upload_document(
    title: str,
    category: str,
    description: Optional[str] = None,
    file: UploadFile = File(...),
    request: Request = None
):
    user = await get_current_user(request, db)
    await require_role(user, [UserRole.ADMIN, UserRole.BOARD_MEMBER])
    
    document_id = f"doc_{uuid.uuid4().hex[:12]}"
    file_url = f"/uploads/documents/{document_id}_{file.filename}"
    
    document_doc = {
        "document_id": document_id,
        "title": title,
        "category": category,
        "file_url": file_url,
        "file_name": file.filename,
        "file_size": file.size if hasattr(file, 'size') else 0,
        "description": description,
        "uploaded_by": user["user_id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.documents.insert_one(document_doc)
    
    return {"document": {k: v for k, v in document_doc.items() if k != "_id"}}


@api_router.get("/documents")
async def get_documents(category: Optional[str] = None):
    query = {"category": category} if category else {}
    
    documents = await db.documents.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return {"documents": documents}


# ==================== EVENT ROUTES ====================
@api_router.post("/events")
async def create_event(event_data: EventCreate, request: Request):
    user = await get_current_user(request, db)
    await require_role(user, [UserRole.ADMIN, UserRole.BOARD_MEMBER])
    
    event_id = f"event_{uuid.uuid4().hex[:12]}"
    
    event_doc = {
        "event_id": event_id,
        "title": event_data.title,
        "description": event_data.description,
        "event_date": event_data.event_date.isoformat(),
        "location": event_data.location,
        "max_attendees": event_data.max_attendees,
        "attendees": [],
        "created_by": user["user_id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.events.insert_one(event_doc)
    
    return {"event": {k: v for k, v in event_doc.items() if k != "_id"}}


@api_router.get("/events")
async def get_events():
    events = await db.events.find(
        {},
        {"_id": 0}
    ).sort("event_date", 1).to_list(100)
    
    return {"events": events}


@api_router.post("/events/{event_id}/attend")
async def attend_event(event_id: str, request: Request):
    user = await get_current_user(request, db)
    
    event = await db.events.find_one({"event_id": event_id}, {"_id": 0})
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if user["user_id"] in event.get("attendees", []):
        raise HTTPException(status_code=400, detail="Already registered")
    
    if event.get("max_attendees") and len(event.get("attendees", [])) >= event["max_attendees"]:
        raise HTTPException(status_code=400, detail="Event is full")
    
    await db.events.update_one(
        {"event_id": event_id},
        {"$push": {"attendees": user["user_id"]}}
    )
    
    return {"message": "Successfully registered for event"}


# ==================== DISCUSSION ROUTES ====================
@api_router.post("/discussions")
async def create_discussion(discussion_data: DiscussionCreate, request: Request):
    user = await get_current_user(request, db)
    
    discussion_id = f"disc_{uuid.uuid4().hex[:12]}"
    
    discussion_doc = {
        "discussion_id": discussion_id,
        "title": discussion_data.title,
        "content": discussion_data.content,
        "category": discussion_data.category,
        "author_id": user["user_id"],
        "author_name": user["name"],
        "replies": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.discussions.insert_one(discussion_doc)
    
    return {"discussion": {k: v for k, v in discussion_doc.items() if k != "_id"}}


@api_router.get("/discussions")
async def get_discussions(category: Optional[str] = None):
    query = {"category": category} if category else {}
    
    discussions = await db.discussions.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return {"discussions": discussions}


@api_router.post("/discussions/{discussion_id}/reply")
async def reply_to_discussion(discussion_id: str, reply_data: DiscussionReply, request: Request):
    user = await get_current_user(request, db)
    
    reply = {
        "reply_id": f"reply_{uuid.uuid4().hex[:8]}",
        "user_id": user["user_id"],
        "user_name": user["name"],
        "content": reply_data.content,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = await db.discussions.update_one(
        {"discussion_id": discussion_id},
        {
            "$push": {"replies": reply},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Discussion not found")
    
    return {"reply": reply}


# ==================== NOTIFICATION ROUTES ====================
@api_router.get("/notifications")
async def get_notifications(request: Request):
    user = await get_current_user(request, db)
    
    notifications = await db.notifications.find(
        {"recipient_id": user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(50)
    
    return {"notifications": notifications}


@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, request: Request):
    user = await get_current_user(request, db)
    
    await db.notifications.update_one(
        {"notification_id": notification_id, "recipient_id": user["user_id"]},
        {"$set": {"read": True}}
    )
    
    return {"message": "Notification marked as read"}


# ==================== ADMIN ROUTES ====================
@api_router.get("/admin/users")
async def get_all_users(request: Request):
    user = await get_current_user(request, db)
    await require_role(user, [UserRole.ADMIN])
    
    users = await db.users.find(
        {},
        {"_id": 0, "password_hash": 0}
    ).to_list(1000)
    
    return {"users": users}


@api_router.get("/admin/analytics")
async def get_analytics(request: Request):
    user = await get_current_user(request, db)
    await require_role(user, [UserRole.ADMIN])
    
    total_users = await db.users.count_documents({})
    total_payments = await db.payments.count_documents({})
    successful_payments = await db.payments.count_documents({"status": PaymentStatus.SUCCESSFUL})
    
    pipeline = [
        {"$match": {"status": PaymentStatus.SUCCESSFUL}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]
    
    result = await db.payments.aggregate(pipeline).to_list(1)
    total_revenue = result[0]["total"] if result else 0
    
    return {
        "total_users": total_users,
        "total_payments": total_payments,
        "successful_payments": successful_payments,
        "total_revenue": total_revenue
    }


# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
