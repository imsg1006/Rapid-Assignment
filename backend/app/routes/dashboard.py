from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models import SearchHistory, ImageHistory, User

router = APIRouter(tags=["dashboard"])

@router.get("/")
def get_user_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    searches = db.query(SearchHistory).filter(SearchHistory.user_id == user.id).all()
    images = db.query(ImageHistory).filter(ImageHistory.user_id == user.id).all()
    return {"searches": searches, "images": images}

# Example of a protected endpoint for deleting an item
@router.delete("/search/{entry_id}")
def delete_search_entry(entry_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry = db.query(SearchHistory).filter(SearchHistory.id == entry_id, SearchHistory.user_id == user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
    return {"message": "Entry deleted successfully"}