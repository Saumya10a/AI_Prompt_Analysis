from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router
from .services.mongodb import mongodb_service
from .services.dataset_generator import DatasetGenerator
from .core.config import settings
from pathlib import Path


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongodb_service.connect()
    
    dataset_path = Path(settings.dataset_path)
    if settings.dataset_generate_if_missing and not dataset_path.exists():
        generator = DatasetGenerator(settings.dataset_path, num_records=100_000)
        generator.generate_and_save()
    
    yield
    
    await mongodb_service.disconnect()
    from .services.spark_runtime import stop_spark_session
    stop_spark_session()


app = FastAPI(
    title="BDA Analytics API",
    description="Big Data Analytics Pipeline for AI Prompt and Response Analysis",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root():
    return {
        "message": "BDA Analytics API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/v1/health-ecosystem",
            "overview": "/api/v1/analytics/overview",
            "categories": "/api/v1/analytics/categories",
            "models": "/api/v1/analytics/models",
            "reconciliation": "/api/v1/analytics/reconciliation",
            "prompt_inspect": "/api/v1/prompt/inspect"
        }
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
