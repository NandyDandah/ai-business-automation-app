"""Compatibility entry point; always run the authenticated application."""

from app.main import app

__all__ = ["app"]

