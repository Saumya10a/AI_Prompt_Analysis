import pandas as pd
from typing import Dict, Any, List
from datetime import datetime
from ..models.schemas import OverviewStats, CategoryAnalytics, ModelAnalytics


class PythonBaselineAnalytics:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._results: Dict[str, Any] = {}
    
    def compute_overview(self) -> OverviewStats:
        total_records = len(self.df)
        total_tokens = self.df['token_count'].sum()
        avg_tokens = total_tokens / total_records if total_records > 0 else 0
        unique_categories = self.df['category'].nunique()
        unique_models = self.df['model'].nunique()
        
        success_count = self.df['success'].sum()
        overall_success_rate = (success_count / total_records * 100) if total_records > 0 else 0
        overall_quality = self.df['quality_score'].mean()
        
        stats = OverviewStats(
            total_records=total_records,
            total_tokens=int(total_tokens),
            average_tokens_per_record=round(avg_tokens, 2),
            unique_categories=unique_categories,
            unique_models=unique_models,
            overall_success_rate=round(overall_success_rate, 2),
            overall_quality_score=round(overall_quality, 2),
            generated_at=datetime.utcnow()
        )
        
        self._results['overview'] = stats.dict()
        return stats
    
    def compute_category_analytics(self) -> List[CategoryAnalytics]:
        category_groups = self.df.groupby('category')
        
        analytics = []
        for category, group in category_groups:
            record_count = len(group)
            token_total = group['token_count'].sum()
            token_avg = token_total / record_count if record_count > 0 else 0
            
            success_count = group['success'].sum()
            failure_count = record_count - success_count
            success_rate = (success_count / record_count * 100) if record_count > 0 else 0
            
            quality_avg = group['quality_score'].mean()
            models_used = group['model'].unique().tolist()
            
            analytics.append(CategoryAnalytics(
                category=category,
                record_count=record_count,
                token_total=int(token_total),
                token_average=round(token_avg, 2),
                success_count=int(success_count),
                failure_count=int(failure_count),
                success_rate=round(success_rate, 2),
                quality_score_average=round(quality_avg, 2),
                models_used=models_used
            ))
        
        self._results['categories'] = [a.dict() for a in analytics]
        return analytics
    
    def compute_model_analytics(self) -> List[ModelAnalytics]:
        model_groups = self.df.groupby('model')
        
        analytics = []
        for model, group in model_groups:
            record_count = len(group)
            token_total = group['token_count'].sum()
            token_avg = token_total / record_count if record_count > 0 else 0
            
            success_count = group['success'].sum()
            failure_count = record_count - success_count
            success_rate = (success_count / record_count * 100) if record_count > 0 else 0
            
            quality_avg = group['quality_score'].mean()
            categories_processed = group['category'].unique().tolist()
            
            analytics.append(ModelAnalytics(
                model=model,
                record_count=record_count,
                token_total=int(token_total),
                token_average=round(token_avg, 2),
                success_count=int(success_count),
                failure_count=int(failure_count),
                success_rate=round(success_rate, 2),
                quality_score_average=round(quality_avg, 2),
                categories_processed=categories_processed
            ))
        
        self._results['models'] = [a.dict() for a in analytics]
        return analytics
    
    def compute_time_series(self) -> List[Dict[str, Any]]:
        if 'timestamp' not in self.df.columns:
            return []
        
        df_with_time = self.df.dropna(subset=['timestamp']).copy()
        df_with_time['date'] = pd.to_datetime(df_with_time['timestamp']).dt.date
        
        time_groups = df_with_time.groupby('date')
        
        time_series = []
        for date, group in time_groups:
            time_series.append({
                'date': date.isoformat(),
                'record_count': len(group),
                'token_total': int(group['token_count'].sum()),
                'success_rate': round(group['success'].mean() * 100, 2),
                'quality_avg': round(group['quality_score'].mean(), 2)
            })
        
        time_series.sort(key=lambda x: x['date'])
        self._results['time_series'] = time_series
        return time_series
    
    def get_all_results(self) -> Dict[str, Any]:
        return self._results
