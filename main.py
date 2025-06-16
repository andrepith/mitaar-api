from fastapi import FastAPI
from routes.employees import router as employee_router
from routes.auth import router as auth_router

app = FastAPI()

app.include_router(employee_router)
app.include_router(auth_router)