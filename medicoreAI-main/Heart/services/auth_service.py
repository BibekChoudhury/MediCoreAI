"""
Heart Health Module - Authentication Service
JWT token management, password hashing, RBAC
"""
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from models.db_models import User, AuditLog
import config


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8')[:72], salt)
    return hashed.decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    try:
        return bcrypt.checkpw(plain.encode('utf-8')[:72], hashed.encode('utf-8'))
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        return payload
    except JWTError:
        return None


def register_user(db: Session, username: str, email: str, password: str,
                  full_name: Optional[str] = None, age: Optional[int] = None, gender: Optional[str] = None,
                  role: str = "patient") -> User:
    hashed = hash_password(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed,
        full_name=full_name,
        age=age,
        gender=gender,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    log_audit(db, user.id, "user_registered", "users")  # type: ignore
    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.hashed_password):  # type: ignore
        log_audit(db, user.id, "user_login", "auth")  # type: ignore
        return user
    return None


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def log_audit(db: Session, user_id: int, action: str, resource: str,
              details: Optional[dict] = None, ip_address: Optional[str] = None):
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        details=details or {},
        ip_address=ip_address
    )
    db.add(entry)
    db.commit()
