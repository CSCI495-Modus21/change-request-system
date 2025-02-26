from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import ChangeRequest
from .serializers import ChangeRequestSerializer

class ChangeRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing change requests with filtering and search capabilities.
    """
    queryset = ChangeRequest.objects.all()
    serializer_class = ChangeRequestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['project_name', 'requested_by', 'date_of_request']
    search_fields = ['description']