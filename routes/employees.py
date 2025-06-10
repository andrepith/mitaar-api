from fastapi import APIRouter
from models.employees import Employee
from datetime import datetime

router = APIRouter()

# In-memory list to store employees (for demonstration purposes)
employees = [
    Employee(
        name="Alice Smith",
        email="alice@example.com",
        password="password123",
        date=datetime(2024, 6, 1, 10, 0, 0)
    ),
    Employee(
        name="Bob Johnson",
        email="bob@example.com",
        password="securepass",
        date=datetime(2024, 6, 2, 11, 30, 0)
    ),
    Employee(
        name="Charlie Brown",
        email="charlie@example.com",
        password="charliepw",
        date=datetime(2024, 6, 3, 9, 15, 0)
    ),
]

@router.get("/employees", response_model=list[Employee])
def get_employees():
    """Get the list of all employees."""
    return employees

@router.post("/employees", response_model=Employee)
def create_employee(employee: Employee):
    """Add a new employee."""
    employees.append(employee)
    return employee