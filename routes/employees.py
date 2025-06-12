from fastapi import APIRouter, Query
from models.employees import Employee
from models.employees import EmployeeUpdate
from config.supabase_client import supabase

router = APIRouter()

def sanitize_employees(data):
    """Remove sensitive fields like 'password' from employee records."""
    return [{k: v for k, v in emp.items() if k != "password"} for emp in data]

@router.get("/employees")
async def get_employees(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Number of employees per page"),
):
    """Fetch employees with pagination and metadata."""
    offset = (page - 1) * limit
    start = offset
    end = offset + limit - 1

    # Get total count
    count_response = supabase.table("employees").select("id", count="exact").execute()
    total_data = count_response.count or 0

    # Get current page data
    response = supabase.table("employees").select("*").range(start, end).execute()
    employees = sanitize_employees(response.data)

    total_pages = (total_data + limit - 1) // limit if limit else 1

    return {
        "current_page": page,
        "total_pages": total_pages,
        "total_data": total_data,
        "data": employees
    }
    
@router.get("/employee/{employee_id}")
async def get_employee(employee_id: int):
    """Fetch a single employee by ID."""
    response = supabase.table("employees").select("*").eq("id", employee_id).execute()
    if not response.data:
        return {"message": "Employee not found"}
    sanitized = sanitize_employees(response.data)
    return sanitized[0] if sanitized else {"message": "Employee not found"}

@router.post("/employee")
async def create_employee(employee: Employee):
    """Add a new employee to the database."""
    data = employee.model_dump()
    # Convert 'created_at' to ISO format if needed
    if "created_at" in data and hasattr(data["created_at"], "isoformat"):
        data["created_at"] = data["created_at"].isoformat()
    response = supabase.table("employees").insert(data).execute()
    return sanitize_employees(response.data)

@router.patch("/employee/{employee_id}")
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

@router.put("/employee/{employee_id}")
async def replace_employee(employee_id: int, employee: Employee):
    """Replace an existing employee's details (PUT). Ignores 'created_at'."""
    data = {k: v for k, v in employee.model_dump().items() if v is not None and k != "created_at"}
    if not data:
        return {"message": "No data to update"}
    response = supabase.table("employees").update(data).eq("id", employee_id).execute()
    return sanitize_employees(response.data)

@router.delete("/employee/{employee_id}")
async def delete_employee(employee_id: int):
    """Delete an employee from the database."""
    response = supabase.table("employees").delete().eq("id", employee_id).execute()
    if response.data:
        return {"message": "Employee deleted successfully"}
    return {"message": "Employee not found or already deleted"}