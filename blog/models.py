from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager

class PublishManager(models.Manager):                               #Custom Manager
    def get_queryset(self):
        return super().get_queryset()\
                        .filter(status=Post.Status.PUBLISHED)

class Post(models.Model):

    class Status(models.TextChoices):                               #Choices for status field
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'
    
    tags = TaggableManager()                                          #Taggable manager for tags
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')  #Slug field for URL
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2,
                              choices=Status.choices,
                              default=Status.DRAFT)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='blog_posts')               #One to Many relationship
    objects = models.Manager()
    published = PublishManager()
    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish'])
        ]

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:post_details', 
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day,
                             self.slug])          #URL for the post details page)
class Comment(models.Model):
    post = models.ForeignKey(Post, 
                             on_delete=models.CASCADE,
                             related_name='comments')               #One to Many relationship
    name = models.CharField(max_length=80)
    email=models.EmailField()
    body = models.TextField()
    created= models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)
    active=models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
        ]
        def __str__ (self):
            return f' Comment by {self.name} on {self.post}'