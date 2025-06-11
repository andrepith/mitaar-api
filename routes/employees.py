from fastapi import APIRouter
from models.employees import Employee
from models.employees import EmployeeUpdate
from config.supabase_client import supabase

router = APIRouter()

def sanitize_employees(data):
    """Remove sensitive fields like 'password' from employee records."""
    return [{k: v for k, v in emp.items() if k != "password"} for emp in data]

@router.get("/employees")
async def get_employees():
    """Fetch all employees from the database."""
    response = supabase.table("employees").select("*").execute()
    return sanitize_employees(response.data)

@router.post("/employees")
async def create_employee(employee: Employee):
    """Add a new employee to the database."""
    data = employee.model_dump()
    # Convert 'created_at' to ISO format if needed
    if "created_at" in data and hasattr(data["created_at"], "isoformat"):
        data["created_at"] = data["created_at"].isoformat()
    response = supabase.table("employees").insert(data).execute()
    return sanitize_employees(response.data)

@router.patch("/employees/{employee_id}")
async def update_employee(employee_id: int, employee: EmployeeUpdate):
    """Update an existing employee's details."""
    data = {k: v for k, v in employee.model_dump().items() if v is not None}
    # Convert 'created_at' to ISO format if needed
    if "created_at" in data and hasattr(data["created_at"], "isoformat"):
        data["created_at"] = data["created_at"].isoformat()
    if not data:
        return {"message": "No data to update"}
    response = supabase.table("employees").update(data).eq("id", employee_id).execute()
    return sanitize_employees(response.data)

@router.put("/employees/{employee_id}")
async def replace_employee(employee_id: int, employee: Employee):
    """Replace an existing employee's details (PUT). Ignores 'created_at'."""
    data = {k: v for k, v in employee.model_dump().items() if v is not None and k != "created_at"}
    if not data:
        return {"message": "No data to update"}
    response = supabase.table("employees").update(data).eq("id", employee_id).execute()
    return sanitize_employees(response.data)