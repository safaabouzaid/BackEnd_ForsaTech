
from django.contrib import admin
from django.urls import path
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/',include("devloper.urls")),
    #path('auth/',include("human_resources.urls")),
    path('api/admin/login/', TokenObtainPairView.as_view(), name='admin_login'),
    path('admin-dash/', include('admin.urls')),


]
