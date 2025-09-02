#!/usr/bin/env python3
"""
Database initialization script for Political Events Platform
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_database():
    """Initialize the database and create tables"""
    print("🗄️ Initializing Political Events Database")
    print("=" * 40)
    
    try:
        # Import the app and database
        from app import app, db, User
        from werkzeug.security import generate_password_hash
        
        with app.app_context():
            # Create all tables
            print("📋 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Create admin user if not exists
            print("👑 Checking for admin user...")
            admin = User.query.filter_by(role='admin').first()
            if not admin:
                admin = User(
                    email='admin@political.com',
                    password_hash=generate_password_hash('admin123'),
                    role='admin'
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin user created successfully")
                print("   Email: admin@political.com")
                print("   Password: admin123")
            else:
                print("✅ Admin user already exists")
            
            print("\n🎉 Database initialization completed!")
            print("🚀 You can now run the application with: python run.py")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install all required packages:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()

