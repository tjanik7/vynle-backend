# URLs for posts

from django.urls import path
from rest_framework import routers

from .views import PostViewSet, CommentView, UserPostViewSet

router = routers.DefaultRouter()
router.register(viewset=PostViewSet, basename='posts', prefix='')
# router.register(viewset=UserPostViewSet, basename='user-posts', prefix='user-posts')

urlpatterns = router.urls

urlpatterns += [
    path('user-posts/<str:username>/', UserPostViewSet.as_view()),
    path('comment', CommentView.as_view()),
]
