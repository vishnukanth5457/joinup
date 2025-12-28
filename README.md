# JoinUp - Digital Event & Student Engagement Platform

<div align="center">
  <img src="./frontend/assets/images/joinup-logo.png" alt="JoinUp Logo" width="200"/>
  <h3>Your College Events, Digitized</h3>
  <p>A production-ready full-stack mobile application for digitizing college event management</p>
</div>

## 📱 Overview

JoinUp replaces WhatsApp groups, Google Forms, Excel sheets, and manual attendance with one unified digital platform for college event management. Built with modern mobile-first architecture for seamless student engagement and efficient organizer management.

## ✨ Features

### 👨‍🎓 Student Features
- **Event Discovery**: Browse inter-college events with search and filters
- **Easy Registration**: One-tap event registration with mock payment
- **Digital QR Codes**: Auto-generated QR codes for event check-in
- **My Events Dashboard**: Track registered, attended, and upcoming events
- **Certificate Management**: Download event participation certificates
- **Activity Tracking**: View SPO/activity points and achievements

### 🏫 Organizer Features
- **Event Creation**: Create and manage events with full details
- **Registration Management**: View all registered students
- **QR Code Scanning**: Mark attendance via QR code scanning
- **Certificate Issuance**: Generate and issue certificates to attendees
- **Analytics Dashboard**: Track registrations and engagement

### 👑 Admin Features (Basic)
- **User Management**: View and manage all users
- **Event Oversight**: Monitor all platform events
- **Organizer Approval**: Approve/block event organizers

## 🏗️ Tech Stack

### Frontend (Mobile App)
- **Framework**: Expo (React Native 0.79.5)
- **Language**: TypeScript
- **Navigation**: Expo Router (file-based routing)
- **State Management**: React Context API + AsyncStorage
- **UI Components**: React Native core components
- **Icons**: @expo/vector-icons
- **QR Codes**: react-native-qrcode-svg
- **Date Handling**: date-fns
- **HTTP Client**: axios

### Backend (API Server)
- **Framework**: FastAPI (Python)
- **Authentication**: JWT (PyJWT)
- **Password Hashing**: bcrypt
- **QR Generation**: qrcode library
- **PDF Generation**: ReportLab
- **CORS**: FastAPI CORS middleware

### Database
- **Database**: MongoDB (Motor async driver)
- **Collections**:
  - `users` - Student, organizer, and admin accounts
  - `events` - Event details and metadata
  - `registrations` - Event registrations with QR codes
  - `certificates` - Issued certificates (base64 PDFs)

## 📁 Project Structure

```
/app
├── backend/
│   ├── server.py          # Main FastAPI application
│   ├── models.py          # Pydantic models
│   ├── auth.py            # JWT authentication & authorization
│   ├── utils.py           # QR code & certificate generation
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Environment variables
├── frontend/
│   ├── app/
│   │   ├── index.tsx          # Landing & role selection
│   │   ├── _layout.tsx        # Root navigation layout
│   │   ├── theme.ts           # Design system & colors
│   │   ├── auth/              # Authentication screens
│   │   │   ├── role-selection.tsx
│   │   │   ├── login.tsx
│   │   │   └── register.tsx
│   │   ├── student/(tabs)/    # Student tab navigation
│   │   │   ├── _layout.tsx
│   │   │   ├── index.tsx      # Event discovery
│   │   │   ├── my-events.tsx  # Registered events
│   │   │   └── profile.tsx    # Student profile
│   │   ├── organizer/         # Organizer screens
│   │   │   ├── dashboard.tsx
│   │   │   ├── analytics.tsx  # Analytics dashboard
│   │   │   └── qr-scanner.tsx # QR code scanner
│   │   └── admin/             # Admin screens
│   │       └── dashboard.tsx
│   ├── context/
│   │   └── AuthContext.tsx    # Auth state management
│   ├── assets/
│   ├── package.json
│   └── .env              # Expo environment variables
├── database/              # Database configuration & scripts
│   ├── README.md         # Full database documentation
│   ├── QUICKSTART.md     # Quick setup guide
│   ├── create_indexes.py # Index creation script
│   ├── seed_data.py      # Sample data seeding
│   ├── clear_database.py # Clear all data
│   ├── backup.sh         # Automated backup
│   └── restore.sh        # Database restore
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and Yarn
- Python 3.11+
- MongoDB instance
- Expo CLI (optional, for development)

### Environment Setup

#### Backend (.env)
```bash
SECRET_KEY=your-secret-key-change-in-production
MONGO_URL=mongodb://localhost:27017
DB_NAME=joinup
```

#### Frontend (.env)
```bash
EXPO_PUBLIC_BACKEND_URL=https://your-backend-url.com
EXPO_PACKAGER_HOSTNAME=your-hostname
EXPO_PACKAGER_PROXY_URL=your-proxy-url
```

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd app
```

2. **Setup Database**
```bash
# Create indexes (required)
cd database
python3 create_indexes.py

# Seed sample data (optional - for testing)
python3 seed_data.py
```

3. **Install Backend Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Install Frontend Dependencies**
```bash
cd frontend
yarn install
```

5. **Start MongoDB**
```bash
# Ensure MongoDB is running on localhost:27017
mongod
```

6. **Start Backend Server**
```bash
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

7. **Start Expo Development Server**
```bash
cd frontend
yarn start
```

8. **Run on Device/Emulator**
- Scan QR code with Expo Go app (iOS/Android)
- Press `a` for Android emulator
- Press `i` for iOS simulator

## 🎯 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user profile

### Events
- `GET /api/events` - List all events (with search)
- `GET /api/events/{event_id}` - Get event details
- `POST /api/events` - Create event (organizer only)
- `GET /api/events/organizer/my-events` - Get organizer's events

### Registrations
- `POST /api/registrations` - Register for event (student)
- `GET /api/registrations/my-registrations` - Get student's registrations
- `GET /api/registrations/event/{event_id}` - Get event registrations (organizer)

### Attendance & Certificates
- `POST /api/attendance/mark` - Mark attendance via QR (organizer)
- `POST /api/certificates/issue` - Issue certificate (organizer)
- `GET /api/certificates/my-certificates` - Get student's certificates

### Dashboard
- `GET /api/dashboard/student` - Get student dashboard stats

### Admin
- `GET /api/admin/users` - List all users (admin)
- `GET /api/admin/events` - List all events (admin)

## 🎨 Design System

### Color Palette (from Logo)
- **Primary Pink**: `#EC407A` - Call-to-action buttons, highlights
- **Secondary Blue**: `#42A5F5` - Secondary actions, links
- **Accent Purple**: `#5E35B1` - Headers, badges
- **Success Green**: `#4CAF50`
- **Warning Orange**: `#FF9800`
- **Error Red**: `#F44336`

### Typography
- **H1**: 32px, bold
- **H2**: 24px, bold
- **H3**: 20px, semi-bold
- **Body**: 16px, regular
- **Caption**: 12px, regular

### Spacing
- Uses 8pt grid system (8px, 16px, 24px, 32px, 48px)

## 🔐 Authentication Flow

1. User selects role (Student/Organizer/Admin)
2. User registers or logs in
3. JWT token stored in AsyncStorage
4. Token included in all API requests via Authorization header
5. Backend validates token and role-based permissions
6. User navigated to role-specific dashboard

## 📸 Screenshots

*(Add screenshots here)*

## 🧪 Testing

### Backend Testing
All backend APIs have been tested and validated:
- ✅ User registration and login
- ✅ Event creation and listing
- ✅ Student registration with QR codes
- ✅ Role-based access control
- ✅ Error handling and validation

```bash
# Run backend tests
curl http://localhost:8001/api/events
```

### Frontend Testing
Test the mobile app on physical device using Expo Go:
1. Install Expo Go from App Store/Play Store
2. Scan QR code from terminal
3. Test all user flows

## 🚧 Future Roadmap

### Phase 2 (Not Implemented Yet)
- [ ] Real payment integration (Razorpay/UPI)
- [ ] Firebase push notifications
- [ ] QR scanner implementation for organizers
- [ ] Certificate PDF download functionality
- [ ] Event image uploads
- [ ] Advanced search and filters
- [ ] Event categories and tags

### Phase 3 (Future)
- [ ] AI-based event recommendations
- [ ] Blockchain certificate verification
- [ ] Analytics dashboard for organizers
- [ ] In-app messaging
- [ ] Event feedback and ratings
- [ ] Multi-college network features

## 🐛 Known Issues

1. **Date Input**: Event creation uses text input for dates (needs date picker)
2. **QR Scanner**: Organizer QR scanning not yet implemented
3. **Certificate Download**: Certificate download to device not implemented
4. **Image Upload**: Event images not supported yet
5. **Real Payments**: Payment is mocked (auto-approved)

## 📝 Development Notes

### Key Decisions
- **Expo Router**: Chosen for file-based routing simplicity
- **JWT Auth**: Stateless authentication for scalability
- **Mock Payments**: For MVP demo purposes
- **Base64 Certificates**: Stored in DB for quick access

### Performance Considerations
- Database queries limited to 1000 documents
- No pagination implemented yet
- Certificate PDFs stored as base64 (can be optimized)

## 🤝 Contributing

This is an MVP project. Contributions welcome for:
- Bug fixes
- Feature implementations from roadmap
- UI/UX improvements
- Performance optimizations

## 📄 License

MIT License - Feel free to use this project for learning and development.

## 👏 Acknowledgments

- Built with ❤️ for college communities
- Inspired by the need to digitize campus events
- Logo colors: Pink (#EC407A), Blue (#42A5F5), Purple (#5E35B1)

---

**JoinUp v1.0.0** - Digitizing College Events, One Registration at a Time 🎓✨
