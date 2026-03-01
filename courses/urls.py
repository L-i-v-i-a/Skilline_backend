# courses/urls.py
from django.urls import path
from .views import (
    CourseListView, CourseDetailView, EnrollCourseView, PaymentInitiateView,
    PaymentCallbackView, AssignmentListView, SubmitAssignmentView,
    StudentResultsView, NotificationListView, MarkNotificationReadView,
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

    # Results
    path('results/', StudentResultsView.as_view(), name='student-results'),

    # Notifications (extra)
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/read/', MarkNotificationReadView.as_view(), name='notification-read'),
]