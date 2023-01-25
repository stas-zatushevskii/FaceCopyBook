from django.db import models
from profiles.models import Profile
from django.core.validators import FileExtensionValidator


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='posts'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])],
        blank=True
    )
    liked = models.ManyToManyField(
        Profile,
        related_name='likes',
        blank=True
    )

    def __str__(self):
        return self.text[:15]

    def num_likes(self):
        return self.liked.all().count()

    def num_comments(self):
        return self.comments.all().count()

    class Meta:
        ordering = ['-pub_date']


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.SET_NULL,
        null=True,
        related_name='comments'
    )
    author = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='Текст коментария'
    )
    created = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return str(self.pk)


LIKES_CHOICES = (
    ('Like', 'Like'),
    ['Unlike', 'Unlike']
)


class Like(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.SET_NULL,
        null=True,
    )
    value = models.CharField(
        max_length=7,
        choices=LIKES_CHOICES
    )
    author = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )

    def __str__(self):
        return f'{self.author}-{self.post}-{self.value}'