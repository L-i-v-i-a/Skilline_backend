# Example using Django signals (recommended for admin actions)
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User
from .models import Notification
from .views import notify_student

@receiver(post_save, sender=User)
def notify_new_user(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        # Notify admin(s)
        admins = User.objects.filter(is_superuser=True)
        for admin in admins:
            Notification.objects.create(
                user=admin,
                message=f"New user registered: {instance.get_full_name()} ({instance.role})"
            )
        # Notify student
        notify_student(
            instance,
            "Welcome to Skilline! Your account has been created. Please verify your email."
        )