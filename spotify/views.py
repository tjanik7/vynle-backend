# Spotify
from django.http import HttpResponse
from requests import Request, post, get
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Account
from .credentials import REDIRECT_URI, CLIENT_SECRET, CLIENT_ID
from .models import SpotifyToken
from .serializers import SpotifyTokenSerializer
from spotify.utils.release_request import get_spotify_album
from .utils.tokens import update_or_create_user_tokens, is_spotify_authenticated, get_header


class SetFavAlbum(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    ALBUM_LIST_LEN = 6  # Treat as constant static variable to avoid hardcoding

    # Note that if variable is accessed using the classname, it is treated as a static variable
    # If it is accessed using an object/instance, it is treated as an object attribute (unique to each object)

    def post(self, request):
        user = request.user

        if is_spotify_authenticated(user):
            album_id = request.data['album_id']
            ind = request.data['ind']
            if not isinstance(ind, int):
                return Response(
                    {'msg': f"Index must be an int 0 <= ind < {str(SetFavAlbum.ALBUM_LIST_LEN)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if ind < 0 or ind >= SetFavAlbum.ALBUM_LIST_LEN:  # If index out of range
                return Response(
                    {'msg': f"Index must be an int 0 <= ind < {str(SetFavAlbum.ALBUM_LIST_LEN)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            album_obj = get_spotify_album(user, album_id)
            if album_obj is None:
                return Response(
                    "This album could not be found",
                    status=status.HTTP_404_NOT_FOUND,
                )

            user_albums = user.profile.favorite_albums

            setattr(user_albums, 'a' + str(ind), album_id)

            user_albums.save()

            return Response(album_obj, status=status.HTTP_200_OK)


# Accepts user and index as args and returns fav album at that index
class GetAlbum(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, format=None):
        user = request.user

        if is_spotify_authenticated(user):
            ind = request.query_params.get('ind')
            if ind is None:
                return Response('Request must have ind param', status=status.HTTP_400_BAD_REQUEST)

            # Retrieve album_id string, i.e. the ID Spotify assigns the release
            album_id = getattr(user.profile.favorite_albums, 'a' + ind)

            if len(album_id) == 0:  # Nothing at this index
                return Response(
                    status=status.HTTP_204_NO_CONTENT,  # Sending a msg with this response code throws an error
                )

            album_obj = get_spotify_album(user, album_id)
            if album_obj is None:
                return Response(
                    "This album could not be found",
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Returns dict with 'name', 'artist', and 'img' keys
            return Response(album_obj, status=status.HTTP_200_OK)


class FavoriteAlbumsView(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, format=None):
        user = request.user

        if is_spotify_authenticated(user):
            try:
                target_username = request.query_params.get('username')
                target_account = Account.objects.get(username=target_username)
                target_profile = target_account.profile
            except Account.DoesNotExist:
                return Response(
                    "No user exists with this username",
                    status=status.HTTP_404_NOT_FOUND
                )

            # Retrieve album_id string, i.e. the ID Spotify assigns the release
            fav_album_id_list = [getattr(target_profile.favorite_albums, 'a' + str(i)) for i in range(6)]
            album_objects = get_spotify_album(user, fav_album_id_list)

            return Response(album_objects, status=status.HTTP_200_OK)  # Will need to add some error conditions
        else:
            raise Exception("User is not authenticated with Spotify")


class GetFavoriteAlbums(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, format=None):
        user = request.user

        if is_spotify_authenticated(user):
            # Retrieve album_id string, i.e. the ID Spotify assigns the release
            fav_album_ids = [getattr(user.profile.favorite_albums, 'a' + str(i)) for i in range(6)]
            album_objects = get_spotify_album(user, fav_album_ids)

            return Response(album_objects, status=status.HTTP_200_OK)  # Will need to add some error conditions
        else:
            raise Exception('User is not authenticated with Spotify')


class SearchSpotify(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, format=None):
        user = request.user
        if is_spotify_authenticated(user):
            q = request.query_params.get('q')
            payload = {
                'q': q,
                'type': 'album',
                'limit': '5'
            }

            headers = get_header(user)

            response = get('https://api.spotify.com/v1/search', params=payload, headers=headers).json()

            return Response(response, status=status.HTTP_200_OK)
        # add else condition for these top two endpoints


class GetCurrentUserSpotifyProfile(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, format=None):
        user = request.user
        if is_spotify_authenticated(user):
            headers = get_header(user)
            response = get('https://api.spotify.com/v1/me', headers=headers).json()

            spotify_username = response.get('id')
            return Response({
                'id': spotify_username,
            },
                status=status.HTTP_200_OK
            )


# Returns the url that will be used to authenticate this application (this endpoint does not make the request)
class AuthURL(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, format=None):
        # Scopes of spotify data we would like to access from user - found in spotify docs
        scopes = 'user-top-read'

        # Prepares the url but does not send a reqeust
        url = Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': scopes,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'state': request.user.id
        }).prepare().url

        return Response(
            {'url': url},
            status=status.HTTP_200_OK
        )


# Callback function which accepts the information returned from the first request to the url generated in 'AuthURL'
def spotify_callback(request, format=None):
    user_id = request.GET.get('state')
    code = request.GET.get('code')
    error = request.GET.get('error')  # Not yet implemented

    user = Account.objects.get(id=user_id)

    response = post('https://accounts.spotify.com/api/token', data={  # Note that the request is sent on this line
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    error = response.get('error')  # Add error functionality

    update_or_create_user_tokens(user, access_token, token_type, expires_in, refresh_token)
    return HttpResponse('Tokens updated successfully', status=status.HTTP_200_OK)


class GetSpotifyToken(APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = SpotifyTokenSerializer

    def get(self, request, format=None):
        user = request.user
        spotify_token = SpotifyToken.objects.filter(user=user)
        if spotify_token:
            data = SpotifyTokenSerializer(spotify_token[0]).data
            return Response(
                {'token': data},
                status=status.HTTP_200_OK
            )
        return Response(
            {'msg': 'No Spotify token associated with this user'},
            status=status.HTTP_404_NOT_FOUND
        )


class IsSpotifyAuthenticated(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, format=None):
        is_authenticated = is_spotify_authenticated(request.user)
        return Response(
            {'status': is_authenticated},
            status=status.HTTP_200_OK
        )
