from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1 import diseases, history, predict, stats, system
from app.config import settings
from app.database import init_db
from app.ml.model_service import model_service
from app.services.knowledge_service import knowledge_service

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    print("[Lifecycle] Starting AgriShield backend...")
    init_db()
    knowledge_service.load_kb()
    model_service.load_model()
    print("[Lifecycle] AgriShield backend is ready for inference.")
    yield
    # Shutdown sequence
    print("[Lifecycle] Shutting down AgriShield backend.")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Production-grade AI Crop Disease Detection System REST API. "
        "Provides PyTorch MobileNetV3 inference, plant leaf validation, "
        "calibrated uncertainty metrics, and structured disease management advice."
    ),
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 routes
app.include_router(predict.router, prefix="/api/v1")
app.include_router(history.router, prefix="/api/v1")
app.include_router(diseases.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")
app.include_router(system.router, prefix="/api/v1")

# Mount static asset directories
app.mount("/uploads", StaticFiles(directory=str(settings.uploads_dir)), name="uploads")
app.mount("/samples", StaticFiles(directory=str(settings.sample_dir)), name="samples")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Custom validation error response
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "message": "The submitted request failed validation."
        }
    )

# SPA fallback handler for React Router client-side routes
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa_frontend(full_path: str):
    # If file exists in static dir, serve it
    file_path = STATIC_DIR / full_path
    if full_path and file_path.is_file():
        return FileResponse(file_path)

    # Otherwise return the SPA index.html
    index_file = STATIC_DIR / "index.html"
    if index_file.is_file():
        return FileResponse(index_file)

    return JSONResponse(
        status_code=404,
        content={"message": "Frontend build not found. Please access /api/v1/health or /docs for API documentation."}
    )
