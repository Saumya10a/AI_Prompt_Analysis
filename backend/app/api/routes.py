from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from pydantic import BaseModel
from ..models.schemas import (
    HealthEcosystemResponse, OverviewStats, CategoryAnalytics, 
    ModelAnalytics, ReconciliationReport, PromptInspectionResult
)
from ..services.environment_inspector import EnvironmentInspector
from ..services.ingestion import DatasetIngestion
from ..services.analytics_python import PythonBaselineAnalytics
from ..services.analytics_pyspark import PySparkAnalytics
from ..services.analytics_sparksql import SparkSQLAnalytics
from ..services.spark_runtime import get_spark_session
from ..services.analytics_mapreduce import MapReduceAnalytics
from ..services.reconciliation import ReconciliationEngine
from ..services.prompt_analyzer import PromptAnalyzer
from ..services.mongodb import mongodb_service
from ..core.config import settings


router = APIRouter(prefix="/api/v1")


class PromptInspectionRequest(BaseModel):
    prompt: str


environment_inspector = EnvironmentInspector()
reconciliation_engine = ReconciliationEngine()
prompt_analyzer = PromptAnalyzer()


async def _cache_read(method, fallback):
    """Cache failures never block calculations from the local dataset."""
    try:
        return await method()
    except Exception:
        return fallback


async def _cache_write(method, value):
    """Persistence is best-effort; the API response remains usable without MongoDB."""
    try:
        await method(value)
    except Exception:
        pass


@router.get("/health-ecosystem", response_model=HealthEcosystemResponse)
async def get_health_ecosystem():
    engines = environment_inspector.inspect_all()
    
    mongodb_connected = await mongodb_service.health_check()
    
    dataset_path = settings.dataset_path
    from pathlib import Path
    dataset_loaded = Path(dataset_path).exists()
    
    return HealthEcosystemResponse(
        # The demo's analytics path is local Python + JSONL; MongoDB is only an optional cache.
        system_status="operational" if dataset_loaded else "degraded",
        engines=engines,
        mongodb_connected=mongodb_connected,
        dataset_loaded=dataset_loaded
    )


_cached_df = None
_cached_mtime = None


def _get_processed_df():
    global _cached_df, _cached_mtime
    from pathlib import Path
    dataset_path = Path(settings.dataset_path)
    if not dataset_path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    current_mtime = dataset_path.stat().st_mtime
    if _cached_df is not None and _cached_mtime == current_mtime:
        return _cached_df
    
    ingestion = DatasetIngestion(str(dataset_path))
    if not ingestion.load_dataset():
        raise HTTPException(status_code=404, detail="Dataset not found")
    ingestion.preprocess()
    _cached_df = ingestion.get_processed_dataframe()
    _cached_mtime = current_mtime
    return _cached_df


@router.get("/analytics/overview", response_model=OverviewStats)
async def get_overview_analytics():
    try:
        df = _get_processed_df()
        analytics = PythonBaselineAnalytics(df)
        stats = analytics.compute_overview()
        
        await _cache_write(mongodb_service.store_overview_stats, stats.dict())
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/categories", response_model=list[CategoryAnalytics])
async def get_category_analytics():
    try:
        df = _get_processed_df()
        analytics = PythonBaselineAnalytics(df)
        categories = analytics.compute_category_analytics()
        
        await _cache_write(mongodb_service.store_category_analytics, [c.dict() for c in categories])
        
        return categories
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/models", response_model=list[ModelAnalytics])
async def get_model_analytics():
    try:
        df = _get_processed_df()
        analytics = PythonBaselineAnalytics(df)
        models = analytics.compute_model_analytics()
        
        await _cache_write(mongodb_service.store_model_analytics, [m.dict() for m in models])
        
        return models
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/reconciliation", response_model=list[ReconciliationReport])
async def get_reconciliation_reports():
    try:
        df = _get_processed_df()
        data = df.to_dict('records')

        
        python_analytics = PythonBaselineAnalytics(df)
        python_analytics.compute_overview()
        python_analytics.compute_category_analytics()
        python_analytics.compute_model_analytics()
        python_results = python_analytics.get_all_results()
        
        mapreduce_analytics = MapReduceAnalytics(data)
        mapreduce_analytics.compute_overview()
        mapreduce_analytics.compute_category_analytics()
        mapreduce_analytics.compute_model_analytics()
        mapreduce_results = mapreduce_analytics.get_all_results()
        
        reconciler = ReconciliationEngine()
        reports = reconciler.compare_engines(
            python_results, mapreduce_results, 
            "PYTHON_BASELINE", "MAPREDUCE"
        )

        try:
            spark = get_spark_session(settings.spark_master, settings.spark_app_name)
            from pyspark.sql import functions as F
            from pyspark.sql import functions as F

            # Let Spark read JSONL itself. This keeps the Spark path independent
            # of pandas and avoids sending the full dataset through Python workers.
            spark_df = spark.read.json(settings.dataset_path)
            prompt_lower = F.lower(F.col("prompt"))
            action_requested = F.lit(False)
            for verb in ("explain", "describe", "analyze", "compare"):
                action_requested = action_requested | prompt_lower.contains(verb)
            quality_score = (
                F.when(F.length(F.trim(F.col("prompt"))) > 10, 0.2).otherwise(0.0)
                + F.when(F.length(F.trim(F.col("response"))) > 10, 0.2).otherwise(0.0)
                + F.when(action_requested, 0.2).otherwise(0.0)
                + F.when(~F.lower(F.col("response")).contains("error") & ~F.lower(F.col("response")).contains("failed"), 0.2).otherwise(0.0)
                + F.when(F.coalesce(F.col("success"), F.lit(True)), 0.2).otherwise(0.0)
            )
            spark_df = spark_df.withColumn("quality_score", quality_score).cache()
            spark_df.count()  # Materialize the JSONL read once for both Spark engines.

            dataframe_analytics = PySparkAnalytics(spark, spark_df)
            dataframe_analytics.compute_overview()
            dataframe_analytics.compute_category_analytics()
            dataframe_analytics.compute_model_analytics()
            dataframe_results = dataframe_analytics.get_all_results()
            if len(dataframe_results) == 3:
                reports.extend(reconciler.compare_engines(
                    python_results, dataframe_results,
                    "PYTHON_BASELINE", "PYSPARK"
                ))

            sql_analytics = SparkSQLAnalytics(spark, spark_df)
            sql_analytics.compute_overview()
            sql_analytics.compute_category_analytics()
            sql_analytics.compute_model_analytics()
            sql_results = sql_analytics.get_all_results()
            if len(sql_results) == 3:
                reports.extend(reconciler.compare_engines(
                    python_results, sql_results,
                    "PYTHON_BASELINE", "SPARK_SQL"
                ))
        except Exception as spark_error:
            # The Python and local MapReduce results remain presentable if Spark
            # cannot start on a particular machine.
            print(f"Optional Spark reconciliation was skipped: {spark_error}")
        
        await _cache_write(mongodb_service.store_reconciliation_reports, [r.dict() for r in reports])
        
        return reports
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prompt/inspect", response_model=PromptInspectionResult)
async def inspect_prompt(request: PromptInspectionRequest):
    try:
        result = prompt_analyzer.analyze(request.prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
