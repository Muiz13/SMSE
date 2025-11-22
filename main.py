"""
Root-level main.py for Railway/Heroku deployment compatibility.
This allows uvicorn to use 'main:app' instead of 'supervisor.main:app'
"""

# Import the app from supervisor.main
from supervisor.main import app

# Re-export for uvicorn
__all__ = ["app"]

