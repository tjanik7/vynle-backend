from rest_framework import serializers
from django.contrib.auth import authenticate

from spotify.models import FavAlbums
from spotify.serializers import FavAlbumsSerializer
from .models import Account, Profile


class AccountSerializer(serializers.ModelSerializer):
    # Reference fields in related objects that we want to serialize
    # Read only fields (only used for serialization)
    first = serializers.CharField(source='profile.first')
    last = serializers.CharField(source='profile.last')


    class Meta:
        model = Account
        fields = ('id', 'email', 'username', 'password', 'first', 'last')

        # Write only fields are only used for deserialization
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user_account = Account.objects.create_user(
            validated_data['email'],
            validated_data['username'],
            validated_data['password'],
        )

        profile = Profile.objects.create(
            account=user_account,
            # birthday=  # Implement this later
            first=validated_data['profile']['first'],
            last=validated_data['profile']['last']
        )

        FavAlbums.objects.create(profile=profile)

        return user_account


# Used when retrieving profile objects
class ProfileSerializer(serializers.ModelSerializer):
    favorite_albums = FavAlbumsSerializer()
    username = serializers.CharField(source='account.username')

    class Meta:
        model = Profile
        exclude = ('following', 'id')


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        account = authenticate(**data)
        if account and account.is_active:
            return account
        raise serializers.ValidationError('Incorrect credentials')
