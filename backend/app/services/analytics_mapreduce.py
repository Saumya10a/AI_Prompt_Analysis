from typing import Dict, Any, List, Callable, Tuple
from collections import defaultdict
from datetime import datetime
from ..models.schemas import OverviewStats, CategoryAnalytics, ModelAnalytics


class MapReduceAnalytics:
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data
        self._results: Dict[str, Any] = {}
    
    def _map_identity(self, record: Dict[str, Any]) -> List[Tuple[str, Any]]:
        return [('all', record)]
    
    def _reduce_count(self, values: List[Any]) -> int:
        return len(values)
    
    def _reduce_sum_tokens(self, values: List[Any]) -> int:
        return sum(v.get('token_count', 0) for v in values)
    
    def _reduce_avg_tokens(self, values: List[Any]) -> float:
        total = sum(v.get('token_count', 0) for v in values)
        return total / len(values) if values else 0
    
    def _reduce_sum_success(self, values: List[Any]) -> int:
        return sum(1 for v in values if v.get('success', False))
    
    def _reduce_avg_quality(self, values: List[Any]) -> float:
        total = sum(v.get('quality_score', 0) for v in values)
        return total / len(values) if values else 0
    
    def _reduce_distinct(self, values: List[Any], key: str) -> int:
        return len(set(v.get(key) for v in values))
    
    def _map_category(self, record: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
        category = record.get('category', 'unknown')
        return [(category, record)]
    
    def _map_model(self, record: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
        model = record.get('model', 'unknown')
        return [(model, record)]
    
    def _shuffle(self, mapped: List[Tuple[str, Any]]) -> Dict[str, List[Any]]:
        shuffled = defaultdict(list)
        for key, value in mapped:
            shuffled[key].append(value)
        return dict(shuffled)
    
    def _reduce(self, shuffled: Dict[str, List[Any]], reducer: Callable) -> Dict[str, Any]:
        return {key: reducer(values) for key, values in shuffled.items()}
    
    def compute_overview(self) -> OverviewStats:
        mapped = [item for record in self.data for item in self._map_identity(record)]
        shuffled = self._shuffle(mapped)
        
        total_records = self._reduce_count(shuffled['all'])
        total_tokens = self._reduce_sum_tokens(shuffled['all'])
        avg_tokens = self._reduce_avg_tokens(shuffled['all'])
        unique_categories = self._reduce_distinct(shuffled['all'], 'category')
        unique_models = self._reduce_distinct(shuffled['all'], 'model')
        success_count = self._reduce_sum_success(shuffled['all'])
        overall_success_rate = (success_count / total_records * 100) if total_records > 0 else 0
        overall_quality = self._reduce_avg_quality(shuffled['all'])
        
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
    
    def compute_category_analytics(self) -> List[CategoryAnalytics]:
        mapped = [item for record in self.data for item in self._map_category(record)]
        shuffled = self._shuffle(mapped)
        
        analytics = []
        for category, records in shuffled.items():
            record_count = len(records)
            token_total = sum(r.get('token_count', 0) for r in records)
            token_avg = token_total / record_count if record_count > 0 else 0
            success_count = sum(1 for r in records if r.get('success', False))
            failure_count = record_count - success_count
            success_rate = (success_count / record_count * 100) if record_count > 0 else 0
            quality_avg = sum(r.get('quality_score', 0) for r in records) / record_count if record_count > 0 else 0
            models_used = list(set(r.get('model', 'unknown') for r in records))
            
            analytics.append(CategoryAnalytics(
                category=category,
                record_count=record_count,
                token_total=token_total,
                token_average=round(token_avg, 2),
                success_count=success_count,
                failure_count=failure_count,
                success_rate=round(success_rate, 2),
                quality_score_average=round(quality_avg, 2),
                models_used=models_used
            ))
        
        self._results['categories'] = [a.dict() for a in analytics]
        return analytics
    
    def compute_model_analytics(self) -> List[ModelAnalytics]:
        mapped = [item for record in self.data for item in self._map_model(record)]
        shuffled = self._shuffle(mapped)
        
        analytics = []
        for model, records in shuffled.items():
            record_count = len(records)
            token_total = sum(r.get('token_count', 0) for r in records)
            token_avg = token_total / record_count if record_count > 0 else 0
            success_count = sum(1 for r in records if r.get('success', False))
            failure_count = record_count - success_count
            success_rate = (success_count / record_count * 100) if record_count > 0 else 0
            quality_avg = sum(r.get('quality_score', 0) for r in records) / record_count if record_count > 0 else 0
            categories_processed = list(set(r.get('category', 'unknown') for r in records))
            
            analytics.append(ModelAnalytics(
                model=model,
                record_count=record_count,
                token_total=token_total,
                token_average=round(token_avg, 2),
                success_count=success_count,
                failure_count=failure_count,
                success_rate=round(success_rate, 2),
                quality_score_average=round(quality_avg, 2),
                categories_processed=categories_processed
            ))
        
        self._results['models'] = [a.dict() for a in analytics]
        return analytics
    
    def get_all_results(self) -> Dict[str, Any]:
        return self._results
