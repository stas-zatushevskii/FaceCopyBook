from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Like, Profile


# когда создаеться модель Like она сразу обноваляет поле liked в модели Post
# для того чтобы отслеживать лайки на посте 
@receiver(post_save, sender=Like)
def post_save_create_profile(sender, instance, created, **kwargs):
    if created:
        profile = instance.author
        post = instance.post
        if instance.value == 'Like':
            post.liked.add(profile)
            post.save()