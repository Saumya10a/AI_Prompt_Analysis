from typing import Dict, Any, List, Optional
from datetime import datetime
from ..models.schemas import ReconciliationReport


class ReconciliationEngine:
    def __init__(self):
        self._reports: List[ReconciliationReport] = []
    
    def _compare_values(self, value_a: Any, value_b: Any) -> tuple[bool, float, Optional[float]]:
        try:
            float_a = float(value_a)
            float_b = float(value_b)
            
            absolute_delta = abs(float_a - float_b)
            match_status = absolute_delta < 0.01
            
            if float_b != 0:
                percentage_delta = (absolute_delta / abs(float_b)) * 100
            elif float_a != 0:
                percentage_delta = (absolute_delta / abs(float_a)) * 100
            else:
                percentage_delta = 0.0
            
            return match_status, round(absolute_delta, 4), round(percentage_delta, 2)
        except (ValueError, TypeError):
            match_status = value_a == value_b
            return match_status, 0.0, 0.0
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '') -> Dict[str, Any]:
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key).items())
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        items.extend(self._flatten_dict(item, f"{new_key}[{i}]").items())
                    else:
                        items.append((f"{new_key}[{i}]", item))
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _extract_numeric_metrics(self, results: Dict[str, Any]) -> Dict[str, float]:
        flattened = self._flatten_dict(results)
        numeric_metrics = {}
        
        for key, value in flattened.items():
            try:
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    numeric_metrics[key] = float(value)
            except (ValueError, TypeError):
                continue
        
        return numeric_metrics
    
    def _compare_overview_metrics(self, results_a: Dict[str, Any], results_b: Dict[str, Any], 
                                  engine_a: str, engine_b: str) -> List[ReconciliationReport]:
        reports = []
        
        overview_a = results_a.get('overview', {})
        overview_b = results_b.get('overview', {})
        
        metrics_to_compare = [
            'total_records', 'total_tokens', 'average_tokens_per_record',
            'unique_categories', 'unique_models', 'overall_success_rate', 'overall_quality_score'
        ]
        
        for metric in metrics_to_compare:
            if metric in overview_a and metric in overview_b:
                match_status, abs_delta, pct_delta = self._compare_values(
                    overview_a[metric], overview_b[metric]
                )
                
                reports.append(ReconciliationReport(
                    engine_a=engine_a,
                    engine_b=engine_b,
                    metric_name=f"overview.{metric}",
                    value_a=float(overview_a[metric]),
                    value_b=float(overview_b[metric]),
                    match_status=match_status,
                    absolute_delta=abs_delta,
                    percentage_delta=pct_delta,
                    timestamp=datetime.utcnow()
                ))
        
        return reports
    
    def _compare_category_metrics(self, results_a: Dict[str, Any], results_b: Dict[str, Any],
                                  engine_a: str, engine_b: str) -> List[ReconciliationReport]:
        reports = []
        
        categories_a = results_a.get('categories', [])
        categories_b = results_b.get('categories', [])
        
        categories_dict_a = {c['category']: c for c in categories_a}
        categories_dict_b = {c['category']: c for c in categories_b}
        
        all_categories = set(categories_dict_a.keys()) | set(categories_dict_b.keys())
        
        for category in all_categories:
            cat_a = categories_dict_a.get(category, {})
            cat_b = categories_dict_b.get(category, {})
            
            metrics_to_compare = [
                'record_count', 'token_total', 'token_average',
                'success_count', 'failure_count', 'success_rate', 'quality_score_average'
            ]
            
            for metric in metrics_to_compare:
                if metric in cat_a and metric in cat_b:
                    match_status, abs_delta, pct_delta = self._compare_values(
                        cat_a[metric], cat_b[metric]
                    )
                    
                    reports.append(ReconciliationReport(
                        engine_a=engine_a,
                        engine_b=engine_b,
                        metric_name=f"category.{category}.{metric}",
                        value_a=float(cat_a[metric]),
                        value_b=float(cat_b[metric]),
                        match_status=match_status,
                        absolute_delta=abs_delta,
                        percentage_delta=pct_delta,
                        timestamp=datetime.utcnow()
                    ))
        
        return reports
    
    def _compare_model_metrics(self, results_a: Dict[str, Any], results_b: Dict[str, Any],
                               engine_a: str, engine_b: str) -> List[ReconciliationReport]:
        reports = []
        
        models_a = results_a.get('models', [])
        models_b = results_b.get('models', [])
        
        models_dict_a = {m['model']: m for m in models_a}
        models_dict_b = {m['model']: m for m in models_b}
        
        all_models = set(models_dict_a.keys()) | set(models_dict_b.keys())
        
        for model in all_models:
            mod_a = models_dict_a.get(model, {})
            mod_b = models_dict_b.get(model, {})
            
            metrics_to_compare = [
                'record_count', 'token_total', 'token_average',
                'success_count', 'failure_count', 'success_rate', 'quality_score_average'
            ]
            
            for metric in metrics_to_compare:
                if metric in mod_a and metric in mod_b:
                    match_status, abs_delta, pct_delta = self._compare_values(
                        mod_a[metric], mod_b[metric]
                    )
                    
                    reports.append(ReconciliationReport(
                        engine_a=engine_a,
                        engine_b=engine_b,
                        metric_name=f"model.{model}.{metric}",
                        value_a=float(mod_a[metric]),
                        value_b=float(mod_b[metric]),
                        match_status=match_status,
                        absolute_delta=abs_delta,
                        percentage_delta=pct_delta,
                        timestamp=datetime.utcnow()
                    ))
        
        return reports
    
    def compare_engines(self, results_a: Dict[str, Any], results_b: Dict[str, Any],
                        engine_a: str, engine_b: str) -> List[ReconciliationReport]:
        reports = []
        
        reports.extend(self._compare_overview_metrics(results_a, results_b, engine_a, engine_b))
        reports.extend(self._compare_category_metrics(results_a, results_b, engine_a, engine_b))
        reports.extend(self._compare_model_metrics(results_a, results_b, engine_a, engine_b))
        
        self._reports.extend(reports)
        return reports
    
    def get_mismatches(self, threshold: float = 0.01) -> List[ReconciliationReport]:
        return [r for r in self._reports if not r.match_status and r.absolute_delta >= threshold]
    
    def get_all_reports(self) -> List[ReconciliationReport]:
        return self._reports
    
    def calculate_match_rate(self) -> float:
        if not self._reports:
            return 0.0
        matched = sum(1 for r in self._reports if r.match_status)
        return (matched / len(self._reports)) * 100
