from django.urls import path
from . import views

urlpatterns = [
    path('handle_user/', views.handle_user.as_view()),
    path('register/', views.new_user.as_view()),
    path('token-auth/', views.token_auth.as_view()),
]