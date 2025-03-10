import django.db.models
from django.contrib import admin
from django.db.models import Q

from data_gatherer.admin_sites import global_admin_site
from job_api.logic import work_job, calculate_whole_file
from job_api.models import *
from threading import Thread
from django.contrib import messages


@admin.action(description="Initiate job")
def admin_initiate_job(modeladmin, request, queryset: django.db.models.QuerySet):
    if queryset.model is not Job:
        raise Exception("This action should be available only to Job Admin")
    for item in queryset:
        item: Job = item
        item.isInitiating = True
        item.save()
        thread1 = Thread(target=initiate_job, args=[item])
        thread1.start()
    modeladmin.message_user(
        request,
        f"Jobs {queryset.values_list('title', flat=True)} initiated, refresh page to see when process is complete",
        messages.SUCCESS,
    )


@admin.action(description="Work job")
def admin_work_job(modeladmin, request, queryset: django.db.models.QuerySet, wait=False):
    if queryset.model is not Job:
        raise Exception("This action should be available only to Job Admin")

    for item in queryset:
        job: Job = item
        work_job(job, wait)

    modeladmin.message_user(
        request,
        f"Jobs {queryset.values_list('title', flat=True)} working, refresh page to see when process is complete"
        f"or go see tasks list",
        messages.SUCCESS,
    )


@admin.action(description="calculate whole file")
def calc_whole_file(modeladmin, request, queryset: django.db.models.QuerySet):
    if queryset.model is not Job:
        raise Exception("This action should be available only to Job Admin")

    for item in queryset:
        job: Job = item
        if job.isInitiated is False:
            modeladmin.message_user(
                request,
                f"Job {job} still to be initiated!",
                messages.ERROR,
            )
            continue
        tasks_to_be_done = Task.objects.filter(Q(job=job) & Q(isCompleted=False))
        if tasks_to_be_done.count() > 0:
            modeladmin.message_user(
                request,
                f"Job {job} still to be worked!",
                messages.ERROR,
            )
            continue
        calculate_whole_file(job)


class JobAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'isInitiating', 'isInitiated', 'isWorking', 'isCompleted']
    list_filter = ['project']
    actions = [admin_initiate_job, admin_work_job, calc_whole_file]

    def get_readonly_fields(self, request, obj=None):
        base = [
            'isCompleted',
            'isWorking',
            'isInitiated',
            'isInitiating',
            'file'
        ]

        if obj is None:
            return base

        if obj.isInitiated:
            base.append('taskGranularity')
            return base

        return base


class TaskAdmin(admin.ModelAdmin):
    list_display = ['progressiveID', 'job', 'inProgress', 'isCompleted', 'currentRow', 'totRows']
    readonly_fields = [
        'progressiveID',
        'inProgress',
        'isCompleted',
        'job',
        'file'
    ]
    list_filter = ['job']


global_admin_site.register(Job, JobAdmin)
global_admin_site.register(Task, TaskAdmin)
