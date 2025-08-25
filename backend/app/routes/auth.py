
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas import UserCreate, Token
from app.dependencies import get_db
from app.security import get_password_hash, verify_password, create_access_token
from app.models import User
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Attempting to register user: {user.username}")
    
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        logger.warning(f"Username {user.username} already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    try:
        hashed_password = get_password_hash(user.password)
        db_user = User(username=user.username, hashed_password=hashed_password)
        
        logger.info(f"Adding user to database: {user.username}")
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"User registered successfully with ID: {db_user.id}")
        return {"message": "User registered successfully", "user_id": db_user.id}
        
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Registration failed: {str(e)}")

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Login attempt for user: {form_data.username}")
    
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        logger.warning(f"User not found: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Invalid password for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username, "is_admin": user.is_admin})
    logger.info(f"Token created successfully for user: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}
