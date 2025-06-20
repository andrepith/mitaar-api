from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from config.supabase_client import supabase
from models.employees import EmployeeRegister
from models.employees import LoginRequest
import jwt
import os
from typing import Optional

router = APIRouter()

# Load environment variables
load_dotenv()

# Configuration constants
SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Utility Functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(email: str) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "exp": expiration}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_employee_by_email(email: str) -> Optional[dict]:
    response = supabase.table("employees").select("*").eq("email", email).execute()
    return response.data[0] if response.data else None

# Dependencies
def get_current_user(request: Request) -> dict:
    # Try to get token from Authorization header
    auth_header = request.headers.get("authorization")
    token = None
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header[7:]
    else:
        # Fallback to cookie
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        user = get_employee_by_email(email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def require_level(min_level: int):
    def level_checker(user: dict = Depends(get_current_user)):
        if user.get("level", 0) < min_level:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
        return user
    return level_checker

def can_access_employee(employee_id: int, user: dict = Depends(get_current_user)):
    # Allow if user is admin (level >= 1) or editing their own record
    if user.get("level", 0) >= 1 or user.get("id") == employee_id:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough privileges to edit this employee."
    )

@router.post("/register", response_model=EmployeeRegister)
async def register_employee(employee: EmployeeRegister):
    """Register a new employee."""
    if get_employee_by_email(employee.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    employee_data = employee.model_dump()
    employee_data["password"] = hash_password(employee.password)

    response = supabase.table("employees").insert(employee_data).execute()
    if not response.data:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to register employee")

    return response.data[0]

@router.post("/login")
async def login_employee(login: LoginRequest, response: Response):
    """Login an employee and return a JWT token in an httpOnly cookie."""
    employee = get_employee_by_email(login.email)
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    if not verify_password(login.password, employee["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(employee["email"])
    # Set the token in an httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,  # Set to True in production (HTTPS)
        samesite="lax",  # or "strict" for more security
        max_age=60*60,  # 1 hour
        path="/"
    )
    return {"message": "Login successful"}

@router.post("/logout")
async def logout_employee(response: Response):
    Response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}

@router.post("/refresh-token")
async def refresh_token(token: str = Depends(oauth2_scheme)):
    """Refresh the JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        new_token = create_access_token(email)
        return {"access_token": new_token, "token_type": "bearer"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

