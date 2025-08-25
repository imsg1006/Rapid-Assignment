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

# Delete search entry
@router.delete("/search/{entry_id}")
def delete_search_entry(entry_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry = db.query(SearchHistory).filter(SearchHistory.id == entry_id, SearchHistory.user_id == user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
    return {"message": "Search entry deleted successfully"}

# ✅ Delete image entry
@router.delete("/image/{entry_id}")
def delete_image_entry(entry_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry = db.query(ImageHistory).filter(ImageHistory.id == entry_id, ImageHistory.user_id == user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Image entry not found")
    db.delete(entry)
    db.commit()
    return {"message": "Image entry deleted successfully"}
