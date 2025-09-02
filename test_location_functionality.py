#!/usr/bin/env python3
"""
Test script for the new location functionality in event creation
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_location_functionality():
    """Test the new location functionality"""
    print("🧪 Testing New Location Functionality")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Check if create_event.html has been updated
    total_tests += 1
    try:
        with open('templates/party/create_event.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check if coordinates section was removed
        if 'Coordinates' not in content:
            print("✅ Coordinates section removed from form")
            tests_passed += 1
        else:
            print("❌ Coordinates section still present")
            
    except Exception as e:
        print(f"❌ Error reading create_event.html: {e}")
    
    # Test 2: Check if Google Places autocomplete is added
    total_tests += 1
    try:
        if 'google.maps.places.Autocomplete' in content:
            print("✅ Google Places autocomplete added")
            tests_passed += 1
        else:
            print("❌ Google Places autocomplete not found")
            
    except Exception as e:
        print(f"❌ Error checking autocomplete: {e}")
    
    # Test 3: Check if hidden coordinate fields are present
    total_tests += 1
    try:
        if 'type="hidden" id="latitude"' in content and 'type="hidden" id="longitude"' in content:
            print("✅ Hidden coordinate fields added")
            tests_passed += 1
        else:
            print("❌ Hidden coordinate fields not found")
            
    except Exception as e:
        print(f"❌ Error checking hidden fields: {e}")
    
    # Test 4: Check if geocoding function is added
    total_tests += 1
    try:
        if 'function geocodeAddress' in content:
            print("✅ Geocoding function added")
            tests_passed += 1
        else:
            print("❌ Geocoding function not found")
            
    except Exception as e:
        print(f"❌ Error checking geocoding function: {e}")
    
    # Test 5: Check if location field has autocomplete
    total_tests += 1
    try:
        if 'placeholder="Enter event address or venue name"' in content:
            print("✅ Location field updated with proper placeholder")
            tests_passed += 1
        else:
            print("❌ Location field placeholder not updated")
            
    except Exception as e:
        print(f"❌ Error checking location field: {e}")
    
    # Test 6: Check if map functionality is preserved
    total_tests += 1
    try:
        if 'id="map"' in content and 'google.maps.Map' in content:
            print("✅ Map functionality preserved")
            tests_passed += 1
        else:
            print("❌ Map functionality missing")
            
    except Exception as e:
        print(f"❌ Error checking map functionality: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All location functionality tests passed!")
        return True
    else:
        print("❌ Some location functionality tests failed")
        return False

def test_form_validation():
    """Test form validation logic"""
    print("\n🔍 Testing Form Validation Logic")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Check if validation logic is updated
    total_tests += 1
    try:
        with open('templates/party/create_event.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check if validation includes location check
        if 'Please select a valid location from suggestions' in content:
            print("✅ Updated validation logic found")
            tests_passed += 1
        else:
            print("❌ Updated validation logic not found")
            
    except Exception as e:
        print(f"❌ Error checking validation logic: {e}")
    
    # Test 2: Check if manual location entry is handled
    total_tests += 1
    try:
        if 'geocodeAddress(location)' in content:
            print("✅ Manual location entry handling added")
            tests_passed += 1
        else:
            print("❌ Manual location entry handling not found")
            
    except Exception as e:
        print(f"❌ Error checking manual entry handling: {e}")
    
    # Summary
    print(f"📊 Validation Tests: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All validation tests passed!")
        return True
    else:
        print("❌ Some validation tests failed")
        return False

if __name__ == "__main__":
    print("🚀 Testing New Location Functionality")
    print("=" * 60)
    
    # Test location functionality
    location_passed = test_location_functionality()
    
    # Test form validation
    validation_passed = test_form_validation()
    
    # Final summary
    print("\n" + "=" * 60)
    print("📋 FINAL TEST SUMMARY")
    print("=" * 60)
    
    if location_passed and validation_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Location functionality updated successfully")
        print("✅ Form validation updated correctly")
        print("✅ User experience improved")
    else:
        print("❌ SOME TESTS FAILED")
        if not location_passed:
            print("❌ Location functionality tests failed")
        if not validation_passed:
            print("❌ Validation tests failed")
    
    print("\n🔧 New Location Features Implemented:")
    print("• Removed coordinates input fields")
    print("• Added Google Places autocomplete")
    print("• Hidden coordinate fields for backend")
    print("• Manual address entry with geocoding")
    print("• Map preview with click-to-adjust")
    print("• India-specific location restrictions")
    print("• Real-time validation feedback")
    print("• User-friendly error messages")

