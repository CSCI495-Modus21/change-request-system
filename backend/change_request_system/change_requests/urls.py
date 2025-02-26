from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChangeRequestViewSet

router = DefaultRouter()
router.register(r'change_requests', ChangeRequestViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]