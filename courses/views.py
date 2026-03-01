# courses/views.py
import os
import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from .models import Course, Enrollment, Assignment, Submission, Payment, Notification
from .serializers import (
    CourseSerializer, EnrollmentSerializer, AssignmentSerializer,
    SubmissionSerializer, PaymentSerializer, PaymentInitiateSerializer,
    NotificationSerializer
)
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied


class IsStudentPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_student


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


class EnrollCourseView(APIView):
    permission_classes = [IsStudentPermission]

    @extend_schema(
        summary="Enroll in a course (creates unpaid enrollment)",
        request=EnrollmentSerializer,
        responses={201: EnrollmentSerializer},
        tags=['Student - Enrollment']
    )
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, is_active=True)
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response({"detail": "Already enrolled."}, status=status.HTTP_400_BAD_REQUEST)

        enrollment = Enrollment.objects.create(student=request.user, course=course)
        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
                return Response({"detail": "Paystack not configured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            headers = {
                'Authorization': f'Bearer {paystack_secret}',
                'Content-Type': 'application/json'
            }
            data = {
                'email': request.user.email,
                'amount': int(amount),
                'metadata': {'enrollment_id': enrollment.id},
                'callback_url': request.build_absolute_uri('/api/payments/callback/')  # Adjust URL
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentCallbackView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Paystack payment callback",
        parameters=[OpenApiParameter(name='reference', type=str, location=OpenApiParameter.QUERY)],
        responses={200: OpenApiResponse(description="Payment status")},
        tags=['Student - Payments']
    )
    def get(self, request):
        reference = request.query_params.get('reference')
        if not reference:
            return Response({"detail": "Reference required."}, status=status.HTTP_400_BAD_REQUEST)

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
                # Send notification
                Notification.objects.create(user=payment.enrollment.student, message=f"Payment successful for {payment.enrollment.course.title}")
                return Response({"detail": "Payment successful."})
            payment.status = 'failed'
            payment.save()
            return Response({"detail": "Payment failed."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(response.json(), status=response.status_code)


class AssignmentListView(generics.ListAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [IsStudentPermission]

    @extend_schema(summary="View assignments for a course", tags=['Student - Assignments'])
    def get_queryset(self):
        course_id = self.kwargs['course_id']
        enrollment = get_object_or_404(Enrollment, course_id=course_id, student=self.request.user, is_paid=True)
        return Assignment.objects.filter(course=enrollment.course)


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
            serializer.save()
            Notification.objects.create(user=assignment.course.instructor, message=f"New submission for {assignment.title} by {request.user}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentResultsView(generics.ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [IsStudentPermission]

    @extend_schema(summary="View results/grades", tags=['Student - Results'])
    def get_queryset(self):
        return Submission.objects.filter(student=self.request.user).order_by('-submitted_at')


# Extra: Notifications
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="View notifications", tags=['Student - Notifications'])
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Mark notification as read", tags=['Student - Notifications'])
    def patch(self, request, pk):
        notification = get_object_or_404(Notification, id=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({"detail": "Marked as read."})