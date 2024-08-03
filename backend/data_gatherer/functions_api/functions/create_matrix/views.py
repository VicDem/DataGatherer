from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.decorators import api_view

from functions_api.functions.create_matrix.logic import create_matrix
from functions_api.functions.save_reviewed_text.logic import save_reviewed_text
from functions_api.functions.use_default_crop.logic import apply_default_crop_to_target_image
from functions_api.functions.create_matrix.serializer import Serializer
from storage_api.models.image_models import ImgCrop, Image
from storage_api.models.project_models import Project
from storage_api.serializers.image_serializers import ImgCropSerializer
from rest_framework import generics
from django.http import HttpResponse


class CreateMatrixViewSet(generics.RetrieveAPIView):
    queryset = Project.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=matrix.csv'

        create_matrix(instance, response)

        return response
