# Spotify
from django.urls import path

from .views import AuthURL, spotify_callback, IsSpotifyAuthenticated, GetSpotifyToken, GetCurrentUserSpotifyProfile, \
    SearchSpotify, GetAlbum, SetFavAlbum, FavoriteAlbumsView

urlpatterns = [
    path('get-auth-url', AuthURL.as_view()),
    path('redirect', spotify_callback),
    path('is-spotify-authenticated', IsSpotifyAuthenticated.as_view()),
    path('get-spotify-token', GetSpotifyToken.as_view()),
    path('get-current-user-spotify-profile', GetCurrentUserSpotifyProfile.as_view()),
    path('search-spotify', SearchSpotify.as_view()),
    path('get-album', GetAlbum.as_view()),
    path('set-fav-album', SetFavAlbum.as_view()),
    path('favorite-albums', FavoriteAlbumsView.as_view())
]
