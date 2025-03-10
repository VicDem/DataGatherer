from django.db import models
from storage_api.models.image_models import Image
from storage_api.models.project_models import Project
from django.contrib import admin
from django.contrib.auth.models import User


class Hashtag(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE
    )
    content = models.CharField(max_length=500)
    createdFromImage = models.ForeignKey(
        Image,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        unique_together = ['project', 'content', 'author']

    def __str__(self):
        return "PRJ %s, #%s" % (self.project, self.content)


class IGUser(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=300)
    description = models.TextField(max_length=500, null=True, blank=True)
    createdFromImage = models.ForeignKey(
        Image,
        on_delete=models.SET_NULL,
        null=True
    )
    alias = models.CharField(
        max_length=300,
        null=True,
        blank=True
    )

    @property
    @admin.display(description='Name displayed in adj matrix')
    def matrix_name(self):
        if self.alias is not None:
            return "%s (%s)" % (self.alias, self.name)
        return "%s" % self.name

    class Meta:
        unique_together = [['project', 'name'], ['alias','author']]

    def save(self, *args, **kwargs):
        if not self.alias:
            self.alias = None
        super().save(*args, **kwargs)

    def __str__(self):
        return "PRJ: %s, %s" % (self.project.name, self.name)


class UserHashtagUse(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.RESTRICT
    )
    igUser = models.ForeignKey(
        IGUser,
        on_delete=models.RESTRICT
    )
    hashtag = models.ForeignKey(
        Hashtag,
        on_delete=models.RESTRICT
    )
    image = models.ForeignKey(
        Image,
        on_delete=models.RESTRICT
    )

    def __str__(self):
        return f"{self.project.name}, {self.igUser.name} used #{self.hashtag.content} in {self.image.userId}"

    class Meta:
        unique_together = ['image', 'hashtag', 'igUser', 'project', 'author']
