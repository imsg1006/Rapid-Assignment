from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# User schemas
class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    is_admin: bool = False

# Image schemas
class ImageRequest(BaseModel):
    prompt: str

class ImageResponse(BaseModel):
    id: int
    prompt: str
    image_url: str
    timestamp: datetime
    user_id: int
    
    class Config:
        from_attributes = True

# Search schemas
class SearchResponse(BaseModel):
    id: int
    query: str
    results: str  # JSON string
    timestamp: datetime
    user_id: int
    
    class Config:
        from_attributes = True

# Dashboard schemas
class DashboardEntry(BaseModel):
    searches: List[SearchResponse]
    images: List[ImageResponse]

class HistoryBase(BaseModel):
    type: str
    query: str
    result: str
    meta_data: Optional[str] = None

class HistoryCreate(HistoryBase):
    pass    

class HistoryResponse(HistoryBase):
    id: int
    user_id: int
    timestamp: datetime
    class Config:
        orm_mode = True    