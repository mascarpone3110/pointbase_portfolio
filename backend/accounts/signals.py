from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from points.models import PointManager
from .models import UserProfile, User


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_related_models(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        PointManager.objects.create(user=instance)

