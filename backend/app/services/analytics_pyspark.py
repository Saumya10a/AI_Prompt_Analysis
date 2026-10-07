from datetime import datetime
from typing import Any, Dict, List, Optional

from ..models.schemas import CategoryAnalytics, ModelAnalytics, OverviewStats


class PySparkAnalytics:
    """Aggregations using the PySpark DataFrame API on a Spark DataFrame."""

    def __init__(self, spark_session, df):
        self.spark = spark_session
        self.df = df
        self._results: Dict[str, Any] = {}

    def compute_overview(self) -> Optional[OverviewStats]:
        try:
            from pyspark.sql import functions as F

            row = self.df.agg(
                F.count("*").alias("total_records"),
                F.sum("token_count").alias("total_tokens"),
                F.avg("token_count").alias("avg_tokens"),
                F.countDistinct("category").alias("unique_categories"),
                F.countDistinct("model").alias("unique_models"),
                F.sum(F.col("success").cast("int")).alias("success_count"),
                F.avg("quality_score").alias("overall_quality"),
            ).first()
            total_records = int(row["total_records"] or 0)
            success_count = int(row["success_count"] or 0)
            stats = OverviewStats(
                total_records=total_records,
                total_tokens=int(row["total_tokens"] or 0),
                average_tokens_per_record=round(float(row["avg_tokens"] or 0), 2),
                unique_categories=int(row["unique_categories"] or 0),
                unique_models=int(row["unique_models"] or 0),
                overall_success_rate=round(success_count / total_records * 100, 2) if total_records else 0,
                overall_quality_score=round(float(row["overall_quality"] or 0), 2),
                generated_at=datetime.utcnow(),
            )
            self._results["overview"] = stats.dict()
            return stats
        except Exception as exc:
            print(f"PySpark overview computation error: {exc}")
            return None

    def compute_category_analytics(self) -> Optional[List[CategoryAnalytics]]:
        try:
            from pyspark.sql import functions as F

            rows = self.df.groupBy("category").agg(
                F.count("*").alias("record_count"),
                F.sum("token_count").alias("token_total"),
                F.sum(F.col("success").cast("int")).alias("success_count"),
                F.avg("quality_score").alias("quality_average"),
                F.collect_set("model").alias("models_used"),
            ).collect()
            results = []
            for row in rows:
                count = int(row["record_count"])
                tokens = int(row["token_total"] or 0)
                successes = int(row["success_count"] or 0)
                results.append(CategoryAnalytics(
                    category=row["category"], record_count=count, token_total=tokens,
                    token_average=round(tokens / count, 2) if count else 0,
                    success_count=successes, failure_count=count - successes,
                    success_rate=round(successes / count * 100, 2) if count else 0,
                    quality_score_average=round(float(row["quality_average"] or 0), 2),
                    models_used=list(row["models_used"] or []),
                ))
            self._results["categories"] = [item.dict() for item in results]
            return results
        except Exception as exc:
            print(f"PySpark category analytics error: {exc}")
            return None

    def compute_model_analytics(self) -> Optional[List[ModelAnalytics]]:
        try:
            from pyspark.sql import functions as F

            rows = self.df.groupBy("model").agg(
                F.count("*").alias("record_count"),
                F.sum("token_count").alias("token_total"),
                F.sum(F.col("success").cast("int")).alias("success_count"),
                F.avg("quality_score").alias("quality_average"),
                F.collect_set("category").alias("categories_processed"),
            ).collect()
            results = []
            for row in rows:
                count = int(row["record_count"])
                tokens = int(row["token_total"] or 0)
                successes = int(row["success_count"] or 0)
                results.append(ModelAnalytics(
                    model=row["model"], record_count=count, token_total=tokens,
                    token_average=round(tokens / count, 2) if count else 0,
                    success_count=successes, failure_count=count - successes,
                    success_rate=round(successes / count * 100, 2) if count else 0,
                    quality_score_average=round(float(row["quality_average"] or 0), 2),
                    categories_processed=list(row["categories_processed"] or []),
                ))
            self._results["models"] = [item.dict() for item in results]
            return results
        except Exception as exc:
            print(f"PySpark model analytics error: {exc}")
            return None

    def get_all_results(self) -> Dict[str, Any]:
        return self._results
