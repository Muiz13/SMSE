"""
Shared utility functions for logging, configuration, and time handling.
"""

import os
import json
import logging
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import structlog


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file with environment variable overrides.
    
    Args:
        config_path: Path to config.yaml file. Defaults to shared/config.yaml
        
    Returns:
        Dictionary containing configuration values
    """
    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"
    
    config = {}
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f) or {}
    
    # Override with environment variables
    config.setdefault("supervisor", {})
    config.setdefault("agent", {})
    config.setdefault("ltm", {})
    
    config["supervisor"]["host"] = os.getenv("SUPERVISOR_HOST", config["supervisor"].get("host", "localhost"))
    config["supervisor"]["port"] = int(os.getenv("SUPERVISOR_PORT", config["supervisor"].get("port", 8000)))
    config["supervisor"]["base_url"] = os.getenv(
        "SUPERVISOR_BASE_URL",
        config["supervisor"].get("base_url", f"http://{config['supervisor']['host']}:{config['supervisor']['port']}")
    )
    
    config["agent"]["host"] = os.getenv("AGENT_HOST", config["agent"].get("host", "localhost"))
    config["agent"]["port"] = int(os.getenv("AGENT_PORT", config["agent"].get("port", 8001)))
    config["agent"]["base_url"] = os.getenv(
        "AGENT_BASE_URL",
        config["agent"].get("base_url", f"http://{config['agent']['host']}:{config['agent']['port']}")
    )
    
    config["ltm"]["type"] = os.getenv("LTM_TYPE", config["ltm"].get("type", "sqlite"))
    config["ltm"]["path"] = os.getenv("LTM_PATH", config["ltm"].get("path", "./ltm.db"))
    
    return config


def iso_now() -> str:
    """
    Get current UTC time in ISO 8601 format with Z suffix.
    
    Returns:
        ISO 8601 formatted timestamp string
    """
    return datetime.utcnow().isoformat() + "Z"


def log_json(message: str, **kwargs) -> None:
    """
    Log a structured JSON message.
    
    Args:
        message: Log message
        **kwargs: Additional structured fields
    """
    logger = structlog.get_logger()
    logger.info(message, **kwargs)


def setup_logging(level: str = "INFO", format_type: str = "json") -> None:
    """
    Configure structured logging.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        format_type: Output format ("json" or "text")
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(message)s" if format_type == "json" else "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    if format_type == "json":
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    else:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.dev.ConsoleRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )


def safe_json_loads(data: str) -> Optional[Dict[str, Any]]:
    """
    Safely parse JSON string, returning None on error.
    
    Args:
        data: JSON string to parse
        
    Returns:
        Parsed dictionary or None if parsing fails
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return None


def format_error_response(error: str, status_code: int = 400) -> Dict[str, Any]:
    """
    Format a standardized error response.
    
    Args:
        error: Error message
        status_code: HTTP status code
        
    Returns:
        Error response dictionary
    """
    return {
        "error": error,
        "status_code": status_code,
        "timestamp": iso_now()
    }

