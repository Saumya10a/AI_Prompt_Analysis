from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from .enums import EngineStatus, EngineType


class EngineStatusInfo(BaseModel):
    engine_type: EngineType
    status: EngineStatus
    description: str
    version: Optional[str] = None
    last_checked: datetime


class PreprocessingMetadata(BaseModel):
    total_records_ingested: int
    malformed_rows_dropped: int
    fields_cleaned: int
    processing_time_seconds: float


class OverviewStats(BaseModel):
    total_records: int
    total_tokens: int
    average_tokens_per_record: float
    unique_categories: int
    unique_models: int
    overall_success_rate: float
    overall_quality_score: float
    generated_at: datetime


class CategoryAnalytics(BaseModel):
    category: str
    record_count: int
    token_total: int
    token_average: float
    success_count: int
    failure_count: int
    success_rate: float
    quality_score_average: float
    models_used: List[str]


class ModelAnalytics(BaseModel):
    model: str
    record_count: int
    token_total: int
    token_average: float
    success_count: int
    failure_count: int
    success_rate: float
    quality_score_average: float
    categories_processed: List[str]


class ReconciliationReport(BaseModel):
    engine_a: str
    engine_b: str
    metric_name: str
    value_a: float
    value_b: float
    match_status: bool
    absolute_delta: float
    percentage_delta: Optional[float] = None
    timestamp: datetime


class ScoreBreakdown(BaseModel):
    clarity_score: float = 0.0
    context_score: float = 0.0
    constraint_score: float = 0.0
    length_score: float = 0.0


class ModelRecommendation(BaseModel):
    recommended_model: str
    secondary_model: Optional[str] = None
    reason: str
    trade_off: str


class PromptInspectionResult(BaseModel):
    original_prompt: str
    word_count: int
    character_count: int
    code_blocks_detected: int
    constraints_extracted: List[str]
    specificity_score: float
    improvement_hints: List[str]
    inspected_at: datetime
    detected_intent: Optional[str] = None
    detected_audience: Optional[str] = None
    estimated_age_group: Optional[str] = None
    score_breakdown: Optional[ScoreBreakdown] = None
    model_recommendation: Optional[ModelRecommendation] = None



class HealthEcosystemResponse(BaseModel):
    system_status: str
    engines: List[EngineStatusInfo]
    mongodb_connected: bool
    dataset_loaded: bool
    last_pipeline_run: Optional[datetime] = None
