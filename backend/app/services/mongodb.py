from typing import Optional, List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import settings


class MongoDBService:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
    
    async def connect(self):
        """Connect opportunistically; analytics remain available without MongoDB."""
        try:
            self.client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=1500)
            self.database = self.client[settings.mongodb_database]
            await self.client.admin.command('ping')
            await self._create_indexes()
        except Exception:
            if self.client:
                self.client.close()
            self.client = None
            self.database = None
    
    async def disconnect(self):
        if self.client:
            self.client.close()
        self.client = None
        self.database = None
    
    async def _create_indexes(self):
        collections = {
            'overview_stats': [('generated_at', -1)],
            'category_analytics': [('category', 1), ('generated_at', -1)],
            'model_analytics': [('model', 1), ('generated_at', -1)],
            'reconciliation_reports': [('engine_a', 1), ('engine_b', 1), ('timestamp', -1)],
            'system_status': [('last_checked', -1)]
        }
        
        for collection_name, indexes in collections.items():
            collection = self.database[collection_name]
            for index_field, direction in indexes:
                await collection.create_index([(index_field, direction)])
    
    async def store_overview_stats(self, stats: Dict[str, Any]) -> str:
        if self.database is None:
            return ""
        collection = self.database['overview_stats']
        result = await collection.insert_one(stats)
        return str(result.inserted_id)
    
    async def store_category_analytics(self, analytics: List[Dict[str, Any]]) -> List[str]:
        if self.database is None or not analytics:
            return []
        collection = self.database['category_analytics']
        result = await collection.insert_many(analytics)
        return [str(id) for id in result.inserted_ids]
    
    async def store_model_analytics(self, analytics: List[Dict[str, Any]]) -> List[str]:
        if self.database is None or not analytics:
            return []
        collection = self.database['model_analytics']
        result = await collection.insert_many(analytics)
        return [str(id) for id in result.inserted_ids]
    
    async def store_reconciliation_reports(self, reports: List[Dict[str, Any]]) -> List[str]:
        if self.database is None or not reports:
            return []
        collection = self.database['reconciliation_reports']
        result = await collection.insert_many(reports)
        return [str(id) for id in result.inserted_ids]
    
    async def store_system_status(self, status: Dict[str, Any]) -> str:
        if self.database is None:
            return ""
        collection = self.database['system_status']
        result = await collection.insert_one(status)
        return str(result.inserted_id)
    
    async def get_latest_overview_stats(self) -> Optional[Dict[str, Any]]:
        if self.database is None:
            return None
        collection = self.database['overview_stats']
        return await collection.find_one(sort=[('generated_at', -1)])
    
    async def get_latest_category_analytics(self) -> List[Dict[str, Any]]:
        if self.database is None:
            return []
        collection = self.database['category_analytics']
        latest = await collection.find_one(sort=[('generated_at', -1)])
        if not latest:
            return []
        
        timestamp = latest.get('generated_at')
        cursor = collection.find({'generated_at': timestamp})
        return await cursor.to_list(length=None)
    
    async def get_latest_model_analytics(self) -> List[Dict[str, Any]]:
        if self.database is None:
            return []
        collection = self.database['model_analytics']
        latest = await collection.find_one(sort=[('generated_at', -1)])
        if not latest:
            return []
        
        timestamp = latest.get('generated_at')
        cursor = collection.find({'generated_at': timestamp})
        return await cursor.to_list(length=None)
    
    async def get_latest_reconciliation_reports(self, limit: int = 100) -> List[Dict[str, Any]]:
        if self.database is None:
            return []
        collection = self.database['reconciliation_reports']
        cursor = collection.find(sort=[('timestamp', -1)]).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def get_latest_system_status(self) -> Optional[Dict[str, Any]]:
        if self.database is None:
            return None
        collection = self.database['system_status']
        return await collection.find_one(sort=[('last_checked', -1)])
    
    async def clear_collection(self, collection_name: str):
        if self.database is None:
            return
        if collection_name in self.database.list_collection_names():
            await self.database[collection_name].delete_many({})
    
    async def health_check(self) -> bool:
        try:
            if self.client is None:
                return False
            await self.client.admin.command('ping')
            return True
        except Exception:
            return False


mongodb_service = MongoDBService()
