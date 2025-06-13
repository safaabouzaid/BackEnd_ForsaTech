
from django.contrib import admin
from django.urls import path
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/',include("devloper.urls")),
    path('',include("human_resources.urls")),
    path('api/admin/login/', TokenObtainPairView.as_view(), name='admin_login'),
    path('admin-dash/', include('admin.urls')),
    path('recommend/', include('Recommendation.urls')),


]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)