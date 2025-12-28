# JoinUp Database - Quick Start Guide

## 🚀 Quick Setup (First Time)

### 1. Create Database Indexes
```bash
cd /app/database
python3 create_indexes.py
```

**What it does:**
- Creates all necessary indexes for optimal performance
- Sets up unique constraints
- Enables text search on events
- Takes ~2 seconds

**Output:**
```
✓ Users indexes created
✓ Events indexes created
✓ Registrations indexes created
✓ Certificates indexes created
✓ Ratings indexes created
```

---

### 2. Seed Sample Data (Optional - For Testing)
```bash
cd /app/database
python3 seed_data.py
```

**Type `yes` when prompted**

**What it creates:**
- 3 admin accounts
- 20 student accounts
- 8 organizer accounts
- 25 sample events
- 80 event registrations
- 60+ ratings

**Test Accounts Created:**
```
Admin:     admin1@joinup.com / admin123
Student:   john.smith0@student.com / student123
Organizer: organizer1@mit.com / organizer123
```

---

## 📊 Database Collections

### users
- **Purpose**: All user accounts (students, organizers, admins)
- **Key Fields**: email (unique), role, college, department
- **Indexes**: email, id, role, college

### events
- **Purpose**: All events created by organizers
- **Key Fields**: title, date, venue, organizer_id
- **Indexes**: id, organizer_id, date, college, category, text search

### registrations
- **Purpose**: Student event registrations with QR codes
- **Key Fields**: student_id, event_id, qr_code_data
- **Unique Constraint**: student_id + event_id (prevent duplicates)
- **Indexes**: qr_code_data, attendance_marked

### certificates
- **Purpose**: Issued certificates (base64 PDFs)
- **Key Fields**: registration_id, certificate_data
- **Indexes**: student_id, event_id

### ratings
- **Purpose**: Event ratings and feedback
- **Key Fields**: event_id, student_id, rating (1-5)
- **Unique Constraint**: student_id + event_id (one rating per student)

---

## 🛠️ Common Operations

### Check Database Status
```bash
mongosh joinup --eval "db.stats()"
```

### View Collection Counts
```bash
mongosh joinup --eval "
  db.users.countDocuments();
  db.events.countDocuments();
  db.registrations.countDocuments();
"
```

### Clear All Data (⚠️ DANGEROUS)
```bash
cd /app/database
python3 clear_database.py
```
**Type `yes` and then `DELETE` to confirm**

---

## 💾 Backup & Restore

### Create Backup
```bash
cd /app/database
./backup.sh
```

**What it does:**
- Creates timestamped backup
- Compresses to .tar.gz
- Stores in `/backup/joinup/`
- Auto-deletes backups older than 30 days

**Output:**
```
Backup saved to: /backup/joinup/20250101_120000.tar.gz
```

### Restore from Backup
```bash
cd /app/database
./restore.sh /backup/joinup/20250101_120000.tar.gz
```

**⚠️ WARNING**: This will replace all current data!

### List Available Backups
```bash
ls -lh /backup/joinup/
```

---

## 🔍 Useful MongoDB Queries

### Find User by Email
```javascript
use joinup
db.users.findOne({ email: "student@example.com" })
```

### List All Events
```javascript
db.events.find().sort({ date: -1 }).limit(10)
```

### Check Registrations for Event
```javascript
db.registrations.find({ event_id: "your-event-id" })
```

### View Event Ratings
```javascript
db.ratings.find({ event_id: "your-event-id" }).sort({ created_at: -1 })
```

### Count Users by Role
```javascript
db.users.aggregate([
  { $group: { _id: "$role", count: { $sum: 1 } } }
])
```

---

## 🎯 Performance Tips

### 1. Index Usage
All queries use indexed fields for fast performance:
- Email lookups: `email` index
- Event searches: `date`, `category` indexes
- QR scanning: `qr_code_data` index

### 2. Query Limits
All backend queries limit results to 1000 documents:
```python
.to_list(1000)
```

### 3. Text Search
Events support full-text search on title and description:
```javascript
db.events.find({ $text: { $search: "hackathon" } })
```

---

## 🔐 Security Checklist

- [x] Passwords hashed with bcrypt
- [x] JWT tokens for authentication
- [x] Unique constraints on critical fields
- [x] Role-based access control
- [ ] MongoDB authentication (enable in production)
- [ ] SSL/TLS encryption (enable in production)
- [ ] Network firewall rules (configure in production)

---

## 📈 Monitoring

### Check Slow Queries
```javascript
use joinup
db.setProfilingLevel(1, { slowms: 100 })
db.system.profile.find().limit(5).sort({ ts: -1 })
```

### Database Size
```javascript
db.stats()
```

### Collection Stats
```javascript
db.events.stats()
db.users.stats()
```

---

## 🐛 Troubleshooting

### Can't Connect to MongoDB
```bash
# Check if MongoDB is running
sudo systemctl status mongod

# Start MongoDB
sudo systemctl start mongod
```

### Indexes Not Working
```bash
# Rebuild indexes
cd /app/database
python3 create_indexes.py
```

### Database Too Large
```bash
# Check collection sizes
mongosh joinup --eval "
  db.events.stats().size;
  db.certificates.stats().size;
"

# Certificate PDFs might be large (base64)
# Consider moving to file storage
```

---

## 📝 Maintenance Schedule

**Daily:**
- Monitor slow queries
- Check error logs

**Weekly:**
- Run backup script
- Review database size

**Monthly:**
- Analyze query performance
- Optimize indexes if needed
- Clean up old backups

---

## 🎓 Example Workflow

### 1. Fresh Install
```bash
# Create indexes
cd /app/database
python3 create_indexes.py

# Seed sample data (optional)
python3 seed_data.py
```

### 2. Development Testing
```bash
# Use seeded test accounts
# Login as: john.smith0@student.com / student123

# Clear data when done
python3 clear_database.py
```

### 3. Before Production
```bash
# Clear test data
python3 clear_database.py

# Create indexes
python3 create_indexes.py

# Setup backup cron job
# Add to crontab:
# 0 2 * * * /app/database/backup.sh
```

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Create indexes | `python3 create_indexes.py` |
| Seed data | `python3 seed_data.py` |
| Clear database | `python3 clear_database.py` |
| Backup | `./backup.sh` |
| Restore | `./restore.sh <file>` |
| MongoDB shell | `mongosh joinup` |
| View logs | Check backend server logs |

---

## ✅ Database Setup Complete!

Your JoinUp database is now configured with:
- ✓ Optimized indexes for all collections
- ✓ Unique constraints to prevent duplicates
- ✓ Text search capability
- ✓ Backup/restore scripts
- ✓ Sample data (if seeded)

**Ready for production!** 🚀
