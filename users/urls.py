# Users
from django.urls import path, include
from knox import views as knox_views

from .views import RegisterAPI, LoginAPI, AccountAPI, ProfileViewSet, FollowUser, UnfollowUser, HealthcheckViewSet

# Prepended with 'users/'
urlpatterns = [
    path('auth', include('knox.urls')),
    path('auth/register', RegisterAPI.as_view()),
    path('auth/login', LoginAPI.as_view()),
    path('auth/account', AccountAPI.as_view()),
    path('auth/logout', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('<str:username>/', ProfileViewSet.as_view()),
    path('follow/<int:user_id>/', FollowUser.as_view()),
    path('unfollow/<int:user_id>/', UnfollowUser.as_view()),
    path('healthcheck', HealthcheckViewSet.as_view())
]
