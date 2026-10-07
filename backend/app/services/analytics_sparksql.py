from typing import Dict, Any, List, Optional
from datetime import datetime
from ..models.schemas import OverviewStats, CategoryAnalytics, ModelAnalytics


class SparkSQLAnalytics:
    def __init__(self, spark_session, df):
        self.spark = spark_session
        self.df = df
        self.df.createOrReplaceTempView("analytics_data")
        self._results: Dict[str, Any] = {}
    
    def compute_overview(self) -> Optional[OverviewStats]:
        try:
            overview_query = """
                SELECT 
                    COUNT(*) as total_records,
                    SUM(token_count) as total_tokens,
                    AVG(token_count) as avg_tokens,
                    COUNT(DISTINCT category) as unique_categories,
                    COUNT(DISTINCT model) as unique_models,
                    SUM(CAST(success AS INT)) as success_count,
                    AVG(quality_score) as overall_quality
                FROM analytics_data
            """
            
            result = self.spark.sql(overview_query).collect()[0]
            
            total_records = result['total_records']
            total_tokens = int(result['total_tokens']) if result['total_tokens'] else 0
            avg_tokens = float(result['avg_tokens']) if result['avg_tokens'] else 0
            unique_categories = result['unique_categories']
            unique_models = result['unique_models']
            success_count = int(result['success_count']) if result['success_count'] else 0
            overall_success_rate = (success_count / total_records * 100) if total_records > 0 else 0
            overall_quality = float(result['overall_quality']) if result['overall_quality'] else 0
            
            stats = OverviewStats(
                total_records=total_records,
                total_tokens=total_tokens,
                average_tokens_per_record=round(avg_tokens, 2),
                unique_categories=unique_categories,
                unique_models=unique_models,
                overall_success_rate=round(overall_success_rate, 2),
                overall_quality_score=round(overall_quality, 2),
                generated_at=datetime.utcnow()
            )
            
            self._results['overview'] = stats.dict()
            return stats
        except Exception as e:
            print(f"Spark SQL overview computation error: {e}")
            return None
    
    def compute_category_analytics(self) -> Optional[List[CategoryAnalytics]]:
        try:
            category_query = """
                SELECT 
                    category,
                    COUNT(*) as record_count,
                    SUM(token_count) as token_total,
                    SUM(CAST(success AS INT)) as success_count,
                    AVG(quality_score) as quality_avg,
                    COLLECT_SET(model) as models_used
                FROM analytics_data
                GROUP BY category
                ORDER BY category
            """
            
            results = self.spark.sql(category_query).collect()
            
            analytics = []
            for row in results:
                record_count = row['record_count']
                token_total = int(row['token_total']) if row['token_total'] else 0
                token_avg = token_total / record_count if record_count > 0 else 0
                success_count = int(row['success_count']) if row['success_count'] else 0
                failure_count = record_count - success_count
                success_rate = (success_count / record_count * 100) if record_count > 0 else 0
                quality_avg = float(row['quality_avg']) if row['quality_avg'] else 0
                
                models = row['models_used'] or []
                
                analytics.append(CategoryAnalytics(
                    category=row['category'],
                    record_count=record_count,
                    token_total=token_total,
                    token_average=round(token_avg, 2),
                    success_count=success_count,
                    failure_count=failure_count,
                    success_rate=round(success_rate, 2),
                    quality_score_average=round(quality_avg, 2),
                    models_used=models
                ))
            
            self._results['categories'] = [a.dict() for a in analytics]
            return analytics
        except Exception as e:
            print(f"Spark SQL category analytics error: {e}")
            return None
    
    def compute_model_analytics(self) -> Optional[List[ModelAnalytics]]:
        try:
            model_query = """
                SELECT 
                    model,
                    COUNT(*) as record_count,
                    SUM(token_count) as token_total,
                    SUM(CAST(success AS INT)) as success_count,
                    AVG(quality_score) as quality_avg,
                    COLLECT_SET(category) as categories_processed
                FROM analytics_data
                GROUP BY model
                ORDER BY model
            """
            
            results = self.spark.sql(model_query).collect()
            
            analytics = []
            for row in results:
                record_count = row['record_count']
                token_total = int(row['token_total']) if row['token_total'] else 0
                token_avg = token_total / record_count if record_count > 0 else 0
                success_count = int(row['success_count']) if row['success_count'] else 0
                failure_count = record_count - success_count
                success_rate = (success_count / record_count * 100) if record_count > 0 else 0
                quality_avg = float(row['quality_avg']) if row['quality_avg'] else 0
                
                categories = row['categories_processed'] or []
                
                analytics.append(ModelAnalytics(
                    model=row['model'],
                    record_count=record_count,
                    token_total=token_total,
                    token_average=round(token_avg, 2),
                    success_count=success_count,
                    failure_count=failure_count,
                    success_rate=round(success_rate, 2),
                    quality_score_average=round(quality_avg, 2),
                    categories_processed=categories
                ))
            
            self._results['models'] = [a.dict() for a in analytics]
            return analytics
        except Exception as e:
            print(f"Spark SQL model analytics error: {e}")
            return None
    
    def get_all_results(self) -> Dict[str, Any]:
        return self._results
