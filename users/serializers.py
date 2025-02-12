from rest_framework import serializers
from django.contrib.auth import authenticate

from spotify.models import FavAlbums
from spotify.serializers import FavAlbumsSerializer
from .models import Account, Profile


class AccountSerializer(serializers.ModelSerializer):
    # Pull first and last name from user's profile when serializing to json
    first = serializers.CharField(source='profile.first', read_only=True)
    last = serializers.CharField(source='profile.last', read_only=True)

    class Meta:
        model = Account
        fields = ('id', 'email', 'username', 'first', 'last')


# For account creation
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'email', 'username', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user_account = Account.objects.create_user(
            validated_data['email'],
            validated_data['username'],
            validated_data['password'],
        )
        return user_account


# Used when retrieving profile objects
class ProfileSerializer(serializers.ModelSerializer):
    favorite_albums = FavAlbumsSerializer()
    username = serializers.CharField(source='account.username')

    class Meta:
        model = Profile
        exclude = ('following', 'id')

    def create(self, validated_data):
        profile = Profile.objects.create(
            account=validated_data['account'],
            # birthday=  # Implement this later
            first=validated_data['first'],
            last=validated_data['last']
        )

        favalbum_instance = FavAlbums.objects.create(profile=profile)
        favalbum_instance.save()
        return profile


# Used when registering new users
class ProfileRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

    def create(self, validated_data):
        profile = Profile.objects.create(
            account=validated_data['account'],
            # birthday=  # Implement this later
            first=validated_data['first'],
            last=validated_data['last']
        )

        favalbum_instance = FavAlbums.objects.create(profile=profile)
        favalbum_instance.save()
        return profile


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        account = authenticate(**data)
        if account and account.is_active:
            return account
        raise serializers.ValidationError('Incorrect credentials')
