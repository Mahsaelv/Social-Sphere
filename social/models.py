from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from taggit.managers import TaggableManager
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# User = settings.AUTH_USER_MODEL


class User(AbstractUser):
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to="account_images/", blank=True, null=True)
    job = models.CharField(max_length=250, null=True, blank=True)
    following = models.ManyToManyField('self', through='Contact', related_name="followers", symmetrical=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_absolute_url(self):
        return reverse('social:user_detail', args=[self.username])

    def get_followers(self):
        return [contact.user_from for contact in self.rel_to_set.all().order_by('-created')]

    def get_followings(self):
        return [contact.user_to for contact in self.rel_from_set.all().order_by('-created')]


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_posts", verbose_name="نویسنده")
    description = models.TextField(verbose_name="توضیحات")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    saved_by = models.ManyToManyField(User, related_name='saved_posts', blank=True)
    total_likes = models.PositiveIntegerField(default=0)
    total_saves = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    tags = TaggableManager()

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['-total_likes'])
        ]
        verbose_name = "پست"
        verbose_name_plural = "پست ها"

    def __str__(self):
        return self.author.first_name + ": " + self.description[:10] + '...'

    def get_absolute_url(self):
        return reverse('social:post_detail', args=[self.id])

    def delete(self, *args, **kwargs):
        for img in self.images.all():
            storage, path = img.image_file.storage, img.image_file.path
            storage.delete(path)
        super().delete(*args, **kwargs)


class Contact(models.Model):
    user_from = models.ForeignKey(User, related_name='rel_from_set', on_delete=models.CASCADE)
    user_to = models.ForeignKey(User, related_name='rel_to_set', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['-created'])
        ]
        ordering = ('-created',)

    def __str__(self):
        return f"{self.user_from} follows {self.user_to}"


class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images", verbose_name="پست")
    image_file = models.ImageField(upload_to="post_images/")
    title = models.CharField(max_length=250, verbose_name="عنوان", null=True, blank=True)
    description = models.TextField(verbose_name="توضیحات", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created'])
        ]
        verbose_name = "تصویر"
        verbose_name_plural = "تصویر ها"

    def delete(self, *args, **kwargs):
        storage, path = self.image_file.storage, self.image_file.path
        storage.delete(path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.title if self.title else "None"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", verbose_name="پست")
    name = models.CharField(max_length=250, null=True, blank=True, verbose_name="نام")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_comments",
                             null=True, blank=True)
    body = models.TextField(verbose_name="متن کامنت")
    created = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated = models.DateTimeField(auto_now=True, verbose_name="تاریخ ویرایش")
    active = models.BooleanField(default=True, verbose_name="وضعیت")

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created'])
        ]
        verbose_name_plural = "کامنت ها"

    def __str__(self):
        return f"{self.name}: {self.post}"


class Thread(models.Model):
    participants = models.ManyToManyField(User, related_name='threads')
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Thread {self.id}"


class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    shared_post = models.ForeignKey(
        Post,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='shared_in_messages'
    )

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender.username} in Thread {self.thread.id}"



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    verb = models.CharField(max_length=255)  # "liked your post" "started following you"
    target_ct = models.ForeignKey(ContentType, blank=True, null=True, on_delete=models.CASCADE)
    target_id = models.PositiveIntegerField(blank=True, null=True)
    target = GenericForeignKey('target_ct', 'target_id')
    unread = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.actor} {self.verb} → {self.user}"
