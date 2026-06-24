from in_memory_repositories import (
    InMemoryCourseRepository, InMemoryStudentRepository,
    InMemoryEnrollmentRepository, InMemoryLessonRepository,
    InMemoryTestRepository, InMemoryCertificateRepository,
    InMemoryPaymentRepository
)
from services import EducationPortalService
from interfaces import CourseLevel

def main():
    course_repo = InMemoryCourseRepository()
    student_repo = InMemoryStudentRepository()
    enrollment_repo = InMemoryEnrollmentRepository()
    lesson_repo = InMemoryLessonRepository()
    test_repo = InMemoryTestRepository()
    certificate_repo = InMemoryCertificateRepository()
    payment_repo = InMemoryPaymentRepository()
    
    service = EducationPortalService(
        course_repo=course_repo,
        student_repo=student_repo,
        enrollment_repo=enrollment_repo,
        lesson_repo=lesson_repo,
        test_repo=test_repo,
        certificate_repo=certificate_repo,
        payment_repo=payment_repo
    )
    
    course = service.create_course(
        title="Python Programming",
        description="Complete Python course",
        price=99.99,
        level=CourseLevel.BEGINNER,
        duration_hours=40
    )
    print(f"✅ Course created: {course.title} (ID: {course.id})")
    
    student = service.register_student(
        name="Alice Johnson",
        email="alice@example.com",
        phone="+79001234567"
    )
    print(f"✅ Student registered: {student.name} (ID: {student.id})")
    
    payment = service.create_payment(
        student_id=student.id,
        course_id=course.id,
        amount=99.99,
        transaction_id="TXN-123456"
    )
    print(f"✅ Payment created: {payment.transaction_id}")
    
    enrollment = service.enroll_student(
        student_id=student.id,
        course_id=course.id
    )
    print(f"✅ Student enrolled in course (Enrollment ID: {enrollment.id})")
    
    lesson1 = service.add_lesson(
        course_id=course.id,
        title="Introduction to Python",
        content="Learn about Python basics",
        duration_minutes=30
    )
    print(f"✅ Lesson added: {lesson1.title}")
    
    test = service.add_test_to_lesson(
        lesson_id=lesson1.id,
        questions=[
            {
                "question": "What is Python?",
                "options": ["Language", "Snake", "Framework", "Database"],
                "correct_answer": 0
            }
        ]
    )
    print(f"✅ Test added to lesson (ID: {test.id})")
    
    result = service.submit_test(
        test_id=test.id,
        student_id=student.id,
        answers=[0]
    )
    print(f"✅ Test submitted: Score {result['score_percent']}%")
    
    service.update_progress(enrollment_id=enrollment.id, progress_percent=100)
    print(f"✅ Course completed")
    
    certificate = service.issue_certificate(
        student_id=student.id,
        course_id=course.id
    )
    print(f"✅ Certificate issued: {certificate.certificate_number}")
    
    verification = service.verify_certificate(certificate.certificate_number)
    print(f"✅ Certificate verified: Student: {verification['student_name']}")

if __name__ == "__main__":
    main()