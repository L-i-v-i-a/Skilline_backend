# courses/serializers.py
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Course, Enrollment, Assignment, Submission, Payment, Notification, CourseMaterial
from .views import notify_student
class CourseMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMaterial
        fields = ['id', 'title', 'description', 'file', 'video', 'created_at', 'is_public']
class CourseSerializer(serializers.ModelSerializer): 
    materials = CourseMaterialSerializer(many=True, read_only=True)
    instructor = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'instructor', 'price', 'cover_image', 'intro_video', 'created_at', 'is_active', 'materials']

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
        
# courses/serializers.py (add to existing)

class InstructorCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'price', 'cover_image', 'intro_video', 'created_at', 'is_active']

class AssignmentCreateSerializer(serializers.ModelSerializer):
    course_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'due_date', 'max_score', 'file', 'video', 'course_id']

    def create(self, validated_data):
        course_id = validated_data.pop('course_id')
        course = get_object_or_404(Course, id=course_id, instructor=self.context['request'].user)
        assignment = Assignment.objects.create(course=course, **validated_data)
        # Notify enrolled students
        for enrollment in course.enrollments.filter(is_paid=True):
            Notification.objects.create(
                user=enrollment.student,
                message=f"New assignment '{assignment.title}' in {course.title}. Due: {assignment.due_date}"
            )
        return assignment

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'matric_number', 'major']

class SubmissionGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['grade', 'feedback']

    def update(self, instance, validated_data):
        instance.grade = validated_data.get('grade', instance.grade)
        instance.feedback = validated_data.get('feedback', instance.feedback)
        instance.save()
        # Notify student
        Notification.objects.create(
            user=instance.student,
            message=f"Your submission for '{instance.assignment.title}' has been graded: {instance.grade}/{instance.assignment.max_score}. Feedback: {instance.feedback or 'None'}"
        )
        return instance
    
class CourseMaterialCreateSerializer(serializers.ModelSerializer):
    course_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CourseMaterial
        fields = ['id', 'title', 'description', 'file', 'video', 'is_public', 'course_id']

    def create(self, validated_data):
        course_id = validated_data.pop('course_id')
        course = get_object_or_404(Course, id=course_id, instructor=self.context['request'].user)
        material = CourseMaterial.objects.create(course=course, **validated_data)
        # Notify enrolled students
        for enrollment in course.enrollments.filter(is_paid=True):
            notify_student(
                enrollment.student,
                f"New material '{material.title}' added to {course.title}"
            )
        return material

