from rest_framework import serializers

from spotify.utils.release_request import get_spotify_album
from users.models import Account
from .models import Post, Comment


# Serializer specifically for returning the user object within each post
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'username']


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    release = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = '__all__'

    def get_release(self, post):
        if post.spotify_release_uri:
            user = self.context.get('user')
            if user is None:
                raise Exception('"User" was not set in the post serializer')

            return get_spotify_album(user, post.spotify_release_uri)
        return None


# For use within PostListSerializer, since the 'release' field needs to be serialized manually in this case
# to avoid sending a request to Spotify for each post
class PostSerializerWithoutRelease(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Post
        # Note that the 'release' field does not need to be manually excluded, since it is not actually a part
        # of the model in the first place
        fields = '__all__'


def serialize_multiple_posts(post_instance_list, user):
    spotify_uris = [post.spotify_release_uri for post in post_instance_list]

    release_dict_list = get_spotify_album(user, spotify_uris)

    ret = []
    for post_instance, release_dict_serialized in zip(post_instance_list, release_dict_list):
        post_serialized = PostSerializerWithoutRelease(post_instance).data
        post_serialized['release'] = release_dict_serialized
        ret.append(post_serialized)

    return ret

    # ############### Example of serialized post ###############
    # {
    #     "id": 55,
    #     "user": {
    #         "id": 1,
    #         "username": "tjanik7"
    #     },
    #     "release": {
    #         "name": "Minecraft - Volume Alpha",
    #         "artist": "C418",
    #         "img": "https://i.scdn.co/image/ab67616d00001e02aaeb5c9fb6131977995b7f0e"
    #     },
    #     "body": "minecraft",
    #     "spotify_release_uri": "3Gt7rOjcZQoHCfnKl5AkK7"
    # }


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
