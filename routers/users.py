"""
routers/users.py - 사용자 API 라우터
회원가입, 로그인, JWT 인증
passlib 대신 bcrypt를 직접 사용 (bcrypt 4.x / Python 3.14 호환)
"""

import bcrypt
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from models import User
from config import get_settings
from database import get_db
from core.exceptions import AuthenticationError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

router = APIRouter(prefix="/api/users", tags=["사용자"])
settings = get_settings()


def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """비밀번호 검증"""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(data: dict) -> str:
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """회원가입"""
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 사용자 이름입니다",
        )

    user = User(
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        grade=user_data.grade,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "username": user.username})
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            username=user.username,
            grade=user.grade,
            created_at=user.created_at,
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """로그인"""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 사용자 이름 또는 비밀번호입니다",
        )

    token = create_access_token({"sub": str(user.id), "username": user.username})
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            username=user.username,
            grade=user.grade,
            created_at=user.created_at,
        ),
    )


async def get_current_user_dep(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """JWT 토큰을 검증하고 현재 사용자를 반환하는 의존성"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise AuthenticationError("유효하지 않은 토큰입니다.")
    except JWTError:
        raise AuthenticationError("유효하지 않은 토큰입니다.")

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise AuthenticationError("사용자를 찾을 수 없습니다.")
    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user_dep)):
    """현재 사용자 정보"""
    return current_user
