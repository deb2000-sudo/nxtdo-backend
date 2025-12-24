from .firebase import get_firestore_client
from .config import settings
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def get_collection_name(base_name: str) -> str:
    """Get environment-prefixed collection name to avoid data mixing"""
    env = settings.ENVIRONMENT
    if env == "production":
        return base_name  # No prefix for production
    return f"{env}_{base_name}"  # e.g., staging_tasks, development_tasks

class DatabaseService:
    def __init__(self):
        self._db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_firestore_client()
        return self._db
    
    def get_collection(self, collection_name: str):
        """Get collection with environment prefix"""
        prefixed_name = get_collection_name(collection_name)
        logger.debug(f"Accessing collection: {prefixed_name}")
        return self.db.collection(prefixed_name)
    
    def create_document(self, collection: str, data: Dict[str, Any], doc_id: Optional[str] = None) -> str:
        """Create a document"""
        try:
            # Add timestamps
            data["created_at"] = datetime.utcnow().isoformat()
            data["updated_at"] = datetime.utcnow().isoformat()
            
            collection_ref = self.get_collection(collection)
            
            if doc_id:
                collection_ref.document(doc_id).set(data)
                return doc_id
            else:
                _, doc_ref = collection_ref.add(data)
                return doc_ref.id
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            raise
    
    def get_document(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID"""
        try:
            doc = self.get_collection(collection).document(doc_id).get()
            if doc.exists:
                return {"id": doc.id, **doc.to_dict()}
            return None
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            raise
    
    def list_documents(self, collection: str, limit: int = 100) -> List[Dict[str, Any]]:
        """List documents in a collection"""
        try:
            docs = self.get_collection(collection).limit(limit).stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            raise
    
    def update_document(self, collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
        """Update a document"""
        try:
            data["updated_at"] = datetime.utcnow().isoformat()
            self.get_collection(collection).document(doc_id).update(data)
            return True
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            raise
    
    def delete_document(self, collection: str, doc_id: str) -> bool:
        """Delete a document"""
        try:
            self.get_collection(collection).document(doc_id).delete()
            return True
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise

# Global instance
db_service = DatabaseService()
