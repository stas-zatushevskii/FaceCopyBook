from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify
from .utils import ru_to_eng_slug
from django.shortcuts import reverse


User = get_user_model()


class ProfileManager(models.Manager):

    def get_all_profiles_to_invite(self, sender):
        # получаем все профили кроме нашего
        profiles = Profile.objects.all().exclude(user=sender)
        # получаем наш профиль
        profile = Profile.objects.get(user=sender)
        # получаем все созданные отношения в которых задействован наш профиль
        qs = Relationship.objects.filter(Q(sender=profile) | Q(recipient=profile))
        accepted = []
        for obj in qs:
            if obj.status == 'accepted':
                accepted.append(obj.recipient)
                accepted.append(obj.sender)

        # убираем все кроме не принятых
        available = [profile for profile in profiles if not profile in accepted]
        return available

    def get_profiles(self, user):
        result = Profile.objects.all().exclude(user=user)
        return result


class Profile(models.Model):
    first_name = models.CharField(max_length=200, default='NoName', blank=True)
    last_name = models.CharField(max_length=200, default='NoFirstName', blank=True)
    bio = models.TextField(max_length=600, blank=True)
    email = models.EmailField(blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    friends = models.ManyToManyField(User, blank=True, related_name='friends')
    country = models.CharField(max_length=200, blank=True)
    avatar = models.ImageField(default='avatar.png', upload_to='avatars/')
    slug = models.SlugField(unique=True, blank=True)

    objects = ProfileManager()

    def __str__(self):
        return f'{self.user.username}'

    def get_absolute_url(self):
        return reverse("profiles:profile-detail", kwargs={"slug": self.slug})

    __initial_first_name = None
    __initial_last_name = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initial_first_name = self.first_name
        self.__initial_last_name = self.last_name

    def save(self, *args, **kwargs):
        to_slug = self.slug
        if self.first_name != self.__initial_first_name or self.last_name != self.__initial_last_name or self.slug=="":
            to_slug = slugify(str(ru_to_eng_slug(self.first_name)) + ' ' + str(ru_to_eng_slug(self.last_name)))
            exist = Profile.objects.filter(slug=to_slug)
            if exist:
                to_slug = slugify(str(ru_to_eng_slug(self.first_name)) + ' ' + str(ru_to_eng_slug(self.last_name)) + str(self.user.id))
            self.slug = to_slug
        super().save(*args, **kwargs)

    def get_friends(self):
        return self.friends.all()

    def get_friends_num(self):
        return self.friends.all().count()

    def get_posts(self):
        return self.posts.all()

    def get_posts_num(self):
        return self.posts.all().count()

    def get_likes_given(self):
        likes = self.like_set.all()
        num = 0
        for i in likes:
            if i.value == 'Like':
                num += 1
        return num

    def get_likes_recived(self):
        posts = self.posts.all()
        num = 0
        for obj in posts:
            num = obj.liked.all().count()
        return num

CHOICES = (
    ('send', 'send'),
    ('accepted', 'accepted')
)


class RelationshipManager(models.Manager):
    def invitation_received(self, recipient):
        qs = Relationship.objects.filter(recipient=recipient, status='send')
        return qs


class Relationship(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender')
    recipient = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='recipient')
    status = models.CharField(max_length=8, choices=CHOICES)

    objects = RelationshipManager()