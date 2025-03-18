from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

app = FastAPI()

# Message model
class MessageCreate(BaseModel):
    sender: str
    recipient: str
    content: str
    
class MessageUpdate(BaseModel):
    content: Optional[str] = None
    is_read: Optional[bool] = None
    
class Message(BaseModel):
    id: str
    sender: str
    recipient: str
    content: str
    timestamp: str
    is_read: bool

# In-memory database for messages
messages_db = []

@app.get("/")
def index():
    return {"message": "Welcome to the Messaging API"}

@app.get("/messages/", response_model=List[Message])
def get_all_messages():
    """Get all messages"""
    return messages_db

@app.get("/messages/{message_id}", response_model=Message)
def get_message(message_id: str = Path(..., title="The ID of the message to retrieve")):
    """Get a specific message by ID"""
    for message in messages_db:
        if message.id == message_id:
            return message
    raise HTTPException(status_code=404, detail="Message not found")

@app.post("/messages/", response_model=Message)
def create_message(message: MessageCreate):
    """Create a new message"""
    new_message = Message(
        id=str(uuid.uuid4()),
        sender=message.sender,
        recipient=message.recipient,
        content=message.content,
        timestamp=datetime.now().isoformat(),
        is_read=False
    )
    messages_db.append(new_message)
    return new_message

@app.put("/messages/{message_id}", response_model=Message)
def update_message(
    message_update: MessageUpdate,
    message_id: str = Path(..., title="The ID of the message to update")
):
    """Update a message"""
    for i, message in enumerate(messages_db):
        if message.id == message_id:
            update_data = message_update.dict(exclude_unset=True)
            updated_message = message.copy(update=update_data)
            messages_db[i] = updated_message
            return updated_message
    raise HTTPException(status_code=404, detail="Message not found")

@app.delete("/messages/{message_id}")
def delete_message(message_id: str = Path(..., title="The ID of the message to delete")):
    """Delete a message"""
    for i, message in enumerate(messages_db):
        if message.id == message_id:
            del messages_db[i]
            return {"message": "Message deleted successfully"}
    raise HTTPException(status_code=404, detail="Message not found")

# Additional endpoints for specific use cases

@app.get("/messages/sender/{sender}", response_model=List[Message])
def get_messages_by_sender(sender: str):
    """Get all messages from a specific sender"""
    return [msg for msg in messages_db if msg.sender.lower() == sender.lower()]

@app.get("/messages/recipient/{recipient}", response_model=List[Message])
def get_messages_by_recipient(recipient: str):
    """Get all messages for a specific recipient"""
    return [msg for msg in messages_db if msg.recipient.lower() == recipient.lower()]


