#!/usr/bin/env python3
"""
Database Seeding Script
Populates the database with sample data for development and testing
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path
from dotenv import load_dotenv
import uuid
from datetime import datetime, timedelta
import random
import sys

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent / 'backend'))

from auth import get_password_hash

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'joinup')

# Sample data
COLLEGES = ['MIT', 'Stanford', 'Harvard', 'UC Berkeley', 'Caltech', 'Oxford', 'Cambridge']
DEPARTMENTS = ['Computer Science', 'Electrical Engineering', 'Mechanical Engineering', 'Business', 'Physics']
CATEGORIES = ['Technology', 'Sports', 'Cultural', 'Academic', 'Business', 'Arts', 'General']
EVENT_NAMES = [
    'Tech Fest', 'Hackathon', 'Sports Day', 'Cultural Night', 'Business Summit',
    'Music Concert', 'Dance Competition', 'Coding Challenge', 'Startup Expo', 'Art Exhibition',
    'Science Fair', 'Robotics Workshop', 'AI Conference', 'Gaming Tournament', 'Film Festival'
]
FIRST_NAMES = ['John', 'Emma', 'Michael', 'Sophia', 'William', 'Olivia', 'James', 'Ava', 'Robert', 'Isabella']
LAST_NAMES = ['Smith', 'Johnson', 'Brown', 'Davis', 'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson']


async def seed_database():
    """Seed the database with sample data"""
    print(f"Connecting to MongoDB at {mongo_url}...")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✓ Connected to MongoDB successfully\n")
        
        # Clear existing data (optional)
        print("Clearing existing data...")
        await db.users.delete_many({})
        await db.events.delete_many({})
        await db.registrations.delete_many({})
        await db.certificates.delete_many({})
        await db.ratings.delete_many({})
        print("✓ Existing data cleared\n")
        
        # Create users
        users = []
        user_ids = {'students': [], 'organizers': [], 'admins': []}
        
        print("Creating users...")
        
        # Create admin users
        for i in range(3):
            admin_id = str(uuid.uuid4())
            user = {
                'id': admin_id,
                'email': f'admin{i+1}@joinup.com',
                'password': get_password_hash('admin123'),
                'name': f'Admin {i+1}',
                'role': 'admin',
                'college': 'JoinUp HQ',
                'is_approved': True,
                'created_at': datetime.utcnow()
            }
            users.append(user)
            user_ids['admins'].append(admin_id)
        
        # Create student users
        for i in range(20):
            student_id = str(uuid.uuid4())
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            college = random.choice(COLLEGES)
            user = {
                'id': student_id,
                'email': f'{first.lower()}.{last.lower()}{i}@student.com',
                'password': get_password_hash('student123'),
                'name': f'{first} {last}',
                'role': 'student',
                'college': college,
                'department': random.choice(DEPARTMENTS),
                'year': random.randint(1, 4),
                'is_approved': True,
                'created_at': datetime.utcnow() - timedelta(days=random.randint(1, 60))
            }
            users.append(user)
            user_ids['students'].append(student_id)
        
        # Create organizer users
        for i in range(8):
            organizer_id = str(uuid.uuid4())
            college = random.choice(COLLEGES)
            user = {
                'id': organizer_id,
                'email': f'organizer{i+1}@{college.lower().replace(" ", "")}.com',
                'password': get_password_hash('organizer123'),
                'name': f'{college} Event Team',
                'role': 'organizer',
                'college': college,
                'organization_name': f'{college} Events',
                'is_approved': True,
                'created_at': datetime.utcnow() - timedelta(days=random.randint(1, 90))
            }
            users.append(user)
            user_ids['organizers'].append(organizer_id)
        
        await db.users.insert_many(users)
        print(f"✓ Created {len(users)} users (3 admins, 20 students, 8 organizers)\n")
        
        # Create events
        events = []
        event_ids = []
        
        print("Creating events...")
        for i in range(25):
            event_id = str(uuid.uuid4())
            organizer_id = random.choice(user_ids['organizers'])
            organizer = next(u for u in users if u['id'] == organizer_id)
            
            days_ahead = random.randint(-30, 60)  # Some past, some future
            event_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            event = {
                'id': event_id,
                'title': f"{random.choice(EVENT_NAMES)} {2025}",
                'description': f"Join us for an amazing {random.choice(CATEGORIES).lower()} event at {organizer['college']}!",
                'date': event_date,
                'venue': f"{random.choice(['Main Auditorium', 'Sports Complex', 'Conference Hall', 'Open Ground', 'Tech Park'])}",
                'fee': random.choice([0, 100, 200, 500, 1000]),
                'college': organizer['college'],
                'category': random.choice(CATEGORIES),
                'max_participants': random.choice([50, 100, 200, 500, None]),
                'organizer_id': organizer_id,
                'organizer_name': organizer['name'],
                'current_registrations': 0,
                'average_rating': 0.0,
                'total_ratings': 0,
                'created_at': datetime.utcnow() - timedelta(days=random.randint(1, 45))
            }
            events.append(event)
            event_ids.append(event_id)
        
        await db.events.insert_many(events)
        print(f"✓ Created {len(events)} events\n")
        
        # Create registrations
        registrations = []
        registration_ids = []
        
        print("Creating registrations...")
        for i in range(80):
            student_id = random.choice(user_ids['students'])
            event_id = random.choice(event_ids)
            
            # Check if already registered
            existing = next((r for r in registrations if r['student_id'] == student_id and r['event_id'] == event_id), None)
            if existing:
                continue
            
            registration_id = str(uuid.uuid4())
            student = next(u for u in users if u['id'] == student_id)
            event = next(e for e in events if e['id'] == event_id)
            
            # 70% chance of attendance for past events
            is_past = event['date'] < datetime.utcnow()
            attendance_marked = is_past and random.random() < 0.7
            
            registration = {
                'id': registration_id,
                'student_id': student_id,
                'student_name': student['name'],
                'event_id': event_id,
                'event_title': event['title'],
                'payment_status': 'paid',
                'qr_code_data': f"joinup-{registration_id}",
                'attendance_marked': attendance_marked,
                'attendance_time': event['date'] + timedelta(hours=1) if attendance_marked else None,
                'certificate_issued': attendance_marked and random.random() < 0.8,
                'created_at': event['created_at'] + timedelta(days=random.randint(1, 10))
            }
            registrations.append(registration)
            registration_ids.append(registration_id)
            
            # Update event registration count
            event['current_registrations'] += 1
        
        if registrations:
            await db.registrations.insert_many(registrations)
            print(f"✓ Created {len(registrations)} registrations\n")
        
        # Update event registration counts
        for event in events:
            await db.events.update_one(
                {'id': event['id']},
                {'$set': {'current_registrations': event['current_registrations']}}
            )
        
        # Create ratings
        ratings = []
        
        print("Creating ratings...")
        for reg in registrations:
            if reg['attendance_marked'] and random.random() < 0.6:  # 60% of attended events get rated
                rating_id = str(uuid.uuid4())
                rating = {
                    'id': rating_id,
                    'event_id': reg['event_id'],
                    'student_id': reg['student_id'],
                    'student_name': reg['student_name'],
                    'rating': random.randint(3, 5),  # Mostly positive ratings
                    'feedback': random.choice([
                        'Great event!',
                        'Well organized and informative.',
                        'Excellent experience!',
                        'Really enjoyed it.',
                        'Good content and networking.',
                        None
                    ]),
                    'created_at': reg['attendance_time'] + timedelta(days=1) if reg['attendance_time'] else datetime.utcnow()
                }
                ratings.append(rating)
        
        if ratings:
            await db.ratings.insert_many(ratings)
            print(f"✓ Created {len(ratings)} ratings\n")
        
        # Update event average ratings
        for event in events:
            event_ratings = [r for r in ratings if r['event_id'] == event['id']]
            if event_ratings:
                avg_rating = sum(r['rating'] for r in event_ratings) / len(event_ratings)
                await db.events.update_one(
                    {'id': event['id']},
                    {'$set': {
                        'average_rating': round(avg_rating, 2),
                        'total_ratings': len(event_ratings)
                    }}
                )
        
        # Print summary
        print("="*50)
        print("✓ Database seeded successfully!")
        print("="*50)
        print("\nSummary:")
        print(f"  - Users: {len(users)}")
        print(f"    • Admins: 3")
        print(f"    • Students: 20")
        print(f"    • Organizers: 8")
        print(f"  - Events: {len(events)}")
        print(f"  - Registrations: {len(registrations)}")
        print(f"  - Ratings: {len(ratings)}")
        print("\nTest Accounts:")
        print("  Admin: admin1@joinup.com / admin123")
        print("  Student: john.smith0@student.com / student123")
        print("  Organizer: organizer1@mit.com / organizer123")
        print("="*50)
        
    except Exception as e:
        print(f"\n✗ Error seeding database: {e}")
        raise
    finally:
        client.close()
        print("\nConnection closed.")


if __name__ == "__main__":
    print("="*50)
    print("JoinUp Database Seeding")
    print("="*50)
    print("\nWARNING: This will clear all existing data!")
    response = input("Continue? (yes/no): ")
    if response.lower() == 'yes':
        asyncio.run(seed_database())
    else:
        print("Seeding cancelled.")
