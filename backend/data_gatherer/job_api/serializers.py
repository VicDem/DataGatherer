from rest_framework import serializers
from job_api.models import *


class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = "__all__"
        read_only_fields = [
            "createdAt",
            'taskGranularity',
            'project',
            'isCreated'
        ]


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = [
            "progressiveID",
            "job"
        ]
