from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.employees import router as employee_router
from routes.auth import router as auth_router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employee_router)
app.include_router(auth_router)