class DomainError(Exception):
    pass

class ValidationError(DomainError):
    pass

class NotFoundError(DomainError):
    pass

class BusinessRuleViolation(DomainError):
    pass

class CourseNotFoundError(NotFoundError):
    pass

class StudentNotFoundError(NotFoundError):
    pass

class EnrollmentNotFoundError(NotFoundError):
    pass

class LessonNotFoundError(NotFoundError):
    pass

class TestNotFoundError(NotFoundError):
    pass

class CertificateNotFoundError(NotFoundError):
    pass

class DuplicateEnrollmentError(BusinessRuleViolation):
    pass

class CourseNotActiveError(BusinessRuleViolation):
    pass

class StudentNotActiveError(BusinessRuleViolation):
    pass

class PaymentRequiredError(BusinessRuleViolation):
    pass

class ProgressNotValidError(BusinessRuleViolation):
    pass

class CertificateAlreadyIssuedError(BusinessRuleViolation):
    pass

class CourseHasStudentsError(BusinessRuleViolation):
    pass