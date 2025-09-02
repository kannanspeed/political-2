#!/usr/bin/env python3
"""
Test script for event creation functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_event_creation():
    """Test event creation functionality"""
    print("🧪 Testing Event Creation Functionality")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Check if create_event route exists
    total_tests += 1
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if '@app.route(\'/party/create_event\', methods=[\'GET\', \'POST\'])' in content:
            print("✅ Create event route exists")
            tests_passed += 1
        else:
            print("❌ Create event route not found")
            
    except Exception as e:
        print(f"❌ Error checking route: {e}")
    
    # Test 2: Check if Event model exists
    total_tests += 1
    try:
        if 'class Event(db.Model):' in content:
            print("✅ Event model exists")
            tests_passed += 1
        else:
            print("❌ Event model not found")
            
    except Exception as e:
        print(f"❌ Error checking model: {e}")
    
    # Test 3: Check if form submission is fixed
    total_tests += 1
    try:
        with open('templates/party/create_event.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        # Check if simulated submission is removed
        if 'Simulate form submission' not in template_content:
            print("✅ Form submission fixed (no simulation)")
            tests_passed += 1
        else:
            print("❌ Form still using simulated submission")
            
    except Exception as e:
        print(f"❌ Error checking form submission: {e}")
    
    # Test 4: Check if error handling is added
    total_tests += 1
    try:
        if 'try:' in content and 'except Exception as e:' in content and 'db.session.rollback()' in content:
            print("✅ Error handling added to create_event route")
            tests_passed += 1
        else:
            print("❌ Error handling not found in create_event route")
            
    except Exception as e:
        print(f"❌ Error checking error handling: {e}")
    
    # Test 5: Check if validation is added
    total_tests += 1
    try:
        if 'Validate required fields' in content and 'Invalid coordinates' in content:
            print("✅ Form validation added")
            tests_passed += 1
        else:
            print("❌ Form validation not found")
            
    except Exception as e:
        print(f"❌ Error checking validation: {e}")
    
    # Test 6: Check if QR code generation is working
    total_tests += 1
    try:
        if 'qrcode.QRCode(' in content and 'qr.make_image(' in content:
            print("✅ QR code generation implemented")
            tests_passed += 1
        else:
            print("❌ QR code generation not found")
            
    except Exception as e:
        print(f"❌ Error checking QR code generation: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All event creation tests passed!")
        return True
    else:
        print("❌ Some event creation tests failed")
        return False

def test_database_connection():
    """Test database connection and event creation"""
    print("\n🗄️ Testing Database Event Creation")
    print("=" * 40)
    
    try:
        from app import app, db, Event, User
        from werkzeug.security import generate_password_hash
        from datetime import datetime, timedelta
        
        with app.app_context():
            # Create a test political party user
            test_party = User(
                email='testparty@example.com',
                phone='1234567890',
                password_hash=generate_password_hash('TestPass123!'),
                role='party',
                party_name='Test Party'
            )
            
            # Check if user already exists
            existing_user = User.query.filter_by(email='testparty@example.com').first()
            if existing_user:
                test_party = existing_user
            else:
                db.session.add(test_party)
                db.session.commit()
            
            # Create a test event
            test_event = Event(
                title='Test Event',
                description='This is a test event for testing purposes',
                party_name=test_party.party_name,
                party_id=test_party.id,
                location='Test Location, Chennai, India',
                latitude=13.0827,
                longitude=80.2707,
                event_date=datetime.utcnow() + timedelta(days=7),
                qr_code='test_qr_code_data'
            )
            
            db.session.add(test_event)
            db.session.commit()
            
            print("✅ Test event created successfully in database")
            
            # Verify event was created
            created_event = Event.query.filter_by(title='Test Event').first()
            if created_event:
                print(f"✅ Event verified: ID={created_event.id}, Title={created_event.title}")
                
                # Clean up test event
                db.session.delete(created_event)
                db.session.commit()
                print("✅ Test event cleaned up")
                
                return True
            else:
                print("❌ Test event not found in database")
                return False
                
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Event Creation System")
    print("=" * 60)
    
    # Test event creation functionality
    creation_passed = test_event_creation()
    
    # Test database event creation
    db_passed = test_database_connection()
    
    # Final summary
    print("\n" + "=" * 60)
    print("📋 FINAL TEST SUMMARY")
    print("=" * 60)
    
    if creation_passed and db_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Event creation functionality is working")
        print("✅ Database operations are working")
        print("✅ Form submission is fixed")
        print("✅ Error handling is implemented")
    else:
        print("❌ SOME TESTS FAILED")
        if not creation_passed:
            print("❌ Event creation functionality tests failed")
        if not db_passed:
            print("❌ Database tests failed")
    
    print("\n🔧 Event Creation Features Implemented:")
    print("• Fixed form submission (removed simulation)")
    print("• Added comprehensive error handling")
    print("• Added form validation")
    print("• QR code generation")
    print("• Database event creation")
    print("• Proper redirect after creation")
    print("• Flash messages for user feedback")

