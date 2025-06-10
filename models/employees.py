from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class Employee(BaseModel):
    name: str = Field(..., description="Full name of the employee")
    email: EmailStr = Field(..., description="Employee email address")
    password: str = Field(..., description="Employee password")
    date: datetime = Field(default_factory=datetime.now, description="Creation date")

# Example usage:
# employee = Employee(name="John Doe", email="john@example.com", password="secret")