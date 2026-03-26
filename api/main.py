from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from api.core.config import settings
from api.db.database import create_tables
from api.routers import auth, predict, history

# ── App Init ──────────────────────────────────────────────────

app = FastAPI(
    title="AI Diabetes Predictor",
    description="Predict diabetes risk and track your health history over time.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Startup ───────────────────────────────────────────────────

@app.on_event("startup")
def on_startup():
    create_tables()

# ── API Routers ───────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(history.router)

# ── Frontend — single index.html SPA ─────────────────────────

@app.get("/", response_class=FileResponse)
def index():
    return FileResponse("Frontend/indexx.html")