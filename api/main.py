from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from api.core.config import settings
from api.db.database import create_tables
from api.routers import auth, predict, history



app = FastAPI(
    title="AI Diabetes Predictor",
    description="Predict diabetes risk and track your health history over time.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


@app.on_event("startup")
def on_startup():
    create_tables()



app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(history.router)



@app.get("/", response_class=FileResponse)
def index():
    return FileResponse("frontend/index.html")

@app.get("/dashboard", response_class=FileResponse)
def dashboard():
    return FileResponse("frontend/dashboard.html")

@app.get("/history-page", response_class=FileResponse)
def history_page():
    return FileResponse("frontend/history.html")

@app.get("/report-page", response_class=FileResponse)
def report_page():
    return FileResponse("frontend/report.html")
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

@app.get("/", response_class=FileResponse)
def index():
    return FileResponse("frontend/index.html")
    