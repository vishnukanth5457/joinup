# JoinUp Codebase Guide for AI Agents

**JoinUp** is a production-ready full-stack mobile event management platform built with Expo (React Native) frontend and FastAPI backend, using MongoDB for persistence.

## Architecture Overview

### Tech Stack
- **Frontend**: Expo (React Native), TypeScript, Expo Router (file-based routing), React Context API for state
- **Backend**: FastAPI (Python), async with Motor (MongoDB driver)
- **Database**: MongoDB (4 core collections: users, events, registrations, certificates)
- **Authentication**: JWT tokens (7-day expiry), bcrypt password hashing

### Data Flow
1. **Frontend** → Axios HTTP calls → **Backend** (all routes prefixed `/api/`)
2. **Backend** → Motor async queries → **MongoDB**
3. **Auth tokens** stored in frontend AsyncStorage, validated via Bearer scheme in backend

### Critical Files
- [backend/server.py](backend/server.py) - Main FastAPI app with all API routes
- [backend/auth.py](backend/auth.py) - JWT creation, token verification, role-based access control
- [backend/models.py](backend/models.py) - Pydantic schemas for all entities (User, Event, Registration, Certificate)
- [frontend/context/AuthContext.tsx](frontend/context/AuthContext.tsx) - Frontend auth state management, token lifecycle
- [frontend/app/_layout.tsx](frontend/app/_layout.tsx) - Root navigation wrapper with AuthProvider
- [database/README.md](database/README.md) - MongoDB schema definitions and collection indexes

## User Roles & Key Workflows

**Three roles** with distinct permissions:
- **Student**: Register for events, view QR codes, download certificates
- **Organizer**: Create events, scan QR codes for attendance, issue certificates
- **Admin**: Manage users and platform oversight

### Critical Backend Routes
- `POST /api/auth/register`, `POST /api/auth/login` → Token + User data
- `GET /api/events` → List all events (paginated)
- `POST /api/events` → Create event (organizer only)
- `POST /api/registrations` → Register for event (student), creates unique QR code
- `GET /api/registrations/my-registrations` → Student's registered events
- `POST /api/mark-attendance` → Scan QR code (organizer), marks attendance

### Auth Pattern
- Backend dependency: `get_current_user` extracts user from Bearer token
- Role enforcement: `require_role(["organizer", "admin"])` middleware wrapper
- Frontend: `useAuthContext()` hook provides `user`, `token`, `login()`, `register()`, `logout()`
- **All protected routes** require Authorization header with JWT

## Project Conventions

### Backend API Conventions
- All routes use `/api/` prefix
- Request/response models in [backend/models.py](backend/models.py) - use Pydantic for validation
- Async/await consistently (Motor, FastAPI async handlers)
- **Error handling**: HTTPException with status codes (401 auth, 403 permission, 404 not found)
- CORS pre-configured for all origins (development mode)
- Environment variables: `MONGO_URL`, `DB_NAME`, `SECRET_KEY` from `.env`

### Frontend Navigation & State
- **Routing**: Expo Router file-based (`/app/auth/login.tsx` → `/auth/login` route)
- **Auth flow**: Landing → Role Selection → Register/Login → Dashboard (tabs for students, single screens for organizer/admin)
- **State management**: Minimal - AuthContext for auth state, AsyncStorage for persistence
- **API base URL**: From `EXPO_PUBLIC_BACKEND_URL` env var or defaults to `http://localhost:8000`

### MongoDB Schema Conventions
- Document IDs: Custom UUID strings (not ObjectId) in `id` field
- Timestamps: ISO format `created_at`, `updated_at` using `datetime.utcnow()`
- Unique constraints: Email (users), Event ID, Registration ID, QR code data
- Compound indexes for common queries (e.g., `student_id + event_id` in registrations)

## Development Workflows

### Local Development Setup
1. **Backend**: `cd backend && pip install -r requirements.txt`, set `.env` with MongoDB, run `uvicorn server:app --reload`
2. **Frontend**: `cd frontend && npm install`, run `npm start` (Expo Go or Android/iOS emulator)
3. **Database**: MongoDB running locally on `:27017` (use `database/init_database.py` for schema setup)

### Testing
- Backend tests in `comprehensive_backend_test.py` (pytest-style)
- Integration tests: Database seeding in `database/seed_data.py`
- Test utilities: `database/check_db.py` for MongoDB verification

### Common Tasks
- **Add new endpoint**: Define Pydantic model in `models.py`, add route in `server.py`, use auth dependencies
- **Add screen**: Create `.tsx` file in `frontend/app/` following folder structure, integrate via `_layout.tsx`
- **Database migration**: Modify collection schema in server logic, run `database/create_indexes.py` to update indexes
- **QR code generation**: Use `generate_qr_code()` in [backend/utils.py](backend/utils.py), returned as base64 PNG
- **Certificate generation**: Use `generate_certificate_pdf()` in [backend/utils.py](backend/utils.py), returns base64 PDF

## Integration Points & Dependencies

### External Libraries
- **Frontend**: `axios` for HTTP, `react-native-qrcode-svg` for QR rendering, `expo-barcode-scanner` for scanning
- **Backend**: `motor` (async MongoDB), `pyjwt` (JWT), `bcrypt` (passwords), `reportlab` (PDF generation)

### Cross-Component Communication
- Frontend sends `Authorization: Bearer <token>` header → Backend validates with `get_current_user`
- QR code workflow: Registration creates QR → stored as base64 in DB → frontend displays → organizer scans with camera
- Certificate workflow: After attendance marked → backend generates PDF → stores as base64 → frontend downloads

### Environment Bridges
- Frontend uses `EXPO_PUBLIC_BACKEND_URL` to connect to backend
- Backend reads `MONGO_URL` to connect to MongoDB
- Both use `SECRET_KEY` (backend stores, frontend receives in token)

---

## Quick Reference for Common Patterns

| Task | File | Pattern |
|------|------|---------|
| Add protected endpoint | `backend/server.py` | `@app.post(...) async def route(current_user = Depends(get_current_user)):` |
| Require role | `backend/server.py` | `current_user = Depends(require_role(["organizer"]))` |
| Auth state in UI | `frontend/**/*.tsx` | `const { user, token } = useAuthContext()` |
| API call | `frontend/**/*.tsx` | `axios.post(..., { headers: { Authorization: \`Bearer \${token}\` } })` |
| MongoDB query | `backend/server.py` | `db.collection_name.find_one({"field": value})` (Motor async) |
| QR/Certificate | `backend/utils.py` | `generate_qr_code(data)` returns base64 PNG or PDF |

