from datetime import timedelta

from django.utils import timezone
from requests import post

from spotify.credentials import CLIENT_ID, CLIENT_SECRET
from spotify.models import SpotifyToken


def get_user_tokens(user):
    user_tokens = SpotifyToken.objects.filter(user=user)
    if user_tokens.exists():
        return user_tokens[0]
    return None


def update_or_create_user_tokens(user, access_token, token_type, expires_in, refresh_token):
    # Note that SpotifyToken model stores user object rather than session_id (as shown in tutorial)
    # This is because Vynle auth flow uses tokens rather than sessions

    tokens = get_user_tokens(user)

    if expires_in is None:
        raise Exception('func update_or_create_user_tokens() got argument "None" for expires_in')

    # Take the current time and add the amount of time it takes for the token to expire (usually 3600sec)
    expires_at = timezone.now() + timedelta(seconds=expires_in)

    if tokens:  # update existing tokens
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_at = expires_at
        tokens.token_type = token_type
        tokens.save(update_fields=[
            'access_token',
            'refresh_token',
            'expires_at',
            'token_type'
        ])

    else:  # Create new Spotify token
        tokens = SpotifyToken(user=user,
                              access_token=access_token,
                              refresh_token=refresh_token,
                              token_type=token_type,
                              expires_at=expires_at,
                              )
        tokens.save()  # Writes to database


def _refresh_spotify_token(user):
    refresh_token = get_user_tokens(user).refresh_token
    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',  # The type of token being sent
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })

    if response.status_code != 200:
        raise Exception(f"Got {response.status_code} status code with reason {response.text} when trying to refresh "
                        f"user's Spotify token")

    response_data = response.json()

    access_token = response_data.get('access_token')
    token_type = response_data.get('token_type')
    expires_in = response_data.get('expires_in')

    update_or_create_user_tokens(
        user,
        access_token,
        token_type,
        expires_in,
        refresh_token,
    )


def is_spotify_authenticated(user):
    tokens = get_user_tokens(user)
    if tokens:
        expiry = tokens.expires_at
        if expiry <= timezone.now():  # If token is expired
            _refresh_spotify_token(user)
        return True
    return False


def get_header(user):
    access_token = get_user_tokens(user).access_token
    return {
        'Authorization': 'Bearer ' + access_token,
    }
