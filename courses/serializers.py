# courses/serializers.py
from rest_framework import serializers
from .models import Course, Enrollment, Assignment, Submission, Payment, Notification


class CourseSerializer(serializers.ModelSerializer):
    instructor = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'instructor', 'price', 'created_at', 'is_active']


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'course_id', 'enrolled_at', 'is_paid']

    def create(self, validated_data):
        course_id = validated_data.pop('course_id')
        course = Course.objects.get(id=course_id)
        return Enrollment.objects.create(student=self.context['request'].user, course=course, **validated_data)


class AssignmentSerializer(serializers.ModelSerializer):
    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'due_date', 'max_score', 'file', 'created_at', 'course']


class SubmissionSerializer(serializers.ModelSerializer):
    assignment = AssignmentSerializer(read_only=True)
    assignment_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Submission
        fields = ['id', 'assignment', 'assignment_id', 'file', 'submitted_at', 'grade', 'feedback']

    def create(self, validated_data):
        assignment_id = validated_data.pop('assignment_id')
        assignment = Assignment.objects.get(id=assignment_id)
        return Submission.objects.create(student=self.context['request'].user, assignment=assignment, **validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    enrollment = EnrollmentSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'enrollment', 'amount', 'transaction_id', 'status', 'paid_at', 'metadata']


class PaymentInitiateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']