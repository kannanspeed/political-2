#!/usr/bin/env python3
"""
Quick Start Script for Political Events App
Run this script to start the application locally
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import flask_sqlalchemy
        import flask_login
        import flask_socketio
        import qrcode
        import pillow
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_database():
    """Check if database exists and initialize if needed"""
    if not os.path.exists('instance/political_events.db'):
        print("📊 Database not found, initializing...")
        try:
            import init_db
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize database: {e}")
            return False
    else:
        print("✅ Database exists")
    return True

def start_app():
    """Start the Flask application"""
    print("🚀 Starting Political Events App...")
    print("📍 Local URL: http://localhost:5000")
    print("🔑 Admin Login: admin@political.com / admin123")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        # Set development environment
        os.environ['FLASK_ENV'] = 'development'
        os.environ['FLASK_DEBUG'] = '1'
        
        # Import and run the app
        from app import app, socketio
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🏛️  Political Events Management System")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check database
    if not check_database():
        sys.exit(1)
    
    # Start application
    start_app()

if __name__ == "__main__":
    main()
