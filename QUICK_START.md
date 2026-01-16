# JoinUp - Quick Start Guide

## ⚠️ IMPORTANT: All Errors Have Been Fixed! ✅

**Root Issue:** Frontend was connecting to wrong backend URL (8080 instead of 8000)  
**Status:** ✅ FIXED in `frontend/.env`  
**Result:** Registration, Login, Logout - ALL WORKING NOW

---

## 🚀 Start Everything (Easiest Way)

```powershell
.\start-all.ps1
```

This will open 2 terminal windows:
1. **Backend Server** (FastAPI) on http://localhost:8000
2. **Frontend** (Expo) - follow instructions to open in browser/app

---

## 🔧 Manual Start (If You Prefer)

### Terminal 1: Backend
```powershell
cd backend
python server.py
```
✅ Wait for: `Uvicorn running on http://0.0.0.0:8000`

### Terminal 2: Frontend
```powershell
cd frontend
npm start
```
✅ Wait for: Metro bundler to finish, then:
- Press `w` for web browser
- Scan QR code with Expo Go app
- Or press `a` for Android emulator

---

## ✅ What's Working

- ✅ **User Registration & Login**
  - Three roles: Student, Organizer, Admin
  - Secure JWT authentication
  - Password hashing with bcrypt

- ✅ **Logout System**
  - Manual logout button on all dashboards
  - Auto-logout when app closes
  - Confirmation dialog to prevent accidents

- ✅ **Events**
  - Create events (organizer only)
  - Browse events (student)
  - Register for events
  - View my events

- ✅ **QR Codes & Attendance**
  - Generate QR per registration
  - Scan QR for attendance
  - Track attendance status

- ✅ **Dashboards**
  - Student: My events, certificates, profile
  - Organizer: My events, analytics, registrations
  - Admin: System management

---

## 🧪 Testing

Run the complete test suite:

```powershell
python test_all_features.py
```

This tests:
- Registration for students and organizers
- Login authentication
- Event creation
- Event registration
- Dashboard endpoints
- Error handling

---

## 📱 Test Credentials

After first run, you can use:
- **Student**: `student@test.com` / `password123`
- **Organizer**: `organizer@test.com` / `password123`

---

## 🌐 Browser URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:8081 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| API Redoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |

---

## 📋 Key Features

### Frontend (React Native / Expo)
- File-based routing with Expo Router
- TypeScript for type safety
- Context API for state management
- Unified theme system
- Three role-based dashboards

### Backend (FastAPI)
- Async request handling
- MongoDB integration
- JWT authentication
- CORS enabled
- Full API documentation

### Database (MongoDB)
- Users collection (email, password, role)
- Events collection (title, description, date, venue)
- Registrations collection (user_id, event_id, status)
- Certificates collection (user_id, event_id, pdf)

---

## 🎨 Theme System

Located in `frontend/theme.ts`:

```typescript
// Colors
colors.primary       // #6366F1 (Indigo)
colors.secondary     // #EC4899 (Pink)
colors.success       // #10B981 (Green)
colors.danger        // #EF4444 (Red)

// Spacing
spacing.sm, .md, .lg, .xl, etc.

// Typography
typography.h1, .h2, .body, .caption, etc.

// Border Radius
borderRadius.sm, .md, .lg, .full, etc.
```

---

## 🔐 Authentication Flow

1. **Register**
   - Choose role (Student/Organizer/Admin)
   - Fill email, password, name, college
   - Account created, JWT token issued

2. **Login**
   - Email + password
   - JWT token stored in AsyncStorage
   - Redirected to role-specific dashboard

3. **Logout**
   - Click logout button
   - Confirm action
   - Token cleared
   - Redirected to landing page

4. **Auto-Logout**
   - When app is closed/backgrounded
   - Session cleared automatically
   - Next time app opens, user must login

---

## 🛠️ Environment Variables

### Frontend (`frontend/app.json`)
```json
{
  "extra": {
    "EXPO_PUBLIC_BACKEND_URL": "http://localhost:8000"
  }
}
```

### Backend (`backend/.env` or env vars)
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=joinup
SECRET_KEY=your-secret-key-change-in-production
```

---

## 📖 Project Files

### Frontend
```
frontend/
├── app/                    # Expo Router pages
│   ├── _layout.tsx        # Root layout with Auth
│   ├── index.tsx          # Landing page
│   ├── auth/              # Login/Register/Role selection
│   ├── student/           # Student screens
│   ├── organizer/         # Organizer screens
│   └── admin/             # Admin screen
├── context/
│   └── AuthContext.tsx    # Auth state management
├── theme.ts               # Design tokens
└── package.json           # Dependencies
```

### Backend
```
backend/
├── server.py              # Main FastAPI app
├── auth.py                # Authentication logic
├── models.py              # Pydantic schemas
├── utils.py               # Utilities (QR, PDF, etc.)
├── requirements.txt       # Python packages
└── __pycache__/
```

### Database
```
database/
├── init_database.py       # Initialize collections
├── seed_data.py           # Add test data
├── create_indexes.py      # Create indexes
└── README.md              # DB schema docs
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Backend won't start | Kill process on port 8000: `netstat -ano \| findstr :8000` |
| Frontend shows error | Make sure `frontend/theme.ts` exists |
| MongoDB not found | Install MongoDB or start existing service |
| Auth not working | Check `.env` file, restart backend |
| Frontend can't reach backend | Check `EXPO_PUBLIC_BACKEND_URL` in `app.json` |

---

## 📚 Documentation

- **Full Setup Guide**: See `SETUP_COMPLETE.md`
- **API Documentation**: http://localhost:8000/docs
- **Codebase Guide**: See `.github/copilot-instructions.md`

---

## 🎯 Next Steps

1. Start the app: `.\start-all.ps1`
2. Test features: `python test_all_features.py`
3. Explore the UI and test logout
4. Check backend logs for any issues
5. Read `SETUP_COMPLETE.md` for detailed info

---

**Built with ❤️ using FastAPI + Expo/React Native + MongoDB**
