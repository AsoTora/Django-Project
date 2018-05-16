from django.db import models
from django.contrib.auth.models import User

from django.utils.html import mark_safe
from markdown import markdown

import math

class Board(models.Model):  # Ассоциируется с темой. Связь 1 Board -- 0/many Topics
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)

    def get_posts_count(self):
        return Post.objects.filter(topic__board=self).count()

    def get_last_post(self):
        return Post.objects.filter(topic__board=self).order_by('-created_at').first()

    def get_last_post_id(self):
        post = Post.objects.filter(topic__board=self).order_by('-created_at').first()
        return post.topic.pk

    def __str__(self):
        return self.name


class Topic(models.Model):  # Ассоциируется с постами. Связь 1 Topic -- 1/many Posts
    subject = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(Board, related_name='topics', on_delete=models.CASCADE)
    starter = models.ForeignKey(User, related_name='topics', on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0)  # the number of page views

    def __str__(self):
        return self.subject

    def get_page_count(self):
        count = self.posts.count()
        pages = count/20
        return math.ceil(pages)

    def has_many_pages(self, count=None):
        if count is None:
            count = self.get_page_count()
        return count > 6

    def get_page_range(self):
        count = self.get_page_count()
        if self.has_many_pages(count):
            return range(1, 5)
        return range(1, count + 1)

    def get_last_ten_posts(self):
        return self.posts.order_by('-created_at')[:10]


class Post(models.Model):  # Ассоциируется с user. Связь 1 Post -- 1 User
    message = models.TextField(max_length=4000)
    topic = models.ForeignKey(Topic, related_name='posts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, null=True, related_name='+', on_delete=models.CASCADE)
    # related_name='+' instructs Django that we don’t need this reverse relationship, so it will ignore it.

    def __str__(self):
        return self.message[:30]

    def get_message_as_markdown(self):
        return mark_safe(markdown(self.message, safe_mode='escape'))





