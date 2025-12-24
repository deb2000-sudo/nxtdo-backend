import firebase_admin
from firebase_admin import credentials, firestore
from .config import settings
import json
import logging

logger = logging.getLogger(__name__)

_firebase_app = None
_firestore_client = None

def get_firebase_app():
    """Initialize Firebase app (singleton)"""
    global _firebase_app
    
    if _firebase_app is not None:
        return _firebase_app
    
    if firebase_admin._apps:
        _firebase_app = firebase_admin.get_app()
        return _firebase_app
    
    firebase_config = settings.get_firebase_config()
    
    try:
        if settings.FIREBASE_SERVICE_ACCOUNT_KEY:
            try:
                # Try parsing as JSON string first
                service_account_info = json.loads(settings.FIREBASE_SERVICE_ACCOUNT_KEY)
                cred = credentials.Certificate(service_account_info)
                logger.info("Using service account key from environment variable")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in FIREBASE_SERVICE_ACCOUNT_KEY: {e}")
                raise ValueError("FIREBASE_SERVICE_ACCOUNT_KEY is not valid JSON")
        else:
            # Fallback to Application Default Credentials (works on GCP)
            cred = credentials.ApplicationDefault()
            logger.info("Using Application Default Credentials")
        
        _firebase_app = firebase_admin.initialize_app(cred, {
            'projectId': firebase_config['project_id'],
            'storageBucket': firebase_config['storage_bucket'],
            'databaseId': firebase_config.get('database_id', 'nxtdo-dev-db')
        })
        
        logger.info(f"Firebase initialized for project: {firebase_config['project_id']}")
        return _firebase_app
        
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise

def get_firestore_client():
    """Get Firestore client (singleton)"""
    global _firestore_client
    
    if _firestore_client is not None:
        return _firestore_client
    
    get_firebase_app()
    # For non-default databases, use the database parameter
    _firestore_client = firestore.client(database_id='nxtdo-dev-db')
    return _firestore_client