"""foodtalk API URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token

from . import views as api_views


router = DefaultRouter()
router.register("signup", api_views.SignupViewSet, base_name="signup")
router.register("users/profile", api_views.UserProfile, base_name="user_profile")

urlpatterns = [
    path("", include(router.urls)),
    path("token/", obtain_jwt_token),
    # Users
    path("users/explore/", api_views.ExploreUsers.as_view(), name="explore_users"),
    path(
        "users/<int:profile_id>/follow/", view=api_views.FollowUser.as_view(), name="follow_user"
    ),
    path(
        "users/<int:profile_id>/unfollow/",
        view=api_views.UnfollowUser.as_view(),
        name="unfollow_user",
    ),
    path(
        "users/<str:username>/followers/",
        view=api_views.UserFollowers.as_view(),
        name="user_followers",
    ),
    path(
        "users/<str:username>/following/",
        view=api_views.UserFollowing.as_view(),
        name="user_following",
    ),
    path("users/search/", view=api_views.Search.as_view(), name="search"),
    path(
        "users/<str:username>/password/",
        view=api_views.ChangePassword.as_view(),
        name="change_password",
    ),
    path("users/login/facebook/", view=api_views.FacebookLogin.as_view(), name="fb_login"),
    path("users/login/instagram/", view=api_views.InstagramLogin.as_view(), name="ig_login"),
    # Images
    path("images/", view=api_views.Images.as_view(), name="images"),
    path("<int:image_id>/", view=api_views.ImageDetail.as_view(), name="image_detail"),
    path("<int:image_id>/likes/", view=api_views.LikeImage.as_view(), name="like_image"),
    path("<int:image_id>/unlikes/", view=api_views.UnlikeImage.as_view(), name="unlike_image"),
    path(
        "<int:image_id>)/comments/", view=api_views.CommentOnImage.as_view(), name="comment_image"
    ),
    path(
        "<int:image_id>)/comments/<int:comment_id>/",
        view=api_views.ModerateComments.as_view(),
        name="moderate_comments",
    ),
    path("comments/<int:comment_id>/", view=api_views.CommentView.as_view(), name="comment"),
    path("search/", view=api_views.SearchByHashtag.as_view(), name="search"),
    path("notifications/", view=api_views.NotificationsView.as_view(), name="notifications"),
]
