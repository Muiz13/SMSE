"""
Tests for Long-Term Memory (LTM) implementation.
"""

import pytest
import os
from pathlib import Path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ltm import LTM


@pytest.fixture
def file_ltm():
    """Create a file-based LTM for testing."""
    test_path = "./test_ltm_file.json"
    ltm = LTM(backend_type="file", path=test_path, ttl_days=30)
    yield ltm
    # Cleanup
    if Path(test_path).exists():
        os.remove(test_path)


@pytest.fixture
def sqlite_ltm():
    """Create a SQLite-based LTM for testing."""
    test_path = "./test_ltm_sqlite.db"
    ltm = LTM(backend_type="sqlite", path=test_path, ttl_days=30)
    yield ltm
    # Cleanup
    ltm.close()
    if Path(test_path).exists():
        os.remove(test_path)


def test_ltm_write_read_file(file_ltm):
    """Test write and read operations for file-based LTM."""
    key = "test:key:123"
    value = {"data": "test_value", "timestamp": "2025-11-22T18:00:00Z"}
    
    assert file_ltm.write(key, value) == True
    result = file_ltm.read(key)
    
    assert result is not None
    assert result["data"] == "test_value"


def test_ltm_write_read_sqlite(sqlite_ltm):
    """Test write and read operations for SQLite-based LTM."""
    key = "test:key:456"
    value = {"data": "test_value_sqlite", "timestamp": "2025-11-22T18:00:00Z"}
    
    assert sqlite_ltm.write(key, value) == True
    result = sqlite_ltm.read(key)
    
    assert result is not None
    assert result["data"] == "test_value_sqlite"


def test_ltm_query_prefix(file_ltm):
    """Test prefix query functionality."""
    file_ltm.write("analysis:building-a:2025-11-22", {"result": "data1"})
    file_ltm.write("analysis:building-b:2025-11-22", {"result": "data2"})
    file_ltm.write("forecast:building-a:2025-11-22", {"result": "data3"})
    
    results = file_ltm.query("analysis:")
    
    assert len(results) == 2
    assert all("analysis:" in r["key"] for r in results)


def test_ltm_nonexistent_key(file_ltm):
    """Test reading non-existent key."""
    result = file_ltm.read("nonexistent:key")
    assert result is None


def test_ltm_compact(file_ltm):
    """Test LTM compaction (removing expired entries)."""
    # Write some entries
    file_ltm.write("key1", {"data": "value1"})
    file_ltm.write("key2", {"data": "value2"})
    
    # Compact should return number of removed entries (0 if none expired)
    removed = file_ltm.compact()
    assert isinstance(removed, int)
    assert removed >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

