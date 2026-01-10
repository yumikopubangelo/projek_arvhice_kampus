# imports
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt

from app.database import get_db
from app.config import get_settings
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserRead, Token
from app.utils.password import hash_password, verify_password
from app.utils.encryption import decrypt_sensitive_fields
from app.dependencies.dependencies import get_current_active_user # Import the centralized dependency

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()

# =====================================================
# REGISTER ENDPOINT
# =====================================================
@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_data: dict, db: Session = Depends(get_db)):
    """
    Register new user (student or dosen)
    """
    # Decrypt sensitive fields
    decrypted_data = decrypt_sensitive_fields(user_data)

    # Create Pydantic model from decrypted data
    try:
        user_create = UserCreate(**decrypted_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data: {str(e)}"
        )

    print(f"📝 Registration attempt: {user_create.email}")
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_create.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if student_id already exists (if provided)
    if user_create.student_id:
        existing_student = db.query(User).filter(User.student_id == user_create.student_id).first()
        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student ID already registered"
            )

    # Create new user
    new_user = User(
        email=user_create.email,
        hashed_password=hash_password(user_create.password),
        full_name=user_create.full_name,
        role=user_create.role,
        student_id=user_create.student_id if user_create.role == "student" else None,
        department=user_create.department if user_create.role == "dosen" else None,
        title=user_create.title if user_create.role == "dosen" else None,
        phone=user_create.phone,
        is_active=True,
        is_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    print(f"✅ User registered successfully: {new_user.email}")
    
    return new_user


# =====================================================
# LOGIN ENDPOINT
# =====================================================
@router.post("/login", response_model=Token)
async def login(credentials: dict, db: Session = Depends(get_db)):
    """
    Login user and return JWT token
    """
    # Decrypt sensitive fields
    decrypted_credentials = decrypt_sensitive_fields(credentials)

    # Create Pydantic model
    try:
        login_data = UserLogin(**decrypted_credentials)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid login data: {str(e)}"
        )

    print(f"🔐 Login attempt: {login_data.email}")
    
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user:
        print(f"❌ User not found: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        print(f"❌ Invalid password for: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        print(f"❌ Inactive user: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Generate JWT token
    access_token = create_access_token(user_id=user.id, role=user.role)

    print(f"✅ Login successful: {user.email}")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }


# =====================================================
# HELPER FUNCTIONS
# =====================================================
def create_access_token(user_id: int, role: str) -> str:
    """
    Create JWT access token
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

# =====================================================
# GET CURRENT USER (PROFILE)
# =====================================================
@router.get("/me", response_model=UserRead)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current logged-in user profile
    """
    print(f"👤 Get profile: {current_user.email}")
    return current_user
