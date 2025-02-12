from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from spotify.exceptions import UserNotSpotifyAuthenticatedError
from users.models import Account
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer, serialize_multiple_posts


class CommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        parent_post_id = request.query_params['post_id']

        all_comments = Comment.objects.filter(parent_post=parent_post_id)
        comments_ser = CommentSerializer(all_comments, many=True).data

        return Response(
            comments_ser,
            status=200
        )

    def post(self, request):
        required_params = ['body', 'post_id']
        missing_params = [param for param in required_params if param not in request.data]

        if missing_params:
            return Response(
                f'Error: missing required parameters {missing_params}',
                status=400,
            )

        parent_post = Post.objects.get(pk=request.data['post_id'])

        new_comment = Comment.objects.create(
            user=request.user,
            body=request.data['body'],
            parent_post=parent_post,
        )
        new_comment.save()

        return Response(
            CommentSerializer(new_comment).data,
            status=200
        )


class UserPostViewSet(APIView):
    # For getting all the posts by a user
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer

    # This does not appear to be used, but it is required to be defined
    queryset = Post.objects.all()

    def get(self, request, username):
        try:
            target_user = Account.objects.get(username=username)
        except Account.DoesNotExist:
            return Response(
                f'User "{username}" could not be found.',
                status=status.HTTP_404_NOT_FOUND,
            )

        posts_raw = Post.objects.filter(user=target_user)

        try:
            posts_serialized = serialize_multiple_posts(posts_raw, request.user)
        except UserNotSpotifyAuthenticatedError:
            return Response(
                data={
                    'reason': 'not Spotify authenticated'
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(posts_serialized)


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = PostSerializer

    # Overriding default method for getting list posts
    def list(self, request, *args, **kwargs):
        user = request.user
        followed_users = user.profile.following.all()
        posts_raw = Post.objects.filter(user__profile__in=followed_users)

        try:
            posts_serialized = serialize_multiple_posts(posts_raw, request.user)
        except UserNotSpotifyAuthenticatedError:
            return Response(
                data={
                    'reason': 'not Spotify authenticated'
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(posts_serialized)

    # Overriding default method for getting one post
    def retrieve(self, request, *args, **kwargs):
        try:
            # The fact that the key is 'pk' is defined by Django, since we are overriding the default implementation
            post_id = kwargs['pk']
            post_raw = Post.objects.get(pk=post_id)
            post = PostSerializer(post_raw, context={
                'user': request.user
            })
            return Response(
                post.data
            )

        except Post.DoesNotExist:
            return Response(
                'A post with this ID could not be found',
                status=status.HTTP_404_NOT_FOUND
            )

    def get_queryset(self):
        return Post.objects.all()

    def get_serializer_context(self):
        # Add any context data you need to pass to the serializer
        context = super(PostViewSet, self).get_serializer_context()
        context['user'] = self.request.user
        return context

    def perform_create(self, serializer):  # Allows for user to be assigned to post when it is created
        serializer.save(user=self.request.user)
