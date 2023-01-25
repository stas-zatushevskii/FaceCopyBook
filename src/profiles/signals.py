from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, Relationship
from django.db.models import Q

@receiver(post_save, sender=User)
def post_save_create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Relationship)
def post_save_relationship(sender, instance, created, **kwargs):
    if created:
        sender_ = instance.sender
        recipient_ = instance.recipient
        if instance.status == 'accepted':
            sender_.friends.add(recipient_.user)
            recipient_.friends.add(sender_.user)
            sender_.save()
            recipient_.save()

@receiver(pre_delete, sender=Relationship)
def pre_delete_relationship(sender, instance, **kwargs):
    sender = instance.sender
    recipient = instance.recipient
    sender.friends.remove(recipient.user)
    recipient.friends.remove(sender.user)
    sender.save()
    recipient.save()