import json
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
import re
from ..models.schemas import PreprocessingMetadata


class DatasetIngestion:
    def __init__(self, dataset_path: str):
        self.dataset_path = Path(dataset_path)
        self.raw_data: List[Dict[str, Any]] = []
        self.processed_df: Optional[pd.DataFrame] = None
        self.metadata: Optional[PreprocessingMetadata] = None
    
    def _validate_record(self, record: Dict[str, Any]) -> bool:
        required_fields = ['prompt', 'response', 'model', 'category', 'timestamp']
        if not all(field in record for field in required_fields):
            return False
        
        if not isinstance(record['prompt'], str) or not record['prompt'].strip():
            return False
        
        if not isinstance(record['response'], str) or not record['response'].strip():
            return False
        
        return True
    
    def _clean_text(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def _standardize_timestamp(self, timestamp: Any) -> Optional[datetime]:
        if isinstance(timestamp, datetime):
            return timestamp
        if isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                try:
                    return pd.to_datetime(timestamp).to_pydatetime()
                except:
                    return None
        if isinstance(timestamp, (int, float)):
            try:
                return datetime.fromtimestamp(timestamp)
            except:
                return None
        return None
    
    def _count_tokens(self, text: str) -> int:
        if not isinstance(text, str):
            return 0
        return len(text.split())
    
    def _normalize_token_count(self, token_count: Any) -> int:
        if isinstance(token_count, int) and token_count >= 0:
            return token_count
        if isinstance(token_count, float):
            return int(token_count)
        return 0
    
    def _calculate_quality_score(self, record: Dict[str, Any]) -> float:
        score = 0.0
        
        prompt = record.get('prompt', '')
        response = record.get('response', '')
        
        if len(prompt) > 10:
            score += 0.2
        if len(response) > 10:
            score += 0.2
        
        if any(word in prompt.lower() for word in ['explain', 'describe', 'analyze', 'compare']):
            score += 0.2
        
        if 'error' not in response.lower() and 'failed' not in response.lower():
            score += 0.2
        
        if record.get('success', True):
            score += 0.2
        
        return min(score, 1.0)
    
    def load_dataset(self) -> bool:
        if not self.dataset_path.exists():
            return False
        
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            record = json.loads(line)
                            self.raw_data.append(record)
                        except json.JSONDecodeError:
                            continue
            return len(self.raw_data) > 0
        except Exception:
            return False
    
    def preprocess(self) -> PreprocessingMetadata:
        start_time = datetime.utcnow()
        
        valid_records = []
        malformed_count = 0
        fields_cleaned = 0
        
        for record in self.raw_data:
            if not self._validate_record(record):
                malformed_count += 1
                continue
            
            cleaned_record = record.copy()
            
            cleaned_record['prompt'] = self._clean_text(record['prompt'])
            fields_cleaned += 1
            
            cleaned_record['response'] = self._clean_text(record['response'])
            fields_cleaned += 1
            
            cleaned_record['category'] = self._clean_text(record.get('category', ''))
            fields_cleaned += 1
            
            cleaned_record['model'] = self._clean_text(record.get('model', ''))
            fields_cleaned += 1
            
            cleaned_record['timestamp'] = self._standardize_timestamp(record.get('timestamp'))
            if cleaned_record['timestamp']:
                fields_cleaned += 1
            
            cleaned_record['token_count'] = self._normalize_token_count(
                record.get('token_count', self._count_tokens(cleaned_record['prompt'] + cleaned_record['response']))
            )
            fields_cleaned += 1
            
            cleaned_record['success'] = bool(record.get('success', True))
            
            cleaned_record['quality_score'] = self._calculate_quality_score(cleaned_record)
            
            valid_records.append(cleaned_record)
        
        self.processed_df = pd.DataFrame(valid_records)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        self.metadata = PreprocessingMetadata(
            total_records_ingested=len(valid_records),
            malformed_rows_dropped=malformed_count,
            fields_cleaned=fields_cleaned,
            processing_time_seconds=processing_time
        )
        
        return self.metadata
    
    def get_processed_dataframe(self) -> pd.DataFrame:
        if self.processed_df is None:
            raise ValueError("Dataset must be preprocessed first")
        return self.processed_df
    
    def get_metadata(self) -> PreprocessingMetadata:
        if self.metadata is None:
            raise ValueError("Dataset must be preprocessed first")
        return self.metadata
