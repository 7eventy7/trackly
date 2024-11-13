import json
import os
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class JsonCache:
    def __init__(self, max_age: int = 300):  # 5 minutes default cache age
        self.cache: Dict[str, Any] = {}
        self.cache_times: Dict[str, float] = {}
        self.max_age = max_age
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key not in self.cache:
                return None
            
            if time.time() - self.cache_times[key] > self.max_age:
                del self.cache[key]
                del self.cache_times[key]
                return None
                
            return self.cache[key]

    def set(self, key: str, value: Any):
        with self.lock:
            self.cache[key] = value
            self.cache_times[key] = time.time()

    def invalidate(self, key: str):
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                del self.cache_times[key]

class JsonHandler:
    def __init__(self, file_path: str, max_retries: int = 3, retry_delay: float = 0.1):
        self.file_path = file_path
        self.lock = threading.Lock()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.cache = JsonCache()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Create file if it doesn't exist
        if not os.path.exists(file_path):
            self.write_json({})

    def with_retries(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            last_error = None
            for attempt in range(self.max_retries):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    last_error = e
                    time.sleep(self.retry_delay * (2 ** attempt))
            raise last_error
        return wrapper

    @with_retries
    def read_json(self) -> Dict:
        """Read JSON file with caching"""
        cached_data = self.cache.get(self.file_path)
        if cached_data is not None:
            return cached_data

        with self.lock:
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                self.cache.set(self.file_path, data)
                return data
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in {self.file_path}")
                return {}
            except Exception as e:
                logger.error(f"Error reading {self.file_path}: {str(e)}")
                raise

    @with_retries
    def write_json(self, data: Dict):
        """Write JSON file with proper locking"""
        with self.lock:
            try:
                with open(self.file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                self.cache.set(self.file_path, data)
            except Exception as e:
                logger.error(f"Error writing to {self.file_path}: {str(e)}")
                raise

    def update_json(self, update_func):
        """Update JSON file with a function that modifies the data"""
        with self.lock:
            data = self.read_json()
            updated_data = update_func(data)
            self.write_json(updated_data)
            return updated_data

class NotifiedAlbumsHandler(JsonHandler):
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self._ensure_structure()

    def _ensure_structure(self):
        """Ensure the JSON file has the correct structure"""
        data = self.read_json()
        if not isinstance(data, dict) or 'notified_albums' not in data:
            self.write_json({'notified_albums': []})

    def is_album_notified(self, artist: str, album: str) -> bool:
        """Check if an album has already been notified"""
        data = self.read_json()
        return any(
            n['artist'] == artist and n['album'] == album 
            for n in data.get('notified_albums', [])
        )

    def add_notified_album(self, artist: str, album: str, release_date: str):
        """Add an album to the notified albums list"""
        def update_func(data):
            if 'notified_albums' not in data:
                data['notified_albums'] = []
            
            data['notified_albums'].append({
                'artist': artist,
                'album': album,
                'release_date': release_date,
                'notified_at': datetime.now().isoformat()
            })
            return data

        self.update_json(update_func)

    def cleanup_old_notifications(self):
        """Clean up notifications from previous years"""
        def update_func(data):
            if 'notified_albums' not in data:
                return {'notified_albums': []}

            current_year = datetime.now().year
            data['notified_albums'] = [
                n for n in data['notified_albums']
                if datetime.fromisoformat(n['notified_at']).year >= current_year
            ]
            return data

        self.update_json(update_func)

class ArtistsConfigHandler(JsonHandler):
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self._ensure_structure()

    def _ensure_structure(self):
        """Ensure the JSON file has the correct structure"""
        data = self.read_json()
        if not isinstance(data, dict) or 'artists' not in data:
            self.write_json({
                'artists': [],
                'last_updated': datetime.now().isoformat()
            })

    def is_valid(self) -> bool:
        """Check if the artists config is valid and not stale"""
        try:
            data = self.read_json()
            if not isinstance(data, dict) or 'artists' not in data or 'last_updated' not in data:
                return False

            last_updated = datetime.fromisoformat(data['last_updated'])
            if (datetime.now() - last_updated).days > 7:  # Stale after 7 days
                return False

            return True
        except Exception:
            return False

    def update_artists(self, artists: list):
        """Update the artists list"""
        def update_func(data):
            data['artists'] = artists
            data['last_updated'] = datetime.now().isoformat()
            return data

        self.update_json(update_func)