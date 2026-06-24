from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class CourseLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class EnrollmentStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class Entity:
    id: Optional[int] = None

class Course(Entity):
    title: str
    description: str
    price: float
    level: CourseLevel
    duration_hours: int
    is_active: bool = True
    created_at: datetime

class Student(Entity):
    name: str
    email: str
    phone: str
    registered_at: datetime
    is_active: bool = True

class Enrollment(Entity):
    student_id: int
    course_id: int
    enrollment_date: datetime
    status: EnrollmentStatus
    progress_percent: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class Lesson(Entity):
    course_id: int
    title: str
    order_number: int
    content: str
    duration_minutes: int

class Test(Entity):
    lesson_id: int
    questions: List[Dict[str, Any]]

class Certificate(Entity):
    student_id: int
    course_id: int
    certificate_number: str
    issued_at: datetime
    verification_url: str

class Payment(Entity):
    student_id: int
    course_id: int
    amount: float
    payment_date: datetime
    status: PaymentStatus
    transaction_id: str

class CourseRepository(ABC):
    @abstractmethod
    def save(self, course: Course) -> Course:
        pass
    
    @abstractmethod
    def find_by_id(self, course_id: int) -> Optional[Course]:
        pass
    
    @abstractmethod
    def find_all(self, skip: int = 0, limit: int = 100) -> List[Course]:
        pass
    
    @abstractmethod
    def find_by_level(self, level: CourseLevel) -> List[Course]:
        pass
    
    @abstractmethod
    def search_by_title(self, query: str) -> List[Course]:
        pass
    
    @abstractmethod
    def delete(self, course_id: int) -> bool:
        pass
    
    @abstractmethod
    def update(self, course: Course) -> Course:
        pass

class StudentRepository(ABC):
    @abstractmethod
    def save(self, student: Student) -> Student:
        pass
    
    @abstractmethod
    def find_by_id(self, student_id: int) -> Optional[Student]:
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Student]:
        pass
    
    @abstractmethod
    def find_all(self, skip: int = 0, limit: int = 100) -> List[Student]:
        pass
    
    @abstractmethod
    def update(self, student: Student) -> Student:
        pass

class EnrollmentRepository(ABC):
    @abstractmethod
    def save(self, enrollment: Enrollment) -> Enrollment:
        pass
    
    @abstractmethod
    def find_by_id(self, enrollment_id: int) -> Optional[Enrollment]:
        pass
    
    @abstractmethod
    def find_by_student_and_course(self, student_id: int, course_id: int) -> Optional[Enrollment]:
        pass
    
    @abstractmethod
    def find_by_student(self, student_id: int) -> List[Enrollment]:
        pass
    
    @abstractmethod
    def find_by_course(self, course_id: int) -> List[Enrollment]:
        pass
    
    @abstractmethod
    def update(self, enrollment: Enrollment) -> Enrollment:
        pass
    
    @abstractmethod
    def find_active_by_student(self, student_id: int) -> List[Enrollment]:
        pass

class LessonRepository(ABC):
    @abstractmethod
    def save(self, lesson: Lesson) -> Lesson:
        pass
    
    @abstractmethod
    def find_by_id(self, lesson_id: int) -> Optional[Lesson]:
        pass
    
    @abstractmethod
    def find_by_course(self, course_id: int) -> List[Lesson]:
        pass
    
    @abstractmethod
    def delete(self, lesson_id: int) -> bool:
        pass
    
    @abstractmethod
    def update(self, lesson: Lesson) -> Lesson:
        pass

class TestRepository(ABC):
    @abstractmethod
    def save(self, test: Test) -> Test:
        pass
    
    @abstractmethod
    def find_by_lesson(self, lesson_id: int) -> Optional[Test]:
        pass
    
    @abstractmethod
    def update(self, test: Test) -> Test:
        pass

class CertificateRepository(ABC):
    @abstractmethod
    def save(self, certificate: Certificate) -> Certificate:
        pass
    
    @abstractmethod
    def find_by_id(self, cert_id: int) -> Optional[Certificate]:
        pass
    
    @abstractmethod
    def find_by_student_and_course(self, student_id: int, course_id: int) -> Optional[Certificate]:
        pass
    
    @abstractmethod
    def find_by_student(self, student_id: int) -> List[Certificate]:
        pass
    
    @abstractmethod
    def find_by_number(self, cert_number: str) -> Optional[Certificate]:
        pass

class PaymentRepository(ABC):
    @abstractmethod
    def save(self, payment: Payment) -> Payment:
        pass
    
    @abstractmethod
    def find_by_id(self, payment_id: int) -> Optional[Payment]:
        pass
    
    @abstractmethod
    def find_by_student_and_course(self, student_id: int, course_id: int) -> Optional[Payment]:
        pass
    
    @abstractmethod
    def find_by_student(self, student_id: int) -> List[Payment]:
        pass
    
    @abstractmethod
    def update(self, payment: Payment) -> Payment:
        pass