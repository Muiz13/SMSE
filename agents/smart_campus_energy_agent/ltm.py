"""
Long-Term Memory (LTM) implementation for agent task result caching.

Supports SQLite backend with automatic fallback to file-based JSON storage.
"""

import json
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import os

logger = logging.getLogger(__name__)


class LTM:
    """
    Long-Term Memory storage for agent task results.
    
    Supports SQLite (primary) and JSON file (fallback) backends.
    """
    
    def __init__(self, backend_type: str = "sqlite", path: str = "./ltm.db", ttl_days: int = 30):
        """
        Initialize LTM storage.
        
        Args:
            backend_type: "sqlite" or "file"
            path: Path to storage file (SQLite DB or JSON file)
            ttl_days: Time-to-live in days for entries
        """
        self.backend_type = backend_type
        self.path = path
        self.ttl_days = ttl_days
        self.logger = logging.getLogger(f"{__name__}.{backend_type}")
        
        if backend_type == "sqlite":
            self._init_sqlite()
        else:
            self._init_file()
    
    def _init_sqlite(self) -> None:
        """Initialize SQLite database."""
        try:
            self.conn = sqlite3.connect(self.path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ltm_entries (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at ON ltm_entries(created_at)
            """)
            
            self.conn.commit()
            self.logger.info(f"SQLite LTM initialized at {self.path}")
            
        except Exception as e:
            self.logger.warning(f"SQLite initialization failed: {e}, falling back to file storage")
            self.backend_type = "file"
            self.path = self.path.replace(".db", ".json")
            self._init_file()
    
    def _init_file(self) -> None:
        """Initialize file-based JSON storage."""
        self.data: Dict[str, Dict[str, Any]] = {}
        self.file_path = Path(self.path)
        
        # Load existing data if file exists
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r') as f:
                    self.data = json.load(f)
                self.logger.info(f"File LTM loaded from {self.path}")
            except Exception as e:
                self.logger.warning(f"Failed to load LTM file: {e}, starting fresh")
                self.data = {}
        else:
            # Create directory if needed
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"File LTM initialized at {self.path}")
    
    def write(self, key: str, value: Dict[str, Any]) -> bool:
        """
        Write a value to LTM.
        
        Args:
            key: Storage key
            value: Value to store (must be JSON-serializable)
            
        Returns:
            True if successful
        """
        try:
            timestamp = datetime.utcnow().isoformat() + "Z"
            
            if self.backend_type == "sqlite":
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO ltm_entries (key, value, created_at, updated_at)
                    VALUES (?, ?, COALESCE((SELECT created_at FROM ltm_entries WHERE key = ?), ?), ?)
                """, (key, json.dumps(value), key, timestamp, timestamp))
                self.conn.commit()
            else:
                self.data[key] = {
                    "value": value,
                    "created_at": timestamp,
                    "updated_at": timestamp
                }
                self._save_file()
            
            self.logger.debug(f"LTM write: {key}")
            return True
            
        except Exception as e:
            self.logger.error(f"LTM write failed for key {key}: {e}", exc_info=True)
            return False
    
    def read(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Read a value from LTM.
        
        Args:
            key: Storage key
            
        Returns:
            Stored value or None if not found or expired
        """
        try:
            if self.backend_type == "sqlite":
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT value, created_at FROM ltm_entries WHERE key = ?
                """, (key,))
                row = cursor.fetchone()
                
                if row is None:
                    return None
                
                created_at = datetime.fromisoformat(row[1].replace("Z", "+00:00"))
                if datetime.utcnow() - created_at.replace(tzinfo=None) > timedelta(days=self.ttl_days):
                    # Expired, delete and return None
                    cursor.execute("DELETE FROM ltm_entries WHERE key = ?", (key,))
                    self.conn.commit()
                    return None
                
                return json.loads(row[0])
            else:
                if key not in self.data:
                    return None
                
                entry = self.data[key]
                created_at = datetime.fromisoformat(entry["created_at"].replace("Z", "+00:00"))
                if datetime.utcnow() - created_at.replace(tzinfo=None) > timedelta(days=self.ttl_days):
                    # Expired, delete and return None
                    del self.data[key]
                    self._save_file()
                    return None
                
                return entry["value"]
                
        except Exception as e:
            self.logger.error(f"LTM read failed for key {key}: {e}", exc_info=True)
            return None
    
    def query(self, prefix: str) -> List[Dict[str, Any]]:
        """
        Query LTM entries by key prefix.
        
        Args:
            prefix: Key prefix to match
            
        Returns:
            List of matching entries (key-value pairs)
        """
        try:
            results = []
            
            if self.backend_type == "sqlite":
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT key, value, created_at FROM ltm_entries
                    WHERE key LIKE ? AND
                    datetime(created_at) > datetime('now', '-' || ? || ' days')
                """, (f"{prefix}%", self.ttl_days))
                
                for row in cursor.fetchall():
                    created_at = datetime.fromisoformat(row[2].replace("Z", "+00:00"))
                    if datetime.utcnow() - created_at.replace(tzinfo=None) <= timedelta(days=self.ttl_days):
                        results.append({
                            "key": row[0],
                            "value": json.loads(row[1])
                        })
            else:
                cutoff = datetime.utcnow() - timedelta(days=self.ttl_days)
                for key, entry in self.data.items():
                    if key.startswith(prefix):
                        created_at = datetime.fromisoformat(entry["created_at"].replace("Z", "+00:00"))
                        if created_at.replace(tzinfo=None) > cutoff:
                            results.append({
                                "key": key,
                                "value": entry["value"]
                            })
            
            return results
            
        except Exception as e:
            self.logger.error(f"LTM query failed for prefix {prefix}: {e}", exc_info=True)
            return []
    
    def compact(self) -> int:
        """
        Remove expired entries from LTM.
        
        Returns:
            Number of entries removed
        """
        try:
            removed = 0
            cutoff = datetime.utcnow() - timedelta(days=self.ttl_days)
            
            if self.backend_type == "sqlite":
                cursor = self.conn.cursor()
                cursor.execute("""
                    DELETE FROM ltm_entries
                    WHERE datetime(created_at) < datetime('now', '-' || ? || ' days')
                """, (self.ttl_days,))
                removed = cursor.rowcount
                self.conn.commit()
            else:
                keys_to_delete = []
                for key, entry in self.data.items():
                    created_at = datetime.fromisoformat(entry["created_at"].replace("Z", "+00:00"))
                    if created_at.replace(tzinfo=None) < cutoff:
                        keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    del self.data[key]
                    removed += 1
                
                if removed > 0:
                    self._save_file()
            
            self.logger.info(f"LTM compacted: {removed} expired entries removed")
            return removed
            
        except Exception as e:
            self.logger.error(f"LTM compact failed: {e}", exc_info=True)
            return 0
    
    def _save_file(self) -> None:
        """Save file-based LTM to disk."""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save LTM file: {e}", exc_info=True)
    
    def close(self) -> None:
        """Close LTM connections and save data."""
        if self.backend_type == "sqlite":
            if hasattr(self, 'conn'):
                self.conn.close()
        else:
            self._save_file()

