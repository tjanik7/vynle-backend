from django.http import Http404
from knox.models import AuthToken
from rest_framework import permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile, Account
from .serializers import RegisterSerializer, AccountSerializer, LoginSerializer, ProfileSerializer, \
    ProfileRegistrationSerializer


class HealthcheckViewSet(APIView):
    def get(self, request):
        return Response({
            'status': 'okay',
        })


class ProfileViewSet(APIView):
    # Private method used by other methods to retrieve an item from the DB
    def _get_object(self, username):
        try:
            account_instance = Account.objects.get(username=username)
            profile_instance = Profile.objects.get(account_id=account_instance.id)
            return profile_instance

        except (Account.DoesNotExist, Profile.DoesNotExist):
            raise Http404

    # Endpoint exposed on GET request
    def get(self, request, username, format=None):
        try:
            target_profile = self._get_object(username)
        except Http404:
            return Response(status=status.HTTP_404_NOT_FOUND)

        current_profile = request.user.profile

        # Examine whether this user follows the user they are requesting
        is_following = target_profile in current_profile.following.all()

        serializer = ProfileSerializer(target_profile, context={
            'user': request.user
        })

        profile_serialized = serializer.data

        profile_serialized['is_following'] = is_following
        profile_serialized['favorite_albums'] = profile_serialized['favorite_albums']['data_list']

        # Moves Profile PK from key 'account' to 'id' for a more intuitive response
        # The serializer returns the PK under 'account' because the user's Profile and Account have different PKs
        profile_serialized['id'] = profile_serialized.pop('account')

        return Response(profile_serialized)


# Creates user Account & Profile
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        try:
            account_data, profile_data = _split_user_data(request.data)

            serializer = self.get_serializer(data=account_data)
            serializer.is_valid(raise_exception=True)
            if serializer.is_valid:
                account = serializer.save()
            else:
                raise Exception(serializer.errors)

            profile_data['account'] = account.id

            # Calls ProfileRegistrationSerializer.create(), which also creates a new FavAlbums instance
            # to associate with this profile instance
            profile_ser = ProfileRegistrationSerializer(data=profile_data)

            if profile_ser.is_valid(raise_exception=True):
                profile_ser.save()
            else:
                raise Exception(profile_ser.errors)
        except Exception as e:
            raise Exception(e)

        return Response({
            'account': AccountSerializer(account, context=self.get_serializer_context()).data,
            'token': AuthToken.objects.create(account)[1]  # associates new token with specified account
        })


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = serializer.validated_data
        return Response({
            'account': AccountSerializer(account, context=self.get_serializer_context()).data,
            'token': AuthToken.objects.create(account)[1]  # associates new token with specified account
        })


class FollowUser(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        try:
            follower = request.user.profile
            followee = Account.objects.get(pk=user_id).profile

        except Account.DoesNotExist:
            return Response(
                {'error': 'User account not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if follower == followee:
            return Response(
                'You cannot follow yourself',
                status=status.HTTP_400_BAD_REQUEST
            )

        if followee not in follower.following.all():
            follower.following.add(followee)
            follower.save()

        return Response()


class UnfollowUser(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        try:
            follower = request.user.profile
            followee = Account.objects.get(pk=user_id).profile

        except Account.DoesNotExist:
            return Response(
                {'error': 'User account not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if follower == followee:
            return Response(
                'You cannot unfollow yourself',
                status=status.HTTP_400_BAD_REQUEST
            )

        if followee in follower.following.all():
            follower.following.remove(followee)
            follower.save()

        return Response()


# Retrieve a user via their auth token
class AccountAPI(generics.RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = AccountSerializer

    def get_object(self):
        return self.request.user


def _split_user_data(data):
    # Splits dict of user registration data into Account data and Profile data

    account_data = {
        'email': data['email'],
        'username': data['username'],
        'password': data['password'],
    }
    profile_data = {
        'first': data['first'],
        'last': data['last'],
        # 'birthday': data['birthday'],  # Not implemented yet - needs to be added to frontend form
    }
    return account_data, profile_data
