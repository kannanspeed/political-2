#!/usr/bin/env python3
"""
Test script for Political Events Platform
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_setup():
    """Test the application setup"""
    print("🧪 Testing Political Events Platform Setup")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Import required packages
    total_tests += 1
    try:
        import flask
        import flask_sqlalchemy
        import flask_login
        import flask_socketio
        import qrcode
        import werkzeug
        print("✅ Package imports successful")
        tests_passed += 1
    except ImportError as e:
        print(f"❌ Package import failed: {e}")
    
    # Test 2: Import app
    total_tests += 1
    try:
        from app import app, db, User, Event, EventRegistration, Ticket, Notification
        print("✅ App import successful")
        tests_passed += 1
    except ImportError as e:
        print(f"❌ App import failed: {e}")
    
    # Test 3: Database connection
    total_tests += 1
    try:
        with app.app_context():
            # Test database connection
            from sqlalchemy import text
            db.session.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            tests_passed += 1
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    # Test 4: Template files
    total_tests += 1
    required_templates = [
        'templates/base.html',
        'templates/index.html',
        'templates/login.html',
        'templates/signup.html',
        'templates/admin/dashboard.html',
        'templates/party/dashboard.html',
        'templates/user/dashboard.html'
    ]
    
    missing_templates = []
    for template in required_templates:
        if not os.path.exists(template):
            missing_templates.append(template)
    
    if not missing_templates:
        print("✅ All template files found")
        tests_passed += 1
    else:
        print(f"❌ Missing template files: {missing_templates}")
    
    # Test 5: User creation test
    total_tests += 1
    try:
        with app.app_context():
            from werkzeug.security import generate_password_hash
            
            # Test user creation
            test_user = User(
                email='test@example.com',
                password_hash=generate_password_hash('test123'),
                role='user'
            )
            db.session.add(test_user)
            db.session.commit()
            
            # Verify user was created
            created_user = User.query.filter_by(email='test@example.com').first()
            if created_user:
                print("✅ User creation test successful")
                tests_passed += 1
                
                # Clean up test user
                db.session.delete(created_user)
                db.session.commit()
            else:
                print("❌ User creation test failed")
    except Exception as e:
        print(f"❌ User creation test failed: {e}")
    
    # Summary
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Application is ready to run.")
        print("\n🚀 To start the application:")
        print("   python run.py")
        print("\n📱 Access the application at: http://localhost:5000")
        print("🔑 Default admin login: admin@political.com / admin123")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Common fixes:")
        print("   1. Install missing packages: pip install -r requirements.txt")
        print("   2. Initialize database: python init_db.py")
        print("   3. Check template files are in place")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    test_setup()
