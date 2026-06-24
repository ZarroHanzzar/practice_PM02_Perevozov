import pytest
from unittest.mock import Mock
from datetime import datetime

from interfaces import (
    Course, Student, Enrollment, Lesson, Test, Certificate, Payment,
    CourseLevel, EnrollmentStatus, PaymentStatus
)
from services import EducationPortalService
from exceptions import (
    CourseNotFoundError, StudentNotFoundError, EnrollmentNotFoundError,
    DuplicateEnrollmentError, CourseNotActiveError, StudentNotActiveError,
    PaymentRequiredError, ProgressNotValidError, CertificateAlreadyIssuedError,
    CourseHasStudentsError, ValidationError, BusinessRuleViolation,
    CertificateNotFoundError
)

@pytest.fixture
def mock_repositories():
    return {
        "course_repo": Mock(),
        "student_repo": Mock(),
        "enrollment_repo": Mock(),
        "lesson_repo": Mock(),
        "test_repo": Mock(),
        "certificate_repo": Mock(),
        "payment_repo": Mock()
    }

@pytest.fixture
def service(mock_repositories):
    return EducationPortalService(**mock_repositories)

@pytest.fixture
def sample_course():
    course = Course()
    course.id = 1
    course.title = "Python Programming"
    course.description = "Learn Python from scratch"
    course.price = 99.99
    course.level = CourseLevel.BEGINNER
    course.duration_hours = 40
    course.is_active = True
    course.created_at = datetime.now()
    return course

@pytest.fixture
def sample_student():
    student = Student()
    student.id = 1
    student.name = "John Doe"
    student.email = "john@example.com"
    student.phone = "+79111234567"
    student.is_active = True
    student.registered_at = datetime.now()
    return student

@pytest.fixture
def sample_enrollment():
    enrollment = Enrollment()
    enrollment.id = 1
    enrollment.student_id = 1
    enrollment.course_id = 1
    enrollment.status = EnrollmentStatus.ACTIVE
    enrollment.progress_percent = 0
    enrollment.enrollment_date = datetime.now()
    return enrollment

@pytest.fixture
def sample_certificate():
    certificate = Certificate()
    certificate.id = 1
    certificate.student_id = 1
    certificate.course_id = 1
    certificate.certificate_number = "CERT-ABC123"
    certificate.issued_at = datetime.now()
    certificate.verification_url = "https://edu.example.com/verify/CERT-ABC123"
    return certificate

class TestCourseManagement:
    def test_create_course_success(self, service, mock_repositories):
        course = Course()
        course.id = 1
        course.title = "Python Programming"
        course.description = "Learn Python from scratch"
        course.price = 99.99
        course.level = CourseLevel.BEGINNER
        course.duration_hours = 40
        course.is_active = True
        course.created_at = datetime.now()
        
        mock_repositories["course_repo"].save.return_value = course
        
        result = service.create_course(
            title="Python Programming",
            description="Learn Python from scratch",
            price=99.99,
            level=CourseLevel.BEGINNER,
            duration_hours=40
        )
        assert result.title == "Python Programming"
        mock_repositories["course_repo"].save.assert_called_once()
    
    def test_create_course_invalid_data(self, service):
        with pytest.raises(ValidationError):
            service.create_course(
                title="Py",
                description="Learn",
                price=99.99,
                level=CourseLevel.BEGINNER,
                duration_hours=40
            )
    
    def test_get_course_not_found(self, service, mock_repositories):
        mock_repositories["course_repo"].find_by_id.return_value = None
        with pytest.raises(CourseNotFoundError):
            service.get_course(999)
    
    def test_delete_course_with_active_enrollments(self, service, mock_repositories, sample_course):
        mock_repositories["course_repo"].find_by_id.return_value = sample_course
        
        enrollment = Enrollment()
        enrollment.id = 1
        enrollment.status = EnrollmentStatus.ACTIVE
        mock_repositories["enrollment_repo"].find_by_course.return_value = [enrollment]
        
        with pytest.raises(CourseHasStudentsError):
            service.delete_course(1)

class TestStudentManagement:
    def test_register_student_success(self, service, mock_repositories):
        mock_repositories["student_repo"].find_by_email.return_value = None
        
        student = Student()
        student.id = 1
        student.name = "John Doe"
        student.email = "john@example.com"
        student.phone = "+79111234567"
        student.is_active = True
        student.registered_at = datetime.now()
        mock_repositories["student_repo"].save.return_value = student
        
        result = service.register_student(
            name="John Doe",
            email="john@example.com",
            phone="+79111234567"
        )
        assert result.name == "John Doe"
        mock_repositories["student_repo"].save.assert_called_once()
    
    def test_register_student_duplicate_email(self, service, mock_repositories):
        mock_repositories["student_repo"].find_by_email.return_value = Student()
        with pytest.raises(ValidationError):
            service.register_student(
                name="John Doe",
                email="john@example.com",
                phone="+79111234567"
            )

class TestEnrollmentManagement:
    def test_enroll_student_success(self, service, mock_repositories, sample_course, sample_student):
        mock_repositories["course_repo"].find_by_id.return_value = sample_course
        mock_repositories["student_repo"].find_by_id.return_value = sample_student
        mock_repositories["enrollment_repo"].find_by_student_and_course.return_value = None
        
        payment = Payment()
        payment.id = 1
        payment.status = PaymentStatus.COMPLETED
        mock_repositories["payment_repo"].find_by_student_and_course.return_value = payment
        
        enrollment = Enrollment()
        enrollment.id = 1
        enrollment.student_id = 1
        enrollment.course_id = 1
        enrollment.status = EnrollmentStatus.ACTIVE
        enrollment.progress_percent = 0
        mock_repositories["enrollment_repo"].save.return_value = enrollment
        
        result = service.enroll_student(1, 1)
        assert result is not None
        mock_repositories["enrollment_repo"].save.assert_called_once()
    
    def test_enroll_student_no_payment(self, service, mock_repositories, sample_course, sample_student):
        mock_repositories["course_repo"].find_by_id.return_value = sample_course
        mock_repositories["student_repo"].find_by_id.return_value = sample_student
        mock_repositories["enrollment_repo"].find_by_student_and_course.return_value = None
        mock_repositories["payment_repo"].find_by_student_and_course.return_value = None
        
        with pytest.raises(PaymentRequiredError):
            service.enroll_student(1, 1)
    
    def test_update_progress_success(self, service, mock_repositories, sample_enrollment):
        mock_repositories["enrollment_repo"].find_by_id.return_value = sample_enrollment
        
        updated = Enrollment()
        updated.id = 1
        updated.student_id = 1
        updated.course_id = 1
        updated.status = EnrollmentStatus.ACTIVE
        updated.progress_percent = 50
        updated.enrollment_date = datetime.now()
        mock_repositories["enrollment_repo"].update.return_value = updated
        
        result = service.update_progress(1, 50)
        assert result.progress_percent == 50
    
    def test_update_progress_invalid(self, service, mock_repositories, sample_enrollment):
        mock_repositories["enrollment_repo"].find_by_id.return_value = sample_enrollment
        with pytest.raises(ProgressNotValidError):
            service.update_progress(1, 150)
    
    def test_update_progress_complete_course(self, service, mock_repositories, sample_enrollment):
        mock_repositories["enrollment_repo"].find_by_id.return_value = sample_enrollment
        
        completed = Enrollment()
        completed.id = 1
        completed.student_id = 1
        completed.course_id = 1
        completed.status = EnrollmentStatus.COMPLETED
        completed.progress_percent = 100
        completed.enrollment_date = datetime.now()
        completed.completed_at = datetime.now()
        mock_repositories["enrollment_repo"].update.return_value = completed
        
        result = service.update_progress(1, 100)
        assert result.status == EnrollmentStatus.COMPLETED

class TestCertificateManagement:
    def test_issue_certificate_success(self, service, mock_repositories, sample_course, sample_student):
        mock_repositories["course_repo"].find_by_id.return_value = sample_course
        mock_repositories["student_repo"].find_by_id.return_value = sample_student
        
        enrollment = Enrollment()
        enrollment.id = 1
        enrollment.student_id = 1
        enrollment.course_id = 1
        enrollment.status = EnrollmentStatus.COMPLETED
        enrollment.progress_percent = 100
        enrollment.enrollment_date = datetime.now()
        enrollment.completed_at = datetime.now()
        mock_repositories["enrollment_repo"].find_by_student_and_course.return_value = enrollment
        
        mock_repositories["certificate_repo"].find_by_student_and_course.return_value = None
        
        certificate = Certificate()
        certificate.id = 1
        certificate.student_id = 1
        certificate.course_id = 1
        certificate.certificate_number = "CERT-ABC123"
        certificate.issued_at = datetime.now()
        certificate.verification_url = "https://edu.example.com/verify/CERT-ABC123"
        mock_repositories["certificate_repo"].save.return_value = certificate
        
        result = service.issue_certificate(1, 1)
        assert result is not None
        assert result.certificate_number == "CERT-ABC123"
    
    def test_issue_certificate_not_completed(self, service, mock_repositories, sample_course, sample_student):
        mock_repositories["course_repo"].find_by_id.return_value = sample_course
        mock_repositories["student_repo"].find_by_id.return_value = sample_student
        
        enrollment = Enrollment()
        enrollment.id = 1
        enrollment.student_id = 1
        enrollment.course_id = 1
        enrollment.status = EnrollmentStatus.ACTIVE
        enrollment.progress_percent = 50
        enrollment.enrollment_date = datetime.now()
        mock_repositories["enrollment_repo"].find_by_student_and_course.return_value = enrollment
        
        with pytest.raises(BusinessRuleViolation):
            service.issue_certificate(1, 1)
    
    def test_verify_certificate_success(self, service, mock_repositories, sample_course, sample_student, sample_certificate):
        mock_repositories["certificate_repo"].find_by_number.return_value = sample_certificate
        mock_repositories["student_repo"].find_by_id.return_value = sample_student
        mock_repositories["course_repo"].find_by_id.return_value = sample_course
        
        result = service.verify_certificate("CERT-ABC123")
        assert result["valid"] is True
        assert result["student_name"] == "John Doe"
        assert result["course_title"] == "Python Programming"
    
    def test_verify_certificate_not_found(self, service, mock_repositories):
        mock_repositories["certificate_repo"].find_by_number.return_value = None
        with pytest.raises(CertificateNotFoundError):
            service.verify_certificate("CERT-INVALID")

class TestPaymentManagement:
    def test_create_payment_success(self, service, mock_repositories, sample_course, sample_student):
        mock_repositories["course_repo"].find_by_id.return_value = sample_course
        mock_repositories["student_repo"].find_by_id.return_value = sample_student
        mock_repositories["payment_repo"].find_by_student_and_course.return_value = None
        
        payment = Payment()
        payment.id = 1
        payment.student_id = 1
        payment.course_id = 1
        payment.amount = 99.99
        payment.status = PaymentStatus.COMPLETED
        payment.transaction_id = "TXN-123"
        payment.payment_date = datetime.now()
        mock_repositories["payment_repo"].save.return_value = payment
        
        result = service.create_payment(
            student_id=1,
            course_id=1,
            amount=99.99,
            transaction_id="TXN-123"
        )
        assert result is not None
        assert result.transaction_id == "TXN-123"

    def test_create_payment_wrong_amount(self, service, mock_repositories, sample_course, sample_student):
        mock_repositories["course_repo"].find_by_id.return_value = sample_course
        mock_repositories["student_repo"].find_by_id.return_value = sample_student
        
        with pytest.raises(ValidationError):
            service.create_payment(
                student_id=1,
                course_id=1,
                amount=50.00,
                transaction_id="TXN-123"
            )

class TestLessonAndTestManagement:
    def test_add_lesson_success(self, service, mock_repositories, sample_course):
        mock_repositories["course_repo"].find_by_id.return_value = sample_course
        mock_repositories["lesson_repo"].find_by_course.return_value = []
        
        lesson = Lesson()
        lesson.id = 1
        lesson.course_id = 1
        lesson.title = "Introduction to Python"
        lesson.content = "Learn about Python basics"
        lesson.duration_minutes = 45
        lesson.order_number = 1
        mock_repositories["lesson_repo"].save.return_value = lesson
        
        result = service.add_lesson(
            course_id=1,
            title="Introduction to Python",
            content="Learn about Python basics",
            duration_minutes=45
        )
        assert result is not None
        assert result.title == "Introduction to Python"
    
    def test_submit_test_success(self, service, mock_repositories):
        test = Test()
        test.id = 1
        test.lesson_id = 1
        test.questions = [
            {"question": "Q1", "options": ["A", "B"], "correct_answer": 0},
            {"question": "Q2", "options": ["A", "B"], "correct_answer": 1}
        ]
        mock_repositories["test_repo"].find_by_id.return_value = test
        
        lesson = Lesson()
        lesson.id = 1
        lesson.course_id = 1
        mock_repositories["lesson_repo"].find_by_id.return_value = lesson
        
        enrollment = Enrollment()
        enrollment.id = 1
        enrollment.student_id = 1
        enrollment.course_id = 1
        enrollment.status = EnrollmentStatus.ACTIVE
        mock_repositories["enrollment_repo"].find_by_student_and_course.return_value = enrollment
        
        result = service.submit_test(test_id=1, student_id=1, answers=[0, 1])
        assert result["score_percent"] == 100
        assert result["passed"] is True
    
    def test_submit_test_fail(self, service, mock_repositories):
        test = Test()
        test.id = 1
        test.lesson_id = 1
        test.questions = [
            {"question": "Q1", "options": ["A", "B"], "correct_answer": 0},
            {"question": "Q2", "options": ["A", "B"], "correct_answer": 1}
        ]
        mock_repositories["test_repo"].find_by_id.return_value = test
        
        lesson = Lesson()
        lesson.id = 1
        lesson.course_id = 1
        mock_repositories["lesson_repo"].find_by_id.return_value = lesson
        
        enrollment = Enrollment()
        enrollment.id = 1
        enrollment.student_id = 1
        enrollment.course_id = 1
        enrollment.status = EnrollmentStatus.ACTIVE
        mock_repositories["enrollment_repo"].find_by_student_and_course.return_value = enrollment
        
        result = service.submit_test(test_id=1, student_id=1, answers=[1, 0])
        assert result["score_percent"] == 0
        assert result["passed"] is False