import os
import sys


_spark_session = None


def get_spark_session(master: str, app_name: str):
    """Create one local Spark session and reuse it for reconciliation requests."""
    global _spark_session
    if _spark_session is None:
        # On Windows, Spark otherwise may resolve Python to the Store alias.
        os.environ["PYSPARK_PYTHON"] = sys.executable
        os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

        from pyspark.sql import SparkSession

        _spark_session = (
            SparkSession.builder.master(master)
            .appName(app_name)
            .config("spark.ui.enabled", "false")
            .config("spark.sql.shuffle.partitions", "4")
            .getOrCreate()
        )
        _spark_session.sparkContext.setLogLevel("ERROR")
    return _spark_session


def stop_spark_session() -> None:
    global _spark_session
    if _spark_session is not None:
        _spark_session.stop()
        _spark_session = None
