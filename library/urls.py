from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenreViewSet, BookViewSet, FineViewSet, BorrowingViewSet, group_api_view, register_api_view, login_api_view
from rest_framework.urlpatterns import format_suffix_patterns
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Library Management API",
        default_version='v1',
        description="API documentation for managing library system",
        contact=openapi.Contact(email="sabinprajapati7@gmail.com"),
    ),
    public=True,
    # permission_classes=[],
)


router = DefaultRouter()
router.register('genre', GenreViewSet)
router.register('fine', FineViewSet)
router.register('book', BookViewSet)
router.register('borrowing', BorrowingViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/group/', group_api_view, name='group'),
    path('api/register/', register_api_view, name='register'),
    path('api/login/', login_api_view, name='login'),
    path('docs/', schema_view.as_view(), name='api-docs'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
