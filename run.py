#!/usr/bin/env python3
"""
Startup script for the Political Events Platform
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Main startup function"""
    print("🏛️ Political Events Platform")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found!")
        print("Please run this script from the project root directory.")
        sys.exit(1)
    
    # Check if templates directory exists
    if not os.path.exists('templates'):
        print("❌ Error: templates directory not found!")
        print("Please ensure all template files are in place.")
        sys.exit(1)
    
    # Check environment variables
    print("🔧 Checking configuration...")
    
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key or secret_key == 'your-secret-key-here':
        print("⚠️  Warning: SECRET_KEY not set or using default value")
        print("   Please set a secure SECRET_KEY in your .env file")
    
    google_maps_key = os.getenv('GOOGLE_MAPS_API_KEY', 'AIzaSyC4VX_V-P58o0lS1OTAkpfqqRPeNoc61z0')
    if not google_maps_key or google_maps_key == 'your-google-maps-api-key':
        print("⚠️  Warning: GOOGLE_MAPS_API_KEY not set")
        print("   Location features will be limited")
    
    # Try to import and run the app
    try:
        print("🚀 Starting application...")
        
        # Import the app
        from app import app, socketio
        
        print("✅ Application loaded successfully")
        print("🌐 Starting web server...")
        print("📱 Open your browser to: http://localhost:5000")
        print("🔑 Default admin login: admin@political.com / admin123")
        print("\nPress Ctrl+C to stop the server")
        
        # Run the application
        socketio.run(app, 
                    host='0.0.0.0', 
                    port=5000, 
                    debug=True,
                    allow_unsafe_werkzeug=True)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install all required packages:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("Please check your configuration and try again.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
