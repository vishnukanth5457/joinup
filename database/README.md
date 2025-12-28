# MongoDB Configuration for JoinUp

## Database Setup

### Connection Details
- **Host**: localhost (or your MongoDB server)
- **Port**: 27017 (default MongoDB port)
- **Database Name**: joinup
- **Authentication**: Optional (configure based on your setup)

### Environment Variables

Create or update `.env` file in `/app/backend/`:

```bash
MONGO_URL=mongodb://localhost:27017
DB_NAME=joinup
SECRET_KEY=your-secret-key-change-in-production-xyz123
```

### Production Configuration

For production, use MongoDB Atlas or a secure MongoDB instance:

```bash
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=joinup_prod
SECRET_KEY=strong-random-secret-key-min-32-chars
```

## Database Collections

### 1. users
Stores all user accounts (students, organizers, admins)

**Indexes:**
- `email` (unique)
- `id` (unique)
- `role`
- `college`

**Sample Document:**
```json
{
  "_id": ObjectId("..."),
  "id": "uuid-string",
  "email": "student@example.com",
  "password": "$2b$12$hashed_password",
  "name": "John Doe",
  "role": "student",
  "college": "MIT",
  "department": "Computer Science",
  "year": 3,
  "organization_name": null,
  "is_approved": true,
  "created_at": ISODate("2025-01-01T00:00:00Z")
}
```

### 2. events
Stores all events created by organizers

**Indexes:**
- `id` (unique)
- `organizer_id`
- `date`
- `college`
- `category`
- `average_rating`

**Sample Document:**
```json
{
  "_id": ObjectId("..."),
  "id": "uuid-string",
  "title": "Tech Fest 2025",
  "description": "Annual technology festival",
  "date": ISODate("2025-03-15T10:00:00Z"),
  "venue": "Main Auditorium",
  "fee": 500.0,
  "college": "MIT",
  "category": "Technology",
  "max_participants": 200,
  "organizer_id": "uuid-string",
  "organizer_name": "Tech Club MIT",
  "current_registrations": 45,
  "average_rating": 4.5,
  "total_ratings": 23,
  "image": "base64-encoded-image-string",
  "created_at": ISODate("2025-01-01T00:00:00Z")
}
```

### 3. registrations
Stores student registrations for events

**Indexes:**
- `id` (unique)
- `student_id`
- `event_id`
- `qr_code_data` (unique)
- Compound: `student_id + event_id` (unique)

**Sample Document:**
```json
{
  "_id": ObjectId("..."),
  "id": "uuid-string",
  "student_id": "uuid-string",
  "student_name": "John Doe",
  "event_id": "uuid-string",
  "event_title": "Tech Fest 2025",
  "payment_status": "paid",
  "qr_code_data": "joinup-uuid-string",
  "attendance_marked": false,
  "attendance_time": null,
  "certificate_issued": false,
  "created_at": ISODate("2025-01-05T00:00:00Z")
}
```

### 4. certificates
Stores issued certificates

**Indexes:**
- `id` (unique)
- `registration_id` (unique)
- `student_id`
- `event_id`

**Sample Document:**
```json
{
  "_id": ObjectId("..."),
  "id": "uuid-string",
  "registration_id": "uuid-string",
  "student_id": "uuid-string",
  "student_name": "John Doe",
  "event_id": "uuid-string",
  "event_title": "Tech Fest 2025",
  "issued_date": ISODate("2025-03-16T00:00:00Z"),
  "certificate_data": "base64-encoded-pdf-string"
}
```

### 5. ratings
Stores event ratings and feedback

**Indexes:**
- `id` (unique)
- `event_id`
- `student_id`
- Compound: `student_id + event_id` (unique)

**Sample Document:**
```json
{
  "_id": ObjectId("..."),
  "id": "uuid-string",
  "event_id": "uuid-string",
  "student_id": "uuid-string",
  "student_name": "John Doe",
  "rating": 5,
  "feedback": "Excellent event! Well organized.",
  "created_at": ISODate("2025-03-16T00:00:00Z")
}
```

## Performance Optimization

### Recommended Indexes

Run the index creation script to create all necessary indexes:

```bash
python /app/database/create_indexes.py
```

### Query Optimization Tips

1. **Limit Results**: All queries use `.to_list(1000)` to prevent memory issues
2. **Projection**: Only fetch required fields when possible
3. **Sorting**: Sort on indexed fields for better performance
4. **Aggregation**: Use MongoDB aggregation pipeline for complex queries

## Backup and Restore

### Backup Database

```bash
mongodump --db joinup --out /backup/joinup-backup-$(date +%Y%m%d)
```

### Restore Database

```bash
mongorestore --db joinup /backup/joinup-backup-20250101/joinup/
```

### Automated Backup Script

See `/app/database/backup.sh` for automated backup script.

## Data Seeding

For development and testing, seed sample data:

```bash
python /app/database/seed_data.py
```

This will create:
- 3 admin users
- 10 student users
- 5 organizer users
- 15 sample events
- 50 registrations
- 30 ratings

## Security Best Practices

1. **Authentication**: Enable MongoDB authentication in production
2. **SSL/TLS**: Use encrypted connections
3. **Network**: Restrict MongoDB port access
4. **Passwords**: Never store plain text passwords
5. **Backups**: Regular automated backups
6. **Monitoring**: Set up MongoDB monitoring

## Troubleshooting

### Connection Issues

```python
# Test MongoDB connection
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def test_connection():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    try:
        await client.admin.command('ping')
        print("Connected successfully!")
    except Exception as e:
        print(f"Connection failed: {e}")

asyncio.run(test_connection())
```

### Clear Database (Development Only)

```bash
python /app/database/clear_database.py
```

**WARNING**: This will delete all data!

## Monitoring

### Check Database Size

```javascript
use joinup
db.stats()
```

### Monitor Slow Queries

```javascript
db.setProfilingLevel(1, { slowms: 100 })
db.system.profile.find().limit(5).sort({ ts: -1 })
```

## Migration

For schema changes, see `/app/database/migrations/` directory.
