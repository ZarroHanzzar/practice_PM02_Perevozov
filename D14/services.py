import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import json

from interfaces import (
    Course, Student, Enrollment, Lesson, Test, Certificate, Payment,
    CourseRepository, StudentRepository, EnrollmentRepository,
    LessonRepository, TestRepository, CertificateRepository, PaymentRepository,
    CourseLevel, EnrollmentStatus, PaymentStatus
)
from exceptions import (
    CourseNotFoundError, StudentNotFoundError, EnrollmentNotFoundError,
    LessonNotFoundError, TestNotFoundError, CertificateNotFoundError,
    DuplicateEnrollmentError, CourseNotActiveError, StudentNotActiveError,
    PaymentRequiredError, ProgressNotValidError, CertificateAlreadyIssuedError,
    CourseHasStudentsError, ValidationError, BusinessRuleViolation
)

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName
        }
        if hasattr(record, 'extra_data'):
            log_entry.update(record.extra_data)
        return json.dumps(log_entry)

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class EducationPortalService:
    def __init__(
        self,
        course_repo: CourseRepository,
        student_repo: StudentRepository,
        enrollment_repo: EnrollmentRepository,
        lesson_repo: LessonRepository,
        test_repo: TestRepository,
        certificate_repo: CertificateRepository,
        payment_repo: PaymentRepository
    ):
        self._course_repo = course_repo
        self._student_repo = student_repo
        self._enrollment_repo = enrollment_repo
        self._lesson_repo = lesson_repo
        self._test_repo = test_repo
        self._certificate_repo = certificate_repo
        self._payment_repo = payment_repo
    
    def create_course(
        self,
        title: str,
        description: str,
        price: float,
        level: CourseLevel,
        duration_hours: int
    ) -> Course:
        self._validate_course_data(title, description, price, level, duration_hours)
        
        course = Course()
        course.title = title
        course.description = description
        course.price = price
        course.level = level
        course.duration_hours = duration_hours
        course.is_active = True
        
        saved = self._course_repo.save(course)
        
        logger.info(
            "Course created",
            extra={"extra_data": {
                "course_id": saved.id,
                "title": title,
                "price": price,
                "level": level.value
            }}
        )
        return saved
    
    def get_course(self, course_id: int) -> Course:
        course = self._course_repo.find_by_id(course_id)
        if not course:
            raise CourseNotFoundError(f"Course with id {course_id} not found")
        return course
    
    def search_courses(self, query: str) -> List[Course]:
        if not query or len(query.strip()) < 2:
            return []
        return self._course_repo.search_by_title(query)
    
    def get_courses_by_level(self, level: CourseLevel) -> List[Course]:
        return self._course_repo.find_by_level(level)
    
    def delete_course(self, course_id: int):
        course = self.get_course(course_id)
        
        enrollments = self._enrollment_repo.find_by_course(course_id)
        active_enrollments = [e for e in enrollments 
                             if e.status in [EnrollmentStatus.ACTIVE, EnrollmentStatus.PENDING]]
        
        if active_enrollments:
            raise CourseHasStudentsError(
                f"Cannot delete course with {len(active_enrollments)} active enrollments"
            )
        
        lessons = self._lesson_repo.find_by_course(course_id)
        for lesson in lessons:
            self._lesson_repo.delete(lesson.id)
        
        deleted = self._course_repo.delete(course_id)
        if not deleted:
            raise CourseNotFoundError(f"Course with id {course_id} not found")
        
        logger.info(
            "Course deleted",
            extra={"extra_data": {"course_id": course_id, "title": course.title}}
        )
    
    def register_student(self, name: str, email: str, phone: str) -> Student:
        self._validate_student_data(name, email, phone)
        
        existing = self._student_repo.find_by_email(email)
        if existing:
            raise ValidationError(f"Student with email {email} already exists")
        
        student = Student()
        student.name = name
        student.email = email
        student.phone = phone
        student.is_active = True
        
        saved = self._student_repo.save(student)
        
        logger.info(
            "Student registered",
            extra={"extra_data": {"student_id": saved.id, "email": email}}
        )
        return saved
    
    def get_student(self, student_id: int) -> Student:
        student = self._student_repo.find_by_id(student_id)
        if not student:
            raise StudentNotFoundError(f"Student with id {student_id} not found")
        return student
    
    def enroll_student(self, student_id: int, course_id: int) -> Enrollment:
        student = self.get_student(student_id)
        course = self.get_course(course_id)
        
        if not student.is_active:
            raise StudentNotActiveError(f"Student {student_id} is not active")
        
        if not course.is_active:
            raise CourseNotActiveError(f"Course {course_id} is not active")
        
        existing = self._enrollment_repo.find_by_student_and_course(student_id, course_id)
        if existing:
            raise DuplicateEnrollmentError(
                f"Student {student_id} is already enrolled in course {course_id}"
            )
        
        payment = self._payment_repo.find_by_student_and_course(student_id, course_id)
        if not payment or payment.status != PaymentStatus.COMPLETED:
            raise PaymentRequiredError(
                f"Student {student_id} has not paid for course {course_id}"
            )
        
        enrollment = Enrollment()
        enrollment.student_id = student_id
        enrollment.course_id = course_id
        enrollment.status = EnrollmentStatus.ACTIVE
        enrollment.progress_percent = 0
        
        saved = self._enrollment_repo.save(enrollment)
        
        logger.info(
            "Student enrolled in course",
            extra={"extra_data": {
                "student_id": student_id,
                "course_id": course_id,
                "enrollment_id": saved.id
            }}
        )
        return saved
    
    def update_progress(self, enrollment_id: int, progress_percent: int) -> Enrollment:
        enrollment = self._enrollment_repo.find_by_id(enrollment_id)
        if not enrollment:
            raise EnrollmentNotFoundError(f"Enrollment with id {enrollment_id} not found")
        
        if not 0 <= progress_percent <= 100:
            raise ProgressNotValidError("Progress must be between 0 and 100")
        
        enrollment.progress_percent = progress_percent
        
        if progress_percent == 100:
            enrollment.status = EnrollmentStatus.COMPLETED
            enrollment.completed_at = datetime.now()
            logger.info(
                "Course completed by student",
                extra={"extra_data": {
                    "enrollment_id": enrollment_id,
                    "student_id": enrollment.student_id,
                    "course_id": enrollment.course_id
                }}
            )
        
        saved = self._enrollment_repo.update(enrollment)
        return saved
    
    def get_student_courses(self, student_id: int) -> List[Enrollment]:
        self.get_student(student_id)
        return self._enrollment_repo.find_by_student(student_id)
    
    def add_lesson(
        self,
        course_id: int,
        title: str,
        content: str,
        duration_minutes: int
    ) -> Lesson:
        course = self.get_course(course_id)
        
        self._validate_lesson_data(title, content, duration_minutes)
        
        existing_lessons = self._lesson_repo.find_by_course(course_id)
        next_order = len(existing_lessons) + 1
        
        lesson = Lesson()
        lesson.course_id = course_id
        lesson.title = title
        lesson.content = content
        lesson.duration_minutes = duration_minutes
        lesson.order_number = next_order
        
        saved = self._lesson_repo.save(lesson)
        
        logger.info(
            "Lesson added to course",
            extra={"extra_data": {
                "course_id": course_id,
                "lesson_id": saved.id,
                "title": title
            }}
        )
        return saved
    
    def get_course_lessons(self, course_id: int) -> List[Lesson]:
        self.get_course(course_id)
        return self._lesson_repo.find_by_course(course_id)
    
    def add_test_to_lesson(
        self,
        lesson_id: int,
        questions: List[Dict[str, Any]]
    ) -> Test:
        lesson = self._lesson_repo.find_by_id(lesson_id)
        if not lesson:
            raise LessonNotFoundError(f"Lesson with id {lesson_id} not found")
        
        self._validate_test_data(questions)
        
        existing = self._test_repo.find_by_lesson(lesson_id)
        if existing:
            raise ValidationError(f"Lesson {lesson_id} already has a test")
        
        test = Test()
        test.lesson_id = lesson_id
        test.questions = questions
        
        saved = self._test_repo.save(test)
        
        logger.info(
            "Test added to lesson",
            extra={"extra_data": {
                "lesson_id": lesson_id,
                "test_id": saved.id,
                "questions_count": len(questions)
            }}
        )
        return saved
    
    def submit_test(
        self,
        test_id: int,
        student_id: int,
        answers: List[int]
    ) -> Dict[str, Any]:
        test = self._test_repo.find_by_id(test_id)
        if not test:
            raise TestNotFoundError(f"Test with id {test_id} not found")
        
        lesson = self._lesson_repo.find_by_id(test.lesson_id)
        if not lesson:
            raise LessonNotFoundError(f"Lesson with id {test.lesson_id} not found")
        
        enrollment = self._enrollment_repo.find_by_student_and_course(
            student_id, lesson.course_id
        )
        if not enrollment or enrollment.status == EnrollmentStatus.CANCELLED:
            raise ValidationError(
                f"Student {student_id} is not enrolled in course {lesson.course_id}"
            )
        
        correct_count = 0
        total_questions = len(test.questions)
        
        for i, (question, answer) in enumerate(zip(test.questions, answers)):
            if i < len(test.questions) and answer == question.get("correct_answer"):
                correct_count += 1
        
        score_percent = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        passed = score_percent >= 70
        
        result = {
            "test_id": test_id,
            "student_id": student_id,
            "total_questions": total_questions,
            "correct_answers": correct_count,
            "score_percent": score_percent,
            "passed": passed
        }
        
        logger.info(
            "Test submitted",
            extra={"extra_data": {
                "test_id": test_id,
                "student_id": student_id,
                "score": score_percent,
                "passed": passed
            }}
        )
        return result
    
    def issue_certificate(self, student_id: int, course_id: int) -> Certificate:
        student = self.get_student(student_id)
        course = self.get_course(course_id)
        
        enrollment = self._enrollment_repo.find_by_student_and_course(student_id, course_id)
        if not enrollment:
            raise EnrollmentNotFoundError(
                f"Student {student_id} is not enrolled in course {course_id}"
            )
        
        if enrollment.status != EnrollmentStatus.COMPLETED:
            raise BusinessRuleViolation(
                f"Student {student_id} has not completed course {course_id}"
            )
        
        existing = self._certificate_repo.find_by_student_and_course(student_id, course_id)
        if existing:
            raise CertificateAlreadyIssuedError(
                f"Certificate already issued for student {student_id} and course {course_id}"
            )
        
        certificate = Certificate()
        certificate.student_id = student_id
        certificate.course_id = course_id
        certificate.certificate_number = self._generate_certificate_number()
        certificate.verification_url = f"https://edu.example.com/verify/{certificate.certificate_number}"
        
        saved = self._certificate_repo.save(certificate)
        
        logger.info(
            "Certificate issued",
            extra={"extra_data": {
                "student_id": student_id,
                "course_id": course_id,
                "certificate_number": saved.certificate_number
            }}
        )
        return saved
    
    def verify_certificate(self, certificate_number: str) -> dict:
        certificate = self._certificate_repo.find_by_number(certificate_number)
        if not certificate:
            raise CertificateNotFoundError(f"Certificate {certificate_number} not found")
        
        student = self.get_student(certificate.student_id)
        course = self.get_course(certificate.course_id)
        
        return {
            "valid": True,
            "student_name": student.name,
            "course_title": course.title,
            "issued_at": certificate.issued_at.isoformat(),
            "verification_url": certificate.verification_url
        }
    
    def create_payment(
        self,
        student_id: int,
        course_id: int,
        amount: float,
        transaction_id: str
    ) -> Payment:
        student = self.get_student(student_id)
        course = self.get_course(course_id)
        
        if amount != course.price:
            raise ValidationError(
                f"Payment amount {amount} does not match course price {course.price}"
            )
        
        existing = self._payment_repo.find_by_student_and_course(student_id, course_id)
        if existing and existing.status == PaymentStatus.COMPLETED:
            raise ValidationError("Payment already completed for this course")
        
        payment = Payment()
        payment.student_id = student_id
        payment.course_id = course_id
        payment.amount = amount
        payment.status = PaymentStatus.COMPLETED
        payment.transaction_id = transaction_id
        
        saved = self._payment_repo.save(payment)
        
        logger.info(
            "Payment created",
            extra={"extra_data": {
                "student_id": student_id,
                "course_id": course_id,
                "amount": amount,
                "transaction_id": transaction_id
            }}
        )
        return saved
    
    def _validate_course_data(self, title, description, price, level, duration_hours):
        if not title or len(title.strip()) < 3:
            raise ValidationError("Course title must be at least 3 characters")
        if not description or len(description.strip()) < 10:
            raise ValidationError("Course description must be at least 10 characters")
        if price < 0:
            raise ValidationError("Course price cannot be negative")
        if duration_hours <= 0:
            raise ValidationError("Course duration must be positive")
        if not isinstance(level, CourseLevel):
            raise ValidationError("Invalid course level")
    
    def _validate_student_data(self, name, email, phone):
        if not name or len(name.strip()) < 2:
            raise ValidationError("Student name must be at least 2 characters")
        if not email or "@" not in email or "." not in email:
            raise ValidationError("Invalid email format")
        if not phone or len(phone.strip()) < 5:
            raise ValidationError("Invalid phone number")
    
    def _validate_lesson_data(self, title, content, duration_minutes):
        if not title or len(title.strip()) < 3:
            raise ValidationError("Lesson title must be at least 3 characters")
        if not content or len(content.strip()) < 10:
            raise ValidationError("Lesson content must be at least 10 characters")
        if duration_minutes <= 0:
            raise ValidationError("Lesson duration must be positive")
    
    def _validate_test_data(self, questions):
        if not questions or len(questions) < 1:
            raise ValidationError("Test must have at least one question")
        for i, q in enumerate(questions):
            if "question" not in q or not q["question"].strip():
                raise ValidationError(f"Question {i+1} has no question text")
            if "options" not in q or len(q["options"]) < 2:
                raise ValidationError(f"Question {i+1} must have at least 2 options")
            if "correct_answer" not in q or not 0 <= q["correct_answer"] < len(q["options"]):
                raise ValidationError(f"Question {i+1} has invalid correct answer")
    
    def _generate_certificate_number(self) -> str:
        return f"CERT-{uuid.uuid4().hex[:12].upper()}"