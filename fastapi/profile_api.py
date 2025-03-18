from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime
import uuid

app = FastAPI()

# Profile models
class ProfileBase(BaseModel):
    username: str
    email: str
    full_name: str
    bio: Optional[str] = None
    
    @validator('email')
    def validate_email(cls, v):
        # Simple email validation
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v
    
class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    
    @validator('email')
    def validate_email(cls, v):
        if v is not None and '@' not in v:
            raise ValueError('Invalid email format')
        return v

class Profile(ProfileBase):
    id: str
    created_at: str
    updated_at: str
    links: Dict[str, str] = {}

# In-memory database for profiles
profiles_db = []

@app.get("/")
def index():
    return {"message": "Welcome to the Profiles API"}

@app.get("/profiles/", response_model=List[Profile])
def get_all_profiles():
    """Get all profiles"""
    return profiles_db

@app.get("/profiles/{profile_id}", response_model=Profile)
def get_profile(profile_id: str = Path(..., title="The ID of the profile to retrieve")):
    """Get a specific profile by ID"""
    for profile in profiles_db:
        if profile.id == profile_id:
            return profile
    raise HTTPException(status_code=404, detail="Profile not found")

@app.get("/profiles/username/{username}", response_model=Profile)
def get_profile_by_username(username: str):
    """Get a specific profile by username"""
    for profile in profiles_db:
        if profile.username.lower() == username.lower():
            return profile
    raise HTTPException(status_code=404, detail="Profile not found")

@app.post("/profiles/", response_model=Profile)
def create_profile(profile: ProfileCreate):
    """Create a new profile"""
    # Check if username already exists
    for existing_profile in profiles_db:
        if existing_profile.username.lower() == profile.username.lower():
            raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new profile
    now = datetime.now().isoformat()
    new_profile = Profile(
        id=str(uuid.uuid4()),
        username=profile.username,
        email=profile.email,
        full_name=profile.full_name,
        bio=profile.bio,
        created_at=now,
        updated_at=now,
        links={
            "self": f"/profiles/{profile.username}",
            "messages": f"/messages/sender/{profile.username}"
        }
    )
    profiles_db.append(new_profile)
    return new_profile

@app.put("/profiles/{profile_id}", response_model=Profile)
def update_profile(
    profile_update: ProfileUpdate,
    profile_id: str = Path(..., title="The ID of the profile to update")
):
    """Update a profile"""
    for i, profile in enumerate(profiles_db):
        if profile.id == profile_id:
            update_data = profile_update.dict(exclude_unset=True)
            # Add updated timestamp
            update_data["updated_at"] = datetime.now().isoformat()
            
            # Create updated profile
            updated_profile = profile.copy(update=update_data)
            profiles_db[i] = updated_profile
            return updated_profile
    raise HTTPException(status_code=404, detail="Profile not found")

@app.delete("/profiles/{profile_id}")
def delete_profile(profile_id: str = Path(..., title="The ID of the profile to delete")):
    """Delete a profile"""
    for i, profile in enumerate(profiles_db):
        if profile.id == profile_id:
            deleted_profile = profiles_db.pop(i)
            return {"message": f"Profile '{deleted_profile.username}' deleted successfully"}
    raise HTTPException(status_code=404, detail="Profile not found")

# To run this API use: uvicorn profile_api:app --reload
