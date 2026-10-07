export type EngineStatus = 
  | 'AVAILABLE'
  | 'NOT_INSTALLED'
  | 'NOT_CONFIGURED'
  | 'CONFIGURED_BUT_OFFLINE'
  | 'EXECUTION_FAILED'
  | 'VALIDATED_LOCALLY';

export type EngineType = 
  | 'PYTHON_BASELINE'
  | 'PYSPARK'
  | 'SPARK_SQL'
  | 'MAPREDUCE'
  | 'MONGODB'
  | 'HADOOP'
  | 'HIVE'
  | 'PIG'
  | 'SQOOP';

export interface EngineStatusInfo {
  engine_type: EngineType;
  status: EngineStatus;
  description: string;
  version: string | null;
  last_checked: string;
}

export interface OverviewStats {
  total_records: number;
  total_tokens: number;
  average_tokens_per_record: number;
  unique_categories: number;
  unique_models: number;
  overall_success_rate: number;
  overall_quality_score: number;
  generated_at: string;
}

export interface CategoryAnalytics {
  category: string;
  record_count: number;
  token_total: number;
  token_average: number;
  success_count: number;
  failure_count: number;
  success_rate: number;
  quality_score_average: number;
  models_used: string[];
}

export interface ModelAnalytics {
  model: string;
  record_count: number;
  token_total: number;
  token_average: number;
  success_count: number;
  failure_count: number;
  success_rate: number;
  quality_score_average: number;
  categories_processed: string[];
}

export interface ReconciliationReport {
  engine_a: string;
  engine_b: string;
  metric_name: string;
  value_a: number;
  value_b: number;
  match_status: boolean;
  absolute_delta: number;
  percentage_delta: number | null;
  timestamp: string;
}

export interface ScoreBreakdown {
  clarity_score: number;
  context_score: number;
  constraint_score: number;
  length_score: number;
}

export interface ModelRecommendation {
  recommended_model: string;
  secondary_model?: string;
  reason: string;
  trade_off: string;
}

export interface PromptInspectionResult {
  original_prompt: string;
  word_count: number;
  character_count: number;
  code_blocks_detected: number;
  constraints_extracted: string[];
  specificity_score: number;
  improvement_hints: string[];
  inspected_at: string;
  detected_intent?: string;
  detected_audience?: string;
  estimated_age_group?: string;
  score_breakdown?: ScoreBreakdown;
  model_recommendation?: ModelRecommendation;
}


export interface HealthEcosystemResponse {
  system_status: string;
  engines: EngineStatusInfo[];
  mongodb_connected: boolean;
  dataset_loaded: boolean;
  last_pipeline_run: string | null;
}

export interface ApiError {
  message: string;
  status?: number;
}
