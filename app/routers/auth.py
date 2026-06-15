from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse,UserLogin, Token
from app.utils import hash, verify
from app.oauth2 import create_access_token,  get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register",
response_model=UserResponse, status_code=201
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    hashed_password = hash(user.password)

    new_user = User(
        email=user.email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == user_credentials.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=403,
            detail="Invalid credentials"
        )

    if not verify(
        user_credentials.password,
        user.password
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid credentials"
        )

    access_token = create_access_token(
        data={"user_id": user.id}
    )
    print(access_token)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me",response_model=UserResponse)
def me(current_user = Depends(get_current_user)):
    return current_user