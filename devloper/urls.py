from django.urls import path
from . import views

urlpatterns = [
<<<<<<< HEAD
    # path('SignUp/',views.register,name='register'),
    path('LogIn/',views.login,name='register'),
    path('apply/<int:opportunity_id>/', views.apply_for_opportunity, name='apply-for-opportunity'),
=======
    path('SignUp/',views.register,name='register'),
    path('LogIn/',views.login,name='login'),
    path('complaints/', views.add_complaint, name='add_complaint'),
>>>>>>> 791cbf3cd573cd588591bcc0c1dbb4b8748675b9
    
]