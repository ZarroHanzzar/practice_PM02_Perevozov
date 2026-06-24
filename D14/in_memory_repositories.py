from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from interfaces import (
    Course, Student, Enrollment, Lesson, Test, Certificate, Payment,
    CourseRepository, StudentRepository, EnrollmentRepository,
    LessonRepository, TestRepository, CertificateRepository, PaymentRepository,
    CourseLevel, EnrollmentStatus, PaymentStatus
)

class InMemoryCourseRepository(CourseRepository):
    def __init__(self):
        self._courses: Dict[int, Course] = {}
        self._next_id = 1
    
    def save(self, course: Course) -> Course:
        if course.id is None:
            course.id = self._next_id
            self._next_id += 1
            course.created_at = datetime.now()
        self._courses[course.id] = course
        return course
    
    def find_by_id(self, course_id: int) -> Optional[Course]:
        return self._courses.get(course_id)
    
    def find_all(self, skip: int = 0, limit: int = 100) -> List[Course]:
        courses = list(self._courses.values())
        return courses[skip:skip + limit]
    
    def find_by_level(self, level: CourseLevel) -> List[Course]:
        return [c for c in self._courses.values() if c.level == level and c.is_active]
    
    def search_by_title(self, query: str) -> List[Course]:
        query_lower = query.lower()
        return [c for c in self._courses.values() 
                if query_lower in c.title.lower() and c.is_active]
    
    def delete(self, course_id: int) -> bool:
        if course_id in self._courses:
            del self._courses[course_id]
            return True
        return False
    
    def update(self, course: Course) -> Course:
        if course.id in self._courses:
            self._courses[course.id] = course
            return course
        raise ValueError(f"Course with id {course.id} not found")

class InMemoryStudentRepository(StudentRepository):
    def __init__(self):
        self._students: Dict[int, Student] = {}
        self._next_id = 1
    
    def save(self, student: Student) -> Student:
        if student.id is None:
            student.id = self._next_id
            self._next_id += 1
            student.registered_at = datetime.now()
        self._students[student.id] = student
        return student
    
    def find_by_id(self, student_id: int) -> Optional[Student]:
        return self._students.get(student_id)
    
    def find_by_email(self, email: str) -> Optional[Student]:
        for student in self._students.values():
            if student.email == email:
                return student
        return None
    
    def find_all(self, skip: int = 0, limit: int = 100) -> List[Student]:
        students = list(self._students.values())
        return students[skip:skip + limit]
    
    def update(self, student: Student) -> Student:
        if student.id in self._students:
            self._students[student.id] = student
            return student
        raise ValueError(f"Student with id {student.id} not found")

class InMemoryEnrollmentRepository(EnrollmentRepository):
    def __init__(self):
        self._enrollments: Dict[int, Enrollment] = {}
        self._next_id = 1
    
    def save(self, enrollment: Enrollment) -> Enrollment:
        if enrollment.id is None:
            enrollment.id = self._next_id
            self._next_id += 1
            enrollment.enrollment_date = datetime.now()
        self._enrollments[enrollment.id] = enrollment
        return enrollment
    
    def find_by_id(self, enrollment_id: int) -> Optional[Enrollment]:
        return self._enrollments.get(enrollment_id)
    
    def find_by_student_and_course(self, student_id: int, course_id: int) -> Optional[Enrollment]:
        for enrollment in self._enrollments.values():
            if enrollment.student_id == student_id and enrollment.course_id == course_id:
                return enrollment
        return None
    
    def find_by_student(self, student_id: int) -> List[Enrollment]:
        return [e for e in self._enrollments.values() if e.student_id == student_id]
    
    def find_by_course(self, course_id: int) -> List[Enrollment]:
        return [e for e in self._enrollments.values() if e.course_id == course_id]
    
    def update(self, enrollment: Enrollment) -> Enrollment:
        if enrollment.id in self._enrollments:
            self._enrollments[enrollment.id] = enrollment
            return enrollment
        raise ValueError(f"Enrollment with id {enrollment.id} not found")
    
    def find_active_by_student(self, student_id: int) -> List[Enrollment]:
        return [e for e in self._enrollments.values() 
                if e.student_id == student_id and e.status in 
                [EnrollmentStatus.ACTIVE, EnrollmentStatus.PENDING]]

class InMemoryLessonRepository(LessonRepository):
    def __init__(self):
        self._lessons: Dict[int, Lesson] = {}
        self._next_id = 1
    
    def save(self, lesson: Lesson) -> Lesson:
        if lesson.id is None:
            lesson.id = self._next_id
            self._next_id += 1
        self._lessons[lesson.id] = lesson
        return lesson
    
    def find_by_id(self, lesson_id: int) -> Optional[Lesson]:
        return self._lessons.get(lesson_id)
    
    def find_by_course(self, course_id: int) -> List[Lesson]:
        lessons = [l for l in self._lessons.values() if l.course_id == course_id]
        return sorted(lessons, key=lambda x: x.order_number)
    
    def delete(self, lesson_id: int) -> bool:
        if lesson_id in self._lessons:
            del self._lessons[lesson_id]
            return True
        return False
    
    def update(self, lesson: Lesson) -> Lesson:
        if lesson.id in self._lessons:
            self._lessons[lesson.id] = lesson
            return lesson
        raise ValueError(f"Lesson with id {lesson.id} not found")

class InMemoryTestRepository(TestRepository):
    def __init__(self):
        self._tests: Dict[int, Test] = {}
        self._next_id = 1
    
    def save(self, test: Test) -> Test:
        if test.id is None:
            test.id = self._next_id
            self._next_id += 1
        self._tests[test.id] = test
        return test
    
    def find_by_id(self, test_id: int) -> Optional[Test]:
        return self._tests.get(test_id)
    
    def find_by_lesson(self, lesson_id: int) -> Optional[Test]:
        for test in self._tests.values():
            if test.lesson_id == lesson_id:
                return test
        return None
    
    def update(self, test: Test) -> Test:
        if test.id in self._tests:
            self._tests[test.id] = test
            return test
        raise ValueError(f"Test with id {test.id} not found")

class InMemoryCertificateRepository(CertificateRepository):
    def __init__(self):
        self._certificates: Dict[int, Certificate] = {}
        self._next_id = 1
    
    def save(self, certificate: Certificate) -> Certificate:
        if certificate.id is None:
            certificate.id = self._next_id
            self._next_id += 1
            certificate.issued_at = datetime.now()
        self._certificates[certificate.id] = certificate
        return certificate
    
    def find_by_id(self, cert_id: int) -> Optional[Certificate]:
        return self._certificates.get(cert_id)
    
    def find_by_student_and_course(self, student_id: int, course_id: int) -> Optional[Certificate]:
        for cert in self._certificates.values():
            if cert.student_id == student_id and cert.course_id == course_id:
                return cert
        return None
    
    def find_by_student(self, student_id: int) -> List[Certificate]:
        return [c for c in self._certificates.values() if c.student_id == student_id]
    
    def find_by_number(self, cert_number: str) -> Optional[Certificate]:
        for cert in self._certificates.values():
            if cert.certificate_number == cert_number:
                return cert
        return None

class InMemoryPaymentRepository(PaymentRepository):
    def __init__(self):
        self._payments: Dict[int, Payment] = {}
        self._next_id = 1
    
    def save(self, payment: Payment) -> Payment:
        if payment.id is None:
            payment.id = self._next_id
            self._next_id += 1
            payment.payment_date = datetime.now()
        self._payments[payment.id] = payment
        return payment
    
    def find_by_id(self, payment_id: int) -> Optional[Payment]:
        return self._payments.get(payment_id)
    
    def find_by_student_and_course(self, student_id: int, course_id: int) -> Optional[Payment]:
        for payment in self._payments.values():
            if payment.student_id == student_id and payment.course_id == course_id:
                return payment
        return None
    
    def find_by_student(self, student_id: int) -> List[Payment]:
        return [p for p in self._payments.values() if p.student_id == student_id]
    
    def update(self, payment: Payment) -> Payment:
        if payment.id in self._payments:
            self._payments[payment.id] = payment
            return payment
        raise ValueError(f"Payment with id {payment.id} not found")