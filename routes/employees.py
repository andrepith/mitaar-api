from fastapi import APIRouter, Query, Depends
from models.employees import Employee, EmployeeUpdate
from config.supabase_client import supabase
from routes.auth import require_level, can_access_employee

router = APIRouter()

def sanitize_employees(data: list[dict]) -> list[dict]:
    """Remove sensitive fields like 'password' from employee records."""
    return [{k: v for k, v in emp.items() if k != "password"} for emp in data]

def sanitize_single_employee(data: list[dict]) -> dict:
    """Sanitize and return a single employee, or not found message."""
    if not data:
        return {"message": "Employee not found"}
    return sanitize_employees(data)[0]

@router.get("/employees")
async def get_employees(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Employees per page"),
    user: dict = Depends(require_level(1)),
    ):
    
    """Fetch employees with pagination and metadata."""
    offset = (page - 1) * limit

    # Total count
    count_response = supabase.table("employees").select("id", count="exact").execute()
    total_data = count_response.count or 0
    total_pages = (total_data + limit - 1) // limit

    # Paginated data
    data_response = (
        supabase.table("employees").select("*").range(offset, offset + limit - 1).execute()
    )
    employees = sanitize_employees(data_response.data)

    return {
        "current_page": page,
        "total_pages": total_pages,
        "total_data": total_data,
        "data": employees,
    }

@router.get("/employee/{employee_id}")
async def get_employee(
    employee_id: int, 
    user: dict = Depends(can_access_employee),
    ):
    """Fetch a single employee by ID."""
    response = supabase.table("employees").select("*").eq("id", employee_id).execute()
    return sanitize_single_employee(response.data)

@router.post("/employee")
async def create_employee(
    employee: Employee,
    user: dict = Depends(can_access_employee)
    ):
    """Add a new employee to the database."""
    data = employee.model_dump()
    if "created_at" in data and hasattr(data["created_at"], "isoformat"):
        data["created_at"] = data["created_at"].isoformat()

    response = supabase.table("employees").insert(data).execute()
    return sanitize_single_employee(response.data)

@router.patch("/employee/{employee_id}")
async def update_employee(
    employee_id: int, 
    employee: EmployeeUpdate,
    user: dict = Depends(can_access_employee)
    ):
    """Update an existing employee's details."""
    data = {k: v for k, v in employee.model_dump().items() if v is not None}
    if "created_at" in data and hasattr(data["created_at"], "isoformat"):
        data["created_at"] = data["created_at"].isoformat()

    if not data:
        return {"message": "No data to update"}

    response = supabase.table("employees").update(data).eq("id", employee_id).execute()
    return sanitize_single_employee(response.data)

@router.put("/employee/{employee_id}")
async def replace_employee(
    employee_id: int, 
    employee: Employee,
    user: dict = Depends(can_access_employee)
    ):
    """Replace an employee's details completely (excluding created_at)."""
    data = {
        k: v for k, v in employee.model_dump().items()
        if v is not None and k != "created_at"
    }

    if not data:
        return {"message": "No data to update"}

    response = supabase.table("employees").update(data).eq("id", employee_id).execute()
    return sanitize_single_employee(response.data)

@router.delete("/employee/{employee_id}")
async def delete_employee(
    employee_id: int,
    user: dict = Depends(require_level(1))
    ):
    """Delete an employee by ID."""
    response = supabase.table("employees").delete().eq("id", employee_id).execute()
    if response.data:
        return {"message": "Employee deleted successfully"}
    return {"message": "Employee not found or already deleted"}
