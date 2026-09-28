import json
import time
from typing import List, Dict, Optional

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, Query, Response
from sqlalchemy.orm import Session, joinedload
import bleach

from app import schemas
from app.auth import get_current_user_ws, get_current_user
from app.database import get_db, SessionLocal
from app.models import ChatMessage, Notification, User, UserRole

router = APIRouter(prefix="/chat", tags=["الشات"])

class ConnectionManager:
    def __init__(self):
        # user_id -> List of WebSockets
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # user_id -> list of float timestamps for rate-limiting
        self.user_rate_limits: Dict[int, List[float]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        # Max 5 active sockets per user to prevent socket exhaustion DoS
        if len(self.active_connections[user_id]) >= 5:
            oldest_ws = self.active_connections[user_id].pop(0)
            try:
                await oldest_ws.close(code=1000)
            except Exception:
                pass

        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        if user_id in self.user_rate_limits and user_id not in self.active_connections:
            del self.user_rate_limits[user_id]

    def check_rate_limit(self, user_id: int) -> bool:
        """Returns True if within rate limit, False if exceeded (max 5 msgs / 5 sec)."""
        now = time.time()
        timestamps = self.user_rate_limits.get(user_id, [])
        timestamps = [t for t in timestamps if now - t < 5.0]
        if len(timestamps) >= 5:
            self.user_rate_limits[user_id] = timestamps
            return False
        timestamps.append(now)
        self.user_rate_limits[user_id] = timestamps
        return True

    async def broadcast(self, message_data: dict):
        """إرسال رسالة لجميع المتصلين"""
        dead_connections = []
        for user_id, connections in list(self.active_connections.items()):
            for connection in list(connections):
                try:
                    await connection.send_json(message_data)
                except Exception:
                    dead_connections.append((user_id, connection))
        
        for uid, conn in dead_connections:
            self.disconnect(conn, uid)

    async def send_personal_message(self, user_id: int, message_data: dict):
        """إرسال رسالة لمستخدم محدد فقط"""
        if user_id in self.active_connections:
            for connection in list(self.active_connections[user_id]):
                try:
                    await connection.send_json(message_data)
                except Exception:
                    pass

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    user = await get_current_user_ws(token)
    if not user:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, user.id)
    try:
        while True:
            data = await websocket.receive_text()
            if not data or not data.strip():
                continue

            # 1. Payload size protection (DoS mitigation: max 4KB frame)
            if len(data) > 4096:
                await websocket.send_json({"action": "error", "message": "حجم الرسالة كبير جداً."})
                continue
            
            # 2. Rate limiting check across all user connections
            if not manager.check_rate_limit(user.id):
                await websocket.send_json({"action": "error", "message": "أنت ترسل رسائل بسرعة كبيرة. يرجى الانتظار بضع ثوانٍ."})
                continue
                
            try:
                payload = json.loads(data)
                action = payload.get("action", "send")
                msg_text = str(payload.get("message", "")).strip()
                reply_to_id = payload.get("reply_to_id")
                if reply_to_id is not None:
                    try:
                        reply_to_id = int(reply_to_id)
                    except (ValueError, TypeError):
                        reply_to_id = None
            except json.JSONDecodeError:
                action = "send"
                msg_text = data.strip()
                reply_to_id = None
            
            if action == "send":
                if not msg_text:
                    continue

                if len(msg_text) > 1000:
                    await websocket.send_json({"action": "error", "message": "الرسالة طويلة جداً (الحد الأقصى 1000 حرف)."})
                    continue
                    
                # Sanitize input to prevent XSS (strict tags stripping)
                clean_message = bleach.clean(msg_text, tags=[], strip=True).strip()
                if not clean_message:
                    continue
                    
                # Save message to DB with foreign key validation
                db = SessionLocal()
                try:
                    # Validate reply_to_id exists to prevent Foreign Key constraint crash
                    if reply_to_id:
                        parent_exists = db.query(ChatMessage.id).filter(ChatMessage.id == reply_to_id).first()
                        if not parent_exists:
                            reply_to_id = None

                    chat_msg = ChatMessage(user_id=user.id, message=clean_message, reply_to_id=reply_to_id)
                    db.add(chat_msg)
                    db.commit()
                    db.refresh(chat_msg)
                    
                    # Fetch reply text if needed
                    reply_preview = None
                    reply_user_name = None
                    if reply_to_id:
                        replied = db.query(ChatMessage).options(joinedload(ChatMessage.user)).filter(ChatMessage.id == reply_to_id).first()
                        if replied:
                            reply_preview = replied.message
                            if replied.user:
                                reply_user_name = replied.user.full_name
                    
                    # Prepare broadcast data (structured identically to REST API)
                    msg_data = {
                        "action": "new_message",
                        "id": chat_msg.id,
                        "user_id": user.id,
                        "user_name": user.full_name,
                        "avatar": user.profile_picture_path,
                        "message": chat_msg.message,
                        "reply_to_id": reply_to_id,
                        "reply_preview": reply_preview,
                        "reply_user_name": reply_user_name,
                        "created_at": chat_msg.created_at.isoformat()
                    }
                    
                    # Broadcast
                    await manager.broadcast(msg_data)
                except Exception as db_err:
                    db.rollback()
                    await websocket.send_json({"action": "error", "message": "حدث خطأ أثناء حفظ الرسالة. يرجى المحاولة لاحقاً."})
                finally:
                    db.close()
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user.id)
    except Exception:
        manager.disconnect(websocket, user.id)


@router.delete("/messages/{msg_id}", response_model=schemas.MessageOut)
async def delete_message(msg_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    msg = db.query(ChatMessage).filter(ChatMessage.id == msg_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="الرسالة غير موجودة")
        
    if msg.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية لحذف هذه الرسالة")
        
    db.delete(msg)
    db.commit()
    
    # Broadcast deletion to remove from UI in real-time
    await manager.broadcast({
        "action": "delete_message",
        "message_id": msg_id
    })
    
    return {"message": "تم حذف الرسالة بنجاح"}


@router.get("/messages", response_model=List[schemas.ChatMessageOut])
def get_chat_messages(
    response: Response,
    limit: int = Query(default=35, ge=1, le=100, description="عدد الرسائل المطلوبة"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """جلب الرسائل السابقة بسرعة وكفاءة عالية"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    messages = (
        db.query(ChatMessage)
        .options(joinedload(ChatMessage.user), joinedload(ChatMessage.reply_to).joinedload(ChatMessage.user))
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )
    # Reverse so the newest is at the bottom
    messages.reverse()
    return messages
