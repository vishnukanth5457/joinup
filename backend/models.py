from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    STUDENT = "student"
    ORGANIZER = "organizer"
    ADMIN = "admin"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"

class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole

class UserCreate(UserBase):
    password: str
    college: str
    department: Optional[str] = None
    year: Optional[int] = None
    organization_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: str
    college: str
    department: Optional[str] = None
    year: Optional[int] = None
    organization_name: Optional[str] = None
    is_approved: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

class EventBase(BaseModel):
    title: str
    description: str
    date: datetime
    venue: str
    fee: float
    college: str
    category: Optional[str] = "General"
    max_participants: Optional[int] = None
    image: Optional[str] = None  # base64 image

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: str
    organizer_id: str
    organizer_name: str
    current_registrations: int = 0
    average_rating: float = 0.0
    total_ratings: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

class RegistrationCreate(BaseModel):
    event_id: str

class Registration(BaseModel):
    id: str
    student_id: str
    student_name: str
    event_id: str
    event_title: str
    payment_status: PaymentStatus = PaymentStatus.PAID
    qr_code_data: str
    attendance_marked: bool = False
    attendance_time: Optional[datetime] = None
    certificate_issued: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

class AttendanceMarkRequest(BaseModel):
    qr_code_data: str

class CertificateIssueRequest(BaseModel):
    registration_id: str

class Certificate(BaseModel):
    id: str
    registration_id: str
    student_id: str
    student_name: str
    event_id: str
    event_title: str
    issued_date: datetime = Field(default_factory=datetime.utcnow)
    certificate_data: str  # base64 encoded PDF

    class Config:
        from_attributes = True

class RatingCreate(BaseModel):
    event_id: str
    rating: int = Field(ge=1, le=5)
    feedback: Optional[str] = None

class Rating(BaseModel):
    id: str
    event_id: str
    student_id: str
    student_name: str
    rating: int
    feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

class StudentDashboard(BaseModel):
    total_events_registered: int
    attended_events: int
    certificates_earned: int
    upcoming_events: int

class OrganizerAnalytics(BaseModel):
    total_events: int
    total_registrations: int
    total_attendees: int
    upcoming_events: int
    past_events: int
    average_rating: float
    top_events: List[dict]
