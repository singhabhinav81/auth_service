from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from app.schemas.user_schema import UserResponse, UserCreate, Token
from app.services import auth_service, jwt_service
from app.utils.dependencies import get_db, get_current_active_user
from app.utils.logger import logger
from app.models.user import User

router = APIRouter()

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    """
    Register a new user.
    """
    logger.info(f"Initiating signup for user: {user_in.email}")
    user = auth_service.create_user(db, user=user_in)
    logger.info(f"User signup successful: {user.email}")
    return user

@router.post("/login", response_model=Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    logger.info(f"Login attempt for user: {form_data.username}")
    user = auth_service.authenticate_user(db, email=form_data.username, password=form_data.password)
    
    if not user:
        logger.warning(f"Failed login attempt for user: {form_data.username} (Incorrect credentials)")
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        logger.warning(f"Failed login attempt for user: {form_data.username} (Inactive user)")
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token = jwt_service.create_access_token(data={"sub": user.email})
    logger.info(f"Login successful for user: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_active_user)) -> Any:
    """
    Get current user details.
    """
    return current_user
