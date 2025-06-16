from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class Employee(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the employee")
    email: EmailStr = Field(..., description="Employee's email address")
    password: str = Field(..., min_length=8, description="Password for the employee account")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    level: int = Field(default=0, ge=0, le=5, description="Employee's level in the organization")

class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    created_at: Optional[datetime] = None  # Changed to datetime for consistency
    level: Optional[int] = Field(default=0, ge=0, le=5, description="Employee's level in the organization")

class EmployeeRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the employee")
    email: EmailStr = Field(..., description="Employee's email address")
    password: str = Field(..., min_length=8, description="Password for the employee account")