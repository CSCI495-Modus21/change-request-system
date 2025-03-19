from django.urls import path, include
from django.http import HttpResponse
from rest_framework.routers import DefaultRouter
from .views import ChangeRequestViewSet

router = DefaultRouter()
router.register(r'change_requests', ChangeRequestViewSet)

# Simple home view
def home_view(request):
    return HttpResponse("Welcome to the Change Request System!")

urlpatterns = [
    path('', home_view, name='home'),  # This adds a home page
    path('api/', include(router.urls)),  # API routes
]
