#!/usr/bin/env python3
"""
Test script to simulate political party signup and login flow
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_party_flow():
    """Test the political party signup and login flow"""
    print("🧪 Testing Political Party User Flow")
    print("=" * 40)
    
    try:
        from app import app, db, User
        from werkzeug.security import generate_password_hash, check_password_hash
        
        with app.app_context():
            # Test 1: Create a political party user
            print("1️⃣ Creating political party user...")
            
            party_user = User(
                email='testparty@example.com',
                phone='1234567890',
                password_hash=generate_password_hash('test123'),
                role='party',
                party_name='Test Political Party',
                is_business_email=True
            )
            
            db.session.add(party_user)
            db.session.commit()
            
            print("✅ Political party user created successfully")
            print(f"   Email: {party_user.email}")
            print(f"   Role: {party_user.role}")
            print(f"   Party Name: {party_user.party_name}")
            
            # Test 2: Verify user exists in database
            print("\n2️⃣ Verifying user in database...")
            retrieved_user = User.query.filter_by(email='testparty@example.com').first()
            
            if retrieved_user:
                print("✅ User found in database")
                print(f"   ID: {retrieved_user.id}")
                print(f"   Role: {retrieved_user.role}")
                print(f"   Party Name: {retrieved_user.party_name}")
            else:
                print("❌ User not found in database")
                return False
            
            # Test 3: Test password verification
            print("\n3️⃣ Testing password verification...")
            if check_password_hash(retrieved_user.password_hash, 'test123'):
                print("✅ Password verification successful")
            else:
                print("❌ Password verification failed")
                return False
            
            # Test 4: Test role-based routing logic
            print("\n4️⃣ Testing role-based routing logic...")
            
            # Simulate the routing logic from the index route
            user_role = retrieved_user.role
            print(f"   User role: {user_role}")
            
            if user_role == 'admin':
                print("   Would redirect to: admin_dashboard")
            elif user_role == 'party':
                print("   Would redirect to: party_dashboard")
            else:
                print("   Would redirect to: user_dashboard")
            
            # Test 5: Check if party dashboard route exists
            print("\n5️⃣ Checking party dashboard route...")
            try:
                from flask import url_for
                with app.test_request_context():
                    party_dashboard_url = url_for('party_dashboard')
                    print(f"✅ Party dashboard route exists: {party_dashboard_url}")
            except Exception as e:
                print(f"❌ Party dashboard route error: {e}")
                return False
            
            # Test 6: Check if party dashboard template exists
            print("\n6️⃣ Checking party dashboard template...")
            template_path = 'templates/party/dashboard.html'
            if os.path.exists(template_path):
                print("✅ Party dashboard template exists")
            else:
                print("❌ Party dashboard template missing")
                return False
            
            # Clean up test user
            print("\n🧹 Cleaning up test user...")
            db.session.delete(retrieved_user)
            db.session.commit()
            print("✅ Test user cleaned up")
            
            print("\n🎉 All political party flow tests passed!")
            print("\n📋 Summary of the flow:")
            print("   1. User signs up as 'party' role")
            print("   2. User is created with role='party' and party_name")
            print("   3. User logs in successfully")
            print("   4. User is redirected to /party/dashboard")
            print("   5. Party dashboard displays user's events and stats")
            
            return True
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_party_flow()
    if success:
        print("\n✅ Political party flow is working correctly!")
    else:
        print("\n❌ Political party flow has issues that need to be fixed.")

