from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models import SearchHistory, ImageHistory, User
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["dashboard"])

 
# Schemas for PATCH (missing before) 
class SearchUpdate(BaseModel):
    query: Optional[str] = None

class ImageUpdate(BaseModel):
    prompt: Optional[str] = None

 
# Get full history 
@router.get("/")
def get_user_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    searches = db.query(SearchHistory).filter(SearchHistory.user_id == user.id).all()
    images = db.query(ImageHistory).filter(ImageHistory.user_id == user.id).all()
    return {"searches": searches, "images": images}

 
# Delete search entry 
@router.delete("/search/{entry_id}")
def delete_search_entry(entry_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry = db.query(SearchHistory).filter(SearchHistory.id == entry_id, SearchHistory.user_id == user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
    return {"message": "Search entry deleted successfully"}

 
# Delete image entry 
@router.delete("/image/{entry_id}")
def delete_image_entry(entry_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry = db.query(ImageHistory).filter(ImageHistory.id == entry_id, ImageHistory.user_id == user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Image entry not found")
    db.delete(entry)
    db.commit()
    return {"message": "Image entry deleted successfully"}

 
#   PATCH search entry 
@router.patch("/search/{entry_id}")
def update_search_entry(
    entry_id: int,
    update_data: SearchUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(SearchHistory).filter(SearchHistory.id == entry_id, SearchHistory.user_id == user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Search entry not found")

    if update_data.query is not None:
        entry.query = update_data.query

    db.commit()
    db.refresh(entry)
    return {"message": "Search entry updated successfully", "entry": entry}

 
#   PATCH image entry 
@router.patch("/image/{entry_id}")
def update_image_entry(
    entry_id: int,
    update_data: ImageUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(ImageHistory).filter(ImageHistory.id == entry_id, ImageHistory.user_id == user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Image entry not found")

    if update_data.prompt is not None:
        entry.prompt = update_data.prompt

    db.commit()
    db.refresh(entry)
    return {"message": "Image entry updated successfully", "entry": entry}