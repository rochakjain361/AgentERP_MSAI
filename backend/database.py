"""Database configuration and connection management."""
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')

db = None
mongodb_available = False


class MockCollection:
    def __init__(self):
        self.data = []

    async def insert_one(self, doc):
        doc['_id'] = f"mock_{len(self.data)}"
        self.data.append(doc)
        return {"inserted_id": doc['_id']}

    async def find_one(self, query, projection=None):
        for item in self.data:
            if all(item.get(k) == v for k, v in query.items()):
                result = {k: v for k, v in item.items() if k != '_id'}
                return result
        return None

    async def find(self, query=None, projection=None, sort=None, limit=None):
        results = []
        for item in self.data:
            if query is None or all(item.get(k) == v for k, v in (query or {}).items()):
                result = {k: v for k, v in item.items() if k != '_id'}
                results.append(result)

        if sort:
            sort_field, sort_order = sort[0]
            results.sort(key=lambda x: x.get(sort_field, ''), reverse=(sort_order == -1))

        if limit:
            results = results[:limit]

        return results

    async def update_one(self, query, update_data):
        for i, item in enumerate(self.data):
            if all(item.get(k) == v for k, v in query.items()):
                if '$set' in update_data:
                    item.update(update_data['$set'])
                if '$inc' in update_data:
                    for k, v in update_data['$inc'].items():
                        item[k] = item.get(k, 0) + v
                return {"modified_count": 1}
        return {"modified_count": 0}

    async def delete_one(self, query):
        for i, item in enumerate(self.data):
            if all(item.get(k) == v for k, v in query.items()):
                del self.data[i]
                return {"deleted_count": 1}
        return {"deleted_count": 0}

    async def delete_many(self, query):
        original_len = len(self.data)
        self.data = [item for item in self.data if not all(item.get(k) == v for k, v in query.items())]
        return {"deleted_count": original_len - len(self.data)}

    async def count_documents(self, query=None):
        if query is None:
            return len(self.data)
        count = 0
        for item in self.data:
            if all(item.get(k) == v for k, v in query.items()):
                count += 1
        return count

    def to_list(self, length):
        return self.data[:length]


class MockDB:
    def __init__(self):
        self.chat_sessions = MockCollection()
        self.chat_messages = MockCollection()
        self.users = MockCollection()
        self.sales_orders = MockCollection()
        self.approval_requests = MockCollection()
        self.audit_logs = MockCollection()
        self.dashboard_metrics = MockCollection()

    def __getitem__(self, key):
        return getattr(self, key, MockCollection())


class LazyDB:
    def __init__(self):
        self._initialized = False
        self._db = None
        self._client = None

    def _initialize(self):
        global mongodb_available
        if self._initialized:
            return

        self._initialized = True
        try:
            self._client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
            self._client.admin.command('ping')
            self._db = self._client[os.environ.get('DB_NAME', 'agenterp')]
            mongodb_available = True
            logging.info('MongoDB connected successfully')
        except Exception as e:
            logging.warning(f'MongoDB not available, using in-memory fallback: {e}')
            self._db = MockDB()
            mongodb_available = False

    def __getattr__(self, name):
        self._initialize()
        return getattr(self._db, name)

    def __getitem__(self, key):
        self._initialize()
        return self._db[key]

    def close(self):
        if self._client:
            self._client.close()


db = LazyDB()

def close_db():
    if mongodb_available and hasattr(db, '_client'):
        db._client.close()


def is_mongodb_available():
    return mongodb_available
