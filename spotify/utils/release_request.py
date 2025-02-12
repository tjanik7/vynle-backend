from requests import get

from spotify.exceptions import UserNotSpotifyAuthenticatedError
from spotify.utils.tokens import is_spotify_authenticated, get_header


def _request_spotify_release_art(user, release_uri):
    """
    Requests release data from Spotify
    @param user: 'user' object sent with request from the frontend
    @param release_uri: Either str representing one release URI or list specifying multiple
    @return: If one URI specified: dict; If multiple: list of dicts
    """

    base_url = 'https://api.spotify.com/v1/albums'
    headers = get_header(user)

    if isinstance(release_uri, str):  # If only requesting one release
        url = base_url + f'/{release_uri}'
        many = False

    elif isinstance(release_uri, list):  # If requesting multiple releases
        skip_locations = set()  # Indices containing empty values
        release_uris_filtered = []

        # Filter out empty values while taking note of where they take place
        # Necessary to reassemble this list in order
        for ind, uri in enumerate(release_uri):
            if uri == '':
                skip_locations.add(ind)
            else:
                release_uris_filtered.append(uri)

        if not release_uris_filtered:
            # Return list of Nones if empty list since returned list needs to be same size
            return [None] * len(release_uri)

        # Only include non-empty URIs in request, otherwise throws 400 error
        url = base_url + '?ids=' + ','.join(release_uris_filtered)
        many = True

    else:
        raise TypeError('"release_uri" should be type list or str')

    # Send the request
    response_obj = get(url, headers=headers)

    if response_obj.status_code == 200:
        if many:
            album_list_response = response_obj.json()['albums']
            response = []

            for ind in range(len(release_uri)):
                if ind in skip_locations:
                    response.append(None)

                else:
                    response.append(album_list_response.pop(0))

            return response

        return response_obj.json()

    # If request != 200/OK
    raise Exception(
        f'Got {response_obj.status_code} response when retrieving album from Spotify. Reason: {response_obj.text}'
    )


def _transform_release_art_response(response_json, img_size):
    if response_json is None:
        return None

    assert isinstance(response_json, dict), f'Expected type dict but got {type(response_json).__name}'

    size_letter_to_ind = {
        's': 2,
        'm': 1,
        'l': 0,
    }

    img_size_ind = size_letter_to_ind[img_size]

    if 'name' in response_json and 'artists' in response_json and 'images' in response_json:
        return {
            'name': response_json['name'],  # Name of album
            'artist': response_json['artists'][0]['name'],  # Name of first artist listed
            'img': response_json['images'][img_size_ind]['url'],  # Medium img - 300x300
        }

    return {  # Return empty album (either release URI was empty or album could not be found)
        'name': '',  # Name of album
        'artist': '',  # Name of first artist listed
        'img': '',  # Medium img - 300x300
    }


def get_spotify_album(user, release_uri, img_size='m'):
    """
    Calls helper funcs which make the request then transforms the response data
    @param user: 'user' object from request
    @param release_uri: str or list
    @param img_size: one of {s,m,l}
    @return: dict or list
    """
    if is_spotify_authenticated(user):
        response = _request_spotify_release_art(user, release_uri)
        if isinstance(response, dict):
            return _transform_release_art_response(response, img_size)

        elif isinstance(response, list):
            return [_transform_release_art_response(response_item, img_size) for response_item in response]

        raise TypeError(
            f'Return value from _transform_release_art_response expected to be str or list. Got type {type(response)}.'
        )

    raise UserNotSpotifyAuthenticatedError('Unable to pull album data since user is not authenticated with Spotify')
