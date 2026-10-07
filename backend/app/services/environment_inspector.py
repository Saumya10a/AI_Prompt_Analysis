import subprocess
import sys
from typing import Dict, Optional
from datetime import datetime
from ..models.enums import EngineStatus, EngineType
from ..models.schemas import EngineStatusInfo


class EnvironmentInspector:
    def __init__(self):
        self._cache: Dict[EngineType, EngineStatusInfo] = {}
    
    def _run_command(self, command: list) -> tuple[bool, str]:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0, result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, ""
    
    def _get_python_version(self) -> Optional[str]:
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def _check_pyspark(self) -> tuple[EngineStatus, str, Optional[str]]:
        try:
            import pyspark
            version = pyspark.__version__
            return EngineStatus.AVAILABLE, "PySpark installed and importable", version
        except ImportError:
            return EngineStatus.NOT_INSTALLED, "PySpark not installed", None
    
    def _check_spark_sql(self) -> tuple[EngineStatus, str, Optional[str]]:
        try:
            from pyspark.sql import SparkSession
            spark_available, _, spark_version = self._check_pyspark()
            if spark_available != EngineStatus.AVAILABLE:
                return spark_available, "Depends on PySpark availability", None
            return EngineStatus.AVAILABLE, "Spark SQL available via PySpark", spark_version
        except ImportError:
            return EngineStatus.NOT_INSTALLED, "Spark SQL not available", None
    
    def _check_mongodb(self) -> tuple[EngineStatus, str, Optional[str]]:
        success, output = self._run_command(["mongod", "--version"])
        if success:
            version = output.split()[1] if len(output.split()) > 1 else "unknown"
            return EngineStatus.AVAILABLE, "MongoDB binary found", version
        return EngineStatus.NOT_INSTALLED, "MongoDB binary not found in PATH", None
    
    def _check_hadoop(self) -> tuple[EngineStatus, str, Optional[str]]:
        success, output = self._run_command(["hadoop", "version"])
        if success:
            version = output.split()[1] if len(output.split()) > 1 else "unknown"
            return EngineStatus.AVAILABLE, "Hadoop installed", version
        return EngineStatus.NOT_INSTALLED, "Hadoop not installed", None
    
    def _check_hive(self) -> tuple[EngineStatus, str, Optional[str]]:
        success, output = self._run_command(["hive", "--version"])
        if success:
            version = output.split()[1] if len(output.split()) > 1 else "unknown"
            return EngineStatus.AVAILABLE, "Hive installed", version
        return EngineStatus.NOT_INSTALLED, "Hive not installed", None
    
    def _check_pig(self) -> tuple[EngineStatus, str, Optional[str]]:
        success, output = self._run_command(["pig", "-version"])
        if success:
            version = output.split()[1] if len(output.split()) > 1 else "unknown"
            return EngineStatus.AVAILABLE, "Pig installed", version
        return EngineStatus.NOT_INSTALLED, "Pig not installed", None
    
    def _check_sqoop(self) -> tuple[EngineStatus, str, Optional[str]]:
        success, output = self._run_command(["sqoop", "--version"])
        if success:
            version = output.split()[1] if len(output.split()) > 1 else "unknown"
            return EngineStatus.AVAILABLE, "Sqoop installed", version
        return EngineStatus.NOT_INSTALLED, "Sqoop not installed", None
    
    def inspect_engine(self, engine_type: EngineType) -> EngineStatusInfo:
        if engine_type in self._cache:
            return self._cache[engine_type]
        
        checkers = {
            EngineType.PYTHON_BASELINE: lambda: (EngineStatus.AVAILABLE, "Python runtime available", self._get_python_version()),
            EngineType.PYSPARK: self._check_pyspark,
            EngineType.SPARK_SQL: self._check_spark_sql,
            EngineType.MAPREDUCE: lambda: (EngineStatus.VALIDATED_LOCALLY, "MapReduce-style local implementation available", None),
            EngineType.MONGODB: self._check_mongodb,
            EngineType.HADOOP: self._check_hadoop,
            EngineType.HIVE: self._check_hive,
            EngineType.PIG: self._check_pig,
            EngineType.SQOOP: self._check_sqoop,
        }
        
        status, description, version = checkers[engine_type]()
        
        info = EngineStatusInfo(
            engine_type=engine_type,
            status=status,
            description=description,
            version=version,
            last_checked=datetime.utcnow()
        )
        
        self._cache[engine_type] = info
        return info
    
    def inspect_all(self) -> list[EngineStatusInfo]:
        return [self.inspect_engine(engine) for engine in EngineType]
