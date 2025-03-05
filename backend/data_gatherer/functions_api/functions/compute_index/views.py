import io

from django.core.management import call_command
from django.http import HttpResponse
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny


# TODO da guardare

class GetDataDumpApiView(generics.ListAPIView):
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):

        with io.StringIO() as out:
            call_command('dumpdata', stdout=out)
            dump = out.getvalue()

        response = HttpResponse(content_type='text/json', content=dump)
        response['Content-Disposition'] = 'attachment; filename=dump.json'

        return response
