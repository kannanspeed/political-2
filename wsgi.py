#!/usr/bin/env python3
"""
WSGI entry point for production deployment
This file tells Gunicorn how to run the Flask application
"""

from app_production import app

if __name__ == "__main__":
    app.run()
