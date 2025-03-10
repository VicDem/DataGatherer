from django.db import models

from job_api.logic import initiate_job
from storage_api.models.project_models import Project
from django.db.models.signals import post_save


class Job(models.Model):
    title = models.CharField(
        max_length=1000,
        unique=True
    )
    createdAt = models.DateTimeField(
        auto_now_add=True
    )
    isCompleted = models.BooleanField(
        default=False
    )
    taskGranularity = models.IntegerField(
        default=40,
        editable=False
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
    )
    completedFileUrl = models.CharField(
        max_length=5000,
        null=True,
        blank=True,
    )
    notes = models.CharField(
        max_length=5000,
        null=True,
        blank=True,
    )
    isCreated = models.BooleanField(
        default=False
    )
    isWorking = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.title

    @classmethod
    def post_create(cls, sender, instance, created, *args, **kwargs):
        if not created:
            return
        print("post_create method")
        initiate_job(instance)


post_save.connect(Job.post_create, sender=Job)


class Task(models.Model):
    progressiveID = models.IntegerField(
        editable=False
    )
    inProgress = models.BooleanField()
    isCompleted = models.BooleanField()
    fileURL = models.CharField(
        max_length=5000,
        null=True,
        blank=True,
    )
    job = models.ForeignKey(
        to=Job,
        on_delete=models.CASCADE,
        editable=False
    )

    def __str__(self):
        return f"{self.job.title}/T{self.progressiveID}"

    class Meta:
        unique_together = [['progressiveID', 'job']]


class JobHashtag(models.Model):
    job = models.ForeignKey(
        to=Job,
        on_delete=models.CASCADE,
        editable=False
    )
    task = models.ForeignKey(
        to=Task,
        on_delete=models.RESTRICT,
        editable=False
    )
    content = models.CharField(
        max_length=500,
        editable=False
    )

    def __str__(self):
        return f"{self.task}> #{self.content}"

    class Meta:
        unique_together = [['job', 'content']]


class JobIGUser(models.Model):
    job = models.ForeignKey(
        to=Job,
        on_delete=models.CASCADE,
        editable=False
    )
    name = models.CharField(
        max_length=300,
        editable=False
    )

    def __str__(self):
        return f"{self.job}> U{self.name}"

    class Meta:
        unique_together = [['job', 'name']]


class JobUserHashtagUse(models.Model):
    job = models.ForeignKey(
        to=Job,
        on_delete=models.CASCADE,
        editable=False
    )
    user = models.ForeignKey(
        to=JobIGUser,
        on_delete=models.CASCADE,
        editable=False
    )
    hashtag = models.ForeignKey(
        to=JobHashtag,
        on_delete=models.CASCADE,
        editable=False
    )
    image_path = models.CharField(
        max_length=5000,
        editable=False
    )

    def __str__(self):
        return f"{self.job}>> {self.user} {self.hashtag} {self.image_path}"

    class Meta:
        unique_together = [['job', 'user', 'hashtag', 'image_path']]
