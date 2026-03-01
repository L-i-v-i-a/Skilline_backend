# courses/urls.py
from django.urls import path
from .views import (
    CourseListView, CourseDetailView, CourseMaterialListView, EnrollCourseView, PaymentInitiateView,
    PaymentCallbackView, AssignmentListView, SubmitAssignmentView,
    StudentResultsView, NotificationListView, MarkNotificationReadView,
    InstructorCourseListView, InstructorCourseCreateView, InstructorCourseUpdateView,
    AssignmentCreateView, CourseStudentsView, AssignmentSubmissionsView,
    GradeSubmissionView, CourseMaterialCreateView
)

urlpatterns = [
    # Courses
    path('courses/', CourseListView.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),

    # Enrollment
    path('enroll/<int:course_id>/', EnrollCourseView.as_view(), name='enroll-course'),

    # Payments (Paystack)
    path('payments/initiate/<int:enrollment_id>/', PaymentInitiateView.as_view(), name='payment-initiate'),
    path('payments/callback/', PaymentCallbackView.as_view(), name='payment-callback'),

    # Assignments
    path('courses/<int:course_id>/assignments/', AssignmentListView.as_view(), name='assignment-list'),
    path('assignments/<int:assignment_id>/submit/', SubmitAssignmentView.as_view(), name='submit-assignment'),
    path('instructor/courses/<int:course_id>/materials/create/', CourseMaterialCreateView.as_view(), name='material-create'),
    path('courses/<int:course_id>/materials/', CourseMaterialListView.as_view(), name='material-list'),  # For students

    # Results
    path('results/', StudentResultsView.as_view(), name='student-results'),

    # Notifications (extra)
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/read/', MarkNotificationReadView.as_view(), name='notification-read'),
    # Instructor Courses
    path('instructor/courses/', InstructorCourseListView.as_view(), name='instructor-course-list'),
    path('instructor/courses/create/', InstructorCourseCreateView.as_view(), name='instructor-course-create'),
    path('instructor/courses/<int:pk>/update/', InstructorCourseUpdateView.as_view(), name='instructor-course-update'),

    # Assignments
    path('instructor/courses/<int:course_id>/assignments/create/', AssignmentCreateView.as_view(), name='assignment-create'),

    # Students
    path('instructor/courses/<int:course_id>/students/', CourseStudentsView.as_view(), name='course-students'),

    # Submissions
    path('instructor/assignments/<int:assignment_id>/submissions/', AssignmentSubmissionsView.as_view(), name='assignment-submissions'),
    path('instructor/submissions/<int:pk>/grade/', GradeSubmissionView.as_view(), name='grade-submission'),
]