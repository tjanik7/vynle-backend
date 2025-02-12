from rest_framework import serializers
from .models import SpotifyToken, FavAlbums
from spotify.utils.release_request import get_spotify_album


class FavAlbumsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavAlbums
        fields = '__all__'

    def to_representation(self, instance):
        requesting_user = self.context.get('user')

        if not requesting_user:
            raise Exception('User not specified via context when serializing favorite albums.')

        spotify_release_id_list = instance.get_id_list()

        ret = get_spotify_album(requesting_user, spotify_release_id_list)

        # Needs to return dict (not list) otherwise errors are thrown
        return {
            'data_list': ret,
        }


class SpotifyTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotifyToken
        fields = ['access_token', ]
