from django.contrib import admin
from django.urls import path, include

from . import settings


def create_path_str(suffix, path_prefix='api'):
    return path_prefix + '/' + suffix


urlpatterns = [
    # API endpoints
    path(create_path_str('posts/'), include('posts.urls')),
    path(create_path_str('users/'), include('users.urls')),
    path(create_path_str('spotify/'), include('spotify.urls')),

    # Additional endpoints needed for debugging
    path('admin/', admin.site.urls),
    path("__debug__/", include("debug_toolbar.urls")),
]
