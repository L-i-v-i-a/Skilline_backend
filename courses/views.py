import os
import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from accounts.models import User
from .models import Course, Enrollment, Assignment, Submission, Payment, Notification
from .serializers import (
    AssignmentCreateSerializer, CourseSerializer, EnrollmentSerializer,
    AssignmentSerializer, InstructorCourseSerializer, StudentSerializer,
    SubmissionGradeSerializer, SubmissionSerializer, PaymentSerializer,
    PaymentInitiateSerializer, NotificationSerializer, CourseMaterialCreateSerializer, CourseMaterialSerializer
)
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
# Correct import for method_decorator
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


# ────────────────────────────────────────────────
# Helper Notification Functions
# ────────────────────────────────────────────────
def notify_student(student, message):
    """Create a notification for a student"""
    Notification.objects.create(user=student, message=message)


def notify_instructor(instructor, message):
    """Create a notification for an instructor"""
    Notification.objects.create(user=instructor, message=message)


def notify_admins(message):
    """Notify all superusers/admins (optional - call when needed)"""
    admins = User.objects.filter(is_superuser=True)
    for admin in admins:
        Notification.objects.create(user=admin, message=message)


# ────────────────────────────────────────────────
# Permissions
# ────────────────────────────────────────────────
class IsStudentPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_student


class IsInstructorPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_instructor


# ────────────────────────────────────────────────
# Student Views
# ────────────────────────────────────────────────
class CourseListView(generics.ListAPIView):
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="List available courses", tags=['Student - Courses'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="View course details", tags=['Student - Courses'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PaymentInitiateView(APIView):
    permission_classes = [IsStudentPermission]

    @extend_schema(
        summary="Initiate payment for enrollment using Paystack",
        request=PaymentInitiateSerializer,
        responses={200: OpenApiResponse(description="Paystack authorization URL")},
        tags=['Student - Payments']
    )
    def post(self, request, enrollment_id):
        enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user, is_paid=False)
        serializer = PaymentInitiateSerializer(data=request.data)
        if serializer.is_valid():
            amount = enrollment.course.price * 100  # Paystack uses kobo
            paystack_secret = os.getenv('PAYSTACK_SECRET_KEY')
            if not paystack_secret:
                return Response({"detail": "Paystack not configured."}, status=500)

            headers = {'Authorization': f'Bearer {paystack_secret}', 'Content-Type': 'application/json'}
            data = {
                'email': request.user.email,
                'amount': int(amount),
                'metadata': {'enrollment_id': enrollment.id},
                'callback_url': request.build_absolute_uri('/api/payments/callback/')
            }
            response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, json=data)
            if response.status_code == 200:
                auth_url = response.json()['data']['authorization_url']
                transaction_id = response.json()['data']['reference']
                Payment.objects.create(
                    enrollment=enrollment,
                    amount=enrollment.course.price,
                    transaction_id=transaction_id,
                    metadata=response.json()
                )
                return Response({"authorization_url": auth_url})
            return Response(response.json(), status=response.status_code)
        return Response(serializer.errors, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class PaymentCallbackView(APIView):
    permission_classes = [AllowAny]  # Paystack callback is public

    @extend_schema(
        summary="Paystack payment callback",
        parameters=[OpenApiParameter(name='reference', type=str, location=OpenApiParameter.QUERY)],
        responses={200: OpenApiResponse(description="Payment status")},
        tags=['Student - Payments']
    )
    def get(self, request):
        reference = request.query_params.get('reference')
        if not reference:
            return Response({"detail": "Reference required."}, status=400)

        paystack_secret = os.getenv('PAYSTACK_SECRET_KEY')
        headers = {'Authorization': f'Bearer {paystack_secret}'}
        response = requests.get(f'https://api.paystack.co/transaction/verify/{reference}', headers=headers)

        if response.status_code == 200:
            data = response.json()['data']
            payment = get_object_or_404(Payment, transaction_id=reference)

            if data['status'] == 'success':
                payment.status = 'success'
                payment.paid_at = timezone.now()
                payment.enrollment.is_paid = True
                payment.enrollment.save()
                payment.save()

                # Notify STUDENT
                notify_student(
                    payment.enrollment.student,
                    f"Payment successful! You are now fully enrolled in {payment.enrollment.course.title}."
                )

                # Notify INSTRUCTOR
                notify_instructor(
                    payment.enrollment.course.instructor,
                    f"New paid enrollment: {payment.enrollment.student.get_full_name()} "
                    f"successfully joined {payment.enrollment.course.title}"
                )

                # Optional: Notify admins
                notify_admins(
                    f"Payment success: {payment.enrollment.student.get_full_name()} "
                    f"paid for {payment.enrollment.course.title}"
                )

                return Response({"detail": "Payment successful."})
            
            payment.status = 'failed'
            payment.save()
            return Response({"detail": "Payment failed."}, status=400)

        return Response(response.json(), status=response.status_code)


class AssignmentListView(generics.ListAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]  
    @extend_schema(summary="View assignments for a course", tags=['Student - Assignments'])
    def get_queryset(self):
        course_id = self.kwargs['course_id']
        enrollment = get_object_or_404(Enrollment, course_id=course_id, student=self.request.user, is_paid=True)
        return Assignment.objects.filter(course=enrollment.course)


@method_decorator(csrf_exempt, name='dispatch')
class SubmitAssignmentView(APIView):
    permission_classes = [IsStudentPermission]

    @extend_schema(
        summary="Submit assignment",
        request=SubmissionSerializer,
        responses=SubmissionSerializer,
        tags=['Student - Assignments']
    )
    def post(self, request, assignment_id):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        if not Enrollment.objects.filter(student=request.user, course=assignment.course, is_paid=True).exists():
            raise PermissionDenied("Not enrolled in this course.")

        serializer = SubmissionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            submission = serializer.save()

            # Notify INSTRUCTOR about new submission
            notify_instructor(
                assignment.course.instructor,
                f"New submission received for '{assignment.title}' from {request.user.get_full_name()}"
            )

            # Notify STUDENT (confirmation)
            notify_student(
                request.user,
                f"Your submission for '{assignment.title}' has been successfully received. "
                f"You will be notified when it is graded."
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentResultsView(generics.ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [IsStudentPermission]

    @extend_schema(summary="View results/grades", tags=['Student - Results'])
    def get_queryset(self):
        return Submission.objects.filter(student=self.request.user).order_by('-submitted_at')


# ────────────────────────────────────────────────
# Notifications (shared for all roles)
# ────────────────────────────────────────────────
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="View your notifications", tags=['Notifications'])
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Mark a notification as read", tags=['Notifications'])
    def patch(self, request, pk):
        notification = get_object_or_404(Notification, id=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({"detail": "Marked as read."})


# ────────────────────────────────────────────────
# Instructor Views
# ────────────────────────────────────────────────
class InstructorCourseListView(generics.ListAPIView):
    serializer_class = InstructorCourseSerializer
    permission_classes = [IsInstructorPermission]

    @extend_schema(summary="List your courses", tags=['Instructor - Courses'])
    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)


@method_decorator(csrf_exempt, name='dispatch')
class InstructorCourseCreateView(APIView):
    permission_classes = [IsInstructorPermission]

    @extend_schema(
        summary="Create new course (supports image/video upload)",
        request=InstructorCourseSerializer,
        responses=InstructorCourseSerializer,
        tags=['Instructor - Courses']
    )
    def post(self, request):
        serializer = InstructorCourseSerializer(data=request.data)
        if serializer.is_valid():
            course = serializer.save(instructor=request.user)
            notify_instructor(
                request.user,
                f"You successfully created the course: {course.title}"
            )
            notify_admins(f"New course created: {course.title} by {request.user.get_full_name()}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class InstructorCourseUpdateView(generics.UpdateAPIView):
    serializer_class = InstructorCourseSerializer
    permission_classes = [IsInstructorPermission]

    @extend_schema(summary="Update your course (supports image/video)", tags=['Instructor - Courses'])
    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)

    def perform_update(self, serializer):
        course = serializer.save()
        notify_instructor(
            self.request.user,
            f"You updated the course: {course.title}"
        )


@method_decorator(csrf_exempt, name='dispatch')
class AssignmentCreateView(APIView):
    permission_classes = [IsInstructorPermission]

    @extend_schema(
        summary="Create assignment for your course (supports file/video)",
        request=AssignmentCreateSerializer,
        responses=AssignmentCreateSerializer,
        tags=['Instructor - Assignments']
    )
    def post(self, request, course_id):
        serializer = AssignmentCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            assignment = serializer.save()

            # Notify instructor (confirmation)
            notify_instructor(
                request.user,
                f"You created a new assignment '{assignment.title}' in {assignment.course.title}"
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseStudentsView(generics.ListAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsInstructorPermission]

    @extend_schema(summary="List enrolled students in your course", tags=['Instructor - Courses'])
    def get_queryset(self):
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id, instructor=self.request.user)
        return User.objects.filter(enrollments__course=course, enrollments__is_paid=True)


class AssignmentSubmissionsView(generics.ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [IsInstructorPermission]

    @extend_schema(summary="List submissions for your assignment", tags=['Instructor - Assignments'])
    def get_queryset(self):
        assignment_id = self.kwargs['assignment_id']
        assignment = get_object_or_404(Assignment, id=assignment_id, course__instructor=self.request.user)
        return Submission.objects.filter(assignment=assignment)


@method_decorator(csrf_exempt, name='dispatch')
class GradeSubmissionView(generics.UpdateAPIView):
    serializer_class = SubmissionGradeSerializer
    permission_classes = [IsInstructorPermission]

    @extend_schema(summary="Grade a student submission", tags=['Instructor - Assignments'])
    def get_queryset(self):
        return Submission.objects.filter(assignment__course__instructor=self.request.user)

    def perform_update(self, serializer):
        submission = serializer.save()

        # Notify STUDENT about the grade
        notify_student(
            submission.student,
            f"Your submission for '{submission.assignment.title}' has been graded: "
            f"Score: {submission.grade}/{submission.assignment.max_score}. "
            f"Feedback: {submission.feedback or 'None'}"
        )

        # Notify INSTRUCTOR (confirmation)
        notify_instructor(
            self.request.user,
            f"You graded submission from {submission.student.get_full_name()} "
            f"for '{submission.assignment.title}' → Score: {submission.grade}"
        )


# Update views.py to add new views
# courses/views.py (add to existing)

@method_decorator(csrf_exempt, name='dispatch')
class CourseMaterialCreateView(APIView):
    permission_classes = [IsInstructorPermission]

    @extend_schema(
        summary="Add course material (supports file/video upload)",
        request=CourseMaterialCreateSerializer,
        responses=CourseMaterialSerializer,
        tags=['Instructor - Materials']
    )
    def post(self, request, course_id):
        serializer = CourseMaterialCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            material = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseMaterialListView(generics.ListAPIView):
    serializer_class = CourseMaterialSerializer
    permission_classes = [IsAuthenticated]  # Anyone can view, but check enrollment for private

    @extend_schema(summary="List materials for a course", tags=['Student - Materials'])
    def get_queryset(self):
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id, is_active=True)
        # If student, check enrollment
        if self.request.user.is_student:
            get_object_or_404(Enrollment, course=course, student=self.request.user, is_paid=True)
        # If instructor, check ownership
        elif self.request.user.is_instructor:
            if course.instructor != self.request.user:
                raise PermissionDenied("Not your course.")
        # Admins can always view
        elif not self.request.user.is_admin:
            raise PermissionDenied("Access denied.")

        return course.materials.all().order_by('-created_at')


# Update existing EnrollCourseView to prevent duplicate enrollments (already does, but emphasize)
class EnrollCourseView(APIView):
    permission_classes = [IsStudentPermission]

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, is_active=True)
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response({"detail": "Already enrolled. Cannot enroll again."}, status=status.HTTP_400_BAD_REQUEST)
        enrollment = Enrollment.objects.create(student=request.user, course=course)
        serializer = EnrollmentSerializer(enrollment)

        notify_instructor(
            course.instructor,
            f"New enrollment request (unpaid) from {request.user.get_full_name()} for {course.title}"
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Update CourseListView to be public (AllowAny) for "everyone to view all courses"
class CourseListView(generics.ListAPIView):
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]  # ← Change to AllowAny for public access

    @extend_schema(summary="List all available courses (public)", tags=['Public - Courses'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)