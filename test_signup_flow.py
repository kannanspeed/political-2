#!/usr/bin/env python3
"""
Test script to simulate actual signup form submission
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_signup_form_submission():
    """Test the actual signup form submission process"""
    print("🧪 Testing Signup Form Submission")
    print("=" * 40)
    
    try:
        from app import app, db, User
        from werkzeug.security import check_password_hash
        
        with app.test_client() as client:
            with app.app_context():
                # Test 1: Test regular user signup
                print("1️⃣ Testing regular user signup...")
                
                user_data = {
                    'email': 'testuser@example.com',
                    'phone': '1234567890',
                    'password': 'test123',
                    'role': 'user'
                }
                
                response = client.post('/signup', data=user_data, follow_redirects=True)
                
                if response.status_code == 200:
                    print("✅ Regular user signup successful")
                    
                    # Check if user was created
                    user = User.query.filter_by(email='testuser@example.com').first()
                    if user:
                        print(f"   User created with role: {user.role}")
                        # Clean up
                        db.session.delete(user)
                        db.session.commit()
                    else:
                        print("❌ User not found in database")
                else:
                    print(f"❌ Regular user signup failed: {response.status_code}")
                
                # Test 2: Test political party signup
                print("\n2️⃣ Testing political party signup...")
                
                party_data = {
                    'email': 'testparty@example.com',
                    'phone': '1234567890',
                    'password': 'test123',
                    'role': 'party',
                    'party_name': 'Test Political Party'
                }
                
                response = client.post('/signup', data=party_data, follow_redirects=True)
                
                if response.status_code == 200:
                    print("✅ Political party signup successful")
                    
                    # Check if user was created
                    party_user = User.query.filter_by(email='testparty@example.com').first()
                    if party_user:
                        print(f"   User created with role: {party_user.role}")
                        print(f"   Party name: {party_user.party_name}")
                        
                        # Test login
                        print("\n3️⃣ Testing political party login...")
                        
                        login_data = {
                            'email': 'testparty@example.com',
                            'password': 'test123'
                        }
                        
                        response = client.post('/login', data=login_data, follow_redirects=True)
                        
                        if response.status_code == 200:
                            print("✅ Political party login successful")
                            
                            # Check if redirected to party dashboard
                            if '/party/dashboard' in response.request.url or 'party_dashboard' in response.get_data(as_text=True):
                                print("✅ Redirected to party dashboard")
                            else:
                                print("⚠️  Not redirected to party dashboard")
                                print(f"   Final URL: {response.request.url}")
                        else:
                            print(f"❌ Political party login failed: {response.status_code}")
                        
                        # Clean up
                        db.session.delete(party_user)
                        db.session.commit()
                    else:
                        print("❌ Political party user not found in database")
                else:
                    print(f"❌ Political party signup failed: {response.status_code}")
                    print(f"   Response data: {response.get_data(as_text=True)}")
                
                # Test 3: Test signup with missing party name
                print("\n4️⃣ Testing signup with missing party name...")
                
                invalid_party_data = {
                    'email': 'testparty2@example.com',
                    'phone': '1234567890',
                    'password': 'test123',
                    'role': 'party'
                    # Missing party_name
                }
                
                response = client.post('/signup', data=invalid_party_data, follow_redirects=True)
                
                if response.status_code == 200:
                    print("✅ Signup with missing party name completed")
                    
                    # Check if user was created
                    party_user2 = User.query.filter_by(email='testparty2@example.com').first()
                    if party_user2:
                        print(f"   User created with role: {party_user2.role}")
                        print(f"   Party name: {party_user2.party_name}")
                        
                        # Clean up
                        db.session.delete(party_user2)
                        db.session.commit()
                    else:
                        print("❌ User not found in database")
                else:
                    print(f"❌ Signup with missing party name failed: {response.status_code}")
                
                print("\n🎉 Signup flow tests completed!")
                return True
                
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_signup_form_submission()
    if success:
        print("\n✅ Signup flow is working correctly!")
    else:
        print("\n❌ Signup flow has issues that need to be fixed.")

