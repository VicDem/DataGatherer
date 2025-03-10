from django.contrib import admin
from data_gatherer.admin_sites import global_admin_site
from job_api.models import *


class JobAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'isCreated']
    readonly_fields = [
        'isCompleted',
        'isWorking',
        'isCreated'
    ]
    list_filter = ['project']


class TaskAdmin(admin.ModelAdmin):
    list_display = ['progressiveID', 'job', 'inProgress', 'isCompleted']
    readonly_fields = [
        'progressiveID',
        'inProgress',
        'isCompleted',
        'fileURL',
        'job'
    ]
    list_filter = ['job']



global_admin_site.register(Job, JobAdmin)
global_admin_site.register(Task, TaskAdmin)