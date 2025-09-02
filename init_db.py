#!/usr/bin/env python3
"""
Database Initialization Script for Political Events App
Run this script to create all database tables and initial data.
"""

import os
from app_production import app, db, User
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize the database with tables and initial data."""
    
    # Ensure instance directory exists
    instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)
        print(f"✅ Created instance directory: {instance_dir}")
    
    with app.app_context():
        print("Creating database tables...")
        try:
            db.create_all()
            print("✅ Database tables created successfully!")
        except Exception as e:
            print(f"❌ Error creating database: {e}")
            return
        
        # Check if admin user exists
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print("Creating admin user...")
            admin = User(
                email='admin@political.com',
                phone='1234567890',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created: admin@political.com / admin123")
        else:
            print("✅ Admin user already exists")
        
        # Check if demo party user exists
        party_user = User.query.filter_by(role='party').first()
        if not party_user:
            print("Creating demo party user...")
            party_user = User(
                email='party@demo.com',
                phone='9876543210',
                password_hash=generate_password_hash('party123'),
                role='party',
                party_name='Demo Political Party'
            )
            db.session.add(party_user)
            db.session.commit()
            print("✅ Demo party user created: party@demo.com / party123")
        else:
            print("✅ Demo party user already exists")
        
        # Check if demo regular user exists
        regular_user = User.query.filter_by(role='user').first()
        if not regular_user:
            print("Creating demo regular user...")
            regular_user = User(
                email='user@demo.com',
                phone='5555555555',
                password_hash=generate_password_hash('user123'),
                role='user'
            )
            db.session.add(regular_user)
            db.session.commit()
            print("✅ Demo regular user created: user@demo.com / user123")
        else:
            print("✅ Demo regular user already exists")
        
        print("\n🎉 Database initialization complete!")
        print("\n📋 Demo Accounts:")
        print("   Admin: admin@political.com / admin123")
        print("   Party: party@demo.com / party123")
        print("   User:  user@demo.com / user123")

if __name__ == '__main__':
    init_database()

