from fastapi import APIRouter
from models.employees import Employee
from models.employees import EmployeeUpdate
from config.supabase_client import supabase

router = APIRouter()

@router.get("/employees")
async def get_employees():
    """Fetch all employees from the database."""
    response = supabase.table("employees").select("id, name, email, created_at").execute()
    return response.data

