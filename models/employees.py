from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class Employee(BaseModel):
    name: str = Field(..., description="Full name of the employee")
    email: EmailStr = Field(..., description="Employee email address")
    password: str = Field(..., description="Employee password")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation date")
    
class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    created_at: Optional[str] = None

# Example usage:
# employee = Employee(name="John Doe", email="john@example.com", password="secret")