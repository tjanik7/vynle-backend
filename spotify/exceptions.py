class UserNotSpotifyAuthenticatedError(Exception):
    def __init__(self, message='User is not authenticated with Spotify'):
        self.message = message
        super().__init__(self.message)
