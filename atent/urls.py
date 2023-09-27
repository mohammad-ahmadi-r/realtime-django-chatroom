from django.urls import path
from . import views
app_name= "atent"

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('changepass/', views.changepass, name='changepass'),
    path('reset-password/<str:token>/', views.reset_password , name = 'resetpassword'),
    path('verify_email/', views.verify_email, name='verify_email'),
    path('verify/<str:token>/', views.verify, name='verify'),
    path('Notfound/', views.Notfound, name='Notfound'),
    
    path('checkpass/', views.checkpass, name='checkpass'),
    path('checkusername/', views.check_username, name='checkusername'),
    path('emailcheck/', views.check_email, name='emailcheck'),
]