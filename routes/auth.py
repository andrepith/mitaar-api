from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta
from dotenv import load_dotenv
from config.supabase_client import supabase
from models.employees import EmployeeRegister
import jwt
import os

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
    expiration = datetime.now(datetime.timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "exp": expiration}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_employee_by_email(email: str) -> dict | None:
    response = supabase.table("employees").select("*").eq("email", email).execute()
    return response.data[0] if response.data else None