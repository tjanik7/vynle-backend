from django.contrib import admin

from spotify.models import SpotifyToken, FavAlbums


class SpotifyTokenAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'created_at',
        'refresh_token',
        'access_token',
        'expires_at',
        'token_type',
    )


admin.site.register(SpotifyToken, SpotifyTokenAdmin)
admin.site.register(FavAlbums)
