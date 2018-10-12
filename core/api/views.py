# Create your views here.

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.instagram.views import InstagramOAuth2Adapter
from django.contrib.auth.models import User

from django.db.models import Count
from rest_framework import filters
from rest_auth.registration.views import SocialLoginView
from rest_framework import status, permissions, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from core.accounts.models import Profile
from core.api.permissions import IsOwnerOrReadOnly
from core.api.serializers import (
    SignupSerializer,
    NotificationSerializer,
    ListUserSerializer,
    UserProfileSerializer,
    ImageSerializer,
    InputImageSerializer,
    CommentSerializer,
)
from core.images.models import Notification, Image, Like, Comment


class SignupViewSet(ModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = SignupSerializer
    http_method_names = ["post"]


class CustomJWTTokenSignin(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class Logout(GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    http_method_names = ["delete"]

    def delete(self, request, format=None):
        """
        Remove all issued tokens to the logged user and finishes his session
        """
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationsView(APIView):
    def get(self, request, format=None):
        user = request.user.profile
        notifications = Notification.objects.filter(to=user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


def create_notification(creator, to, notification_type, image=None, comment=None):
    notification = Notification.objects.create(
        creator=creator, to=to, notification_type=notification_type, image=image, comment=comment
    )
    notification.save()


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class InstagramLogin(SocialLoginView):
    adapter_class = InstagramOAuth2Adapter


class ExploreUsers(APIView):
    """ returns the 5 users which posted images recently """

    def get(self, request, format=None):
        explore_list = []
        last_five_images = Image.objects.all()[:5]

        for image in last_five_images:
            if image.creator not in explore_list:
                explore_list.append(image.creator)

        serializer = ListUserSerializer(explore_list[:5], many=True, context={"request": request})
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class FollowUser(APIView):
    def post(self, request, profile_id, format=None):
        user = request.user
        try:
            profile_to_follow = Profile.objects.get(id=profile_id)
            user.profile.following.add(profile_to_follow)
            user.profile.save()
            """ create notification for following """
            create_notification(user.profile, profile_to_follow, "follow")
            return Response(status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class UnfollowUser(APIView):
    def post(self, request, profile_id, format=None):
        user = request.user
        try:
            user_to_unfollow = Profile.objects.get(id=profile_id)
            user.profile.following.remove(user_to_unfollow)
            user.profile.save()
            return Response(status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class UserProfile(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
    queryset = Profile.objects.all()
    lookup_field = "owner__username"

    @action(
        methods=["put"],
        detail=True,
        permission_classes=[IsOwnerOrReadOnly, IsAuthenticated],
        url_path="verify",
        url_name="verify_number",
    )
    def confirm_phone(self, request, owner__username=None):
        """
        Verify user's profile phone number with given token.
        """
        profile = self.get_object()
        token = request.data.get("token")

        if not token:
            return Response("Invalid token.", status=status.HTTP_400_BAD_REQUEST)

        verified, error_msgs = profile.verify(token=token)

        if verified:
            return Response({"verified": verified}, status=status.HTTP_200_OK)
        else:
            return Response(error_msgs, status=status.HTTP_400_BAD_REQUEST)


class UserFollowers(APIView):
    def get(self, request, username, format=None):
        try:
            found_user = Profile.objects.get(owner__username=username)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user_followers = found_user.followers.all()
        serializer = ListUserSerializer(user_followers, many=True, context={"request": request})
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class UserFollowing(APIView):
    def get(self, request, username, format=None):
        try:
            found_user = Profile.objects.get(owner__username=username)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user_following = found_user.following.all()
        serializer = ListUserSerializer(user_following, many=True, context={"request": request})
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class Search(APIView):
    """ search for a user by username """

    def get(self, request, format=None):
        username = request.query_params.get("username", None)
        if username is not None:
            users = Profile.objects.filter(owner__username__istartswith=username)
            serializer = ListUserSerializer(users, many=True, context={"request": request})
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ChangePassword(APIView):
    def put(self, request, username, format=None):
        user = request.user
        if user.username == username:
            current_password = request.data.get("current_password", None)
            if current_password is not None:
                passwords_match = user.check_password(current_password)
                if passwords_match:
                    new_password = request.data.get("new_password", None)
                    if new_password is not None:
                        user.set_password(new_password)
                        user.save()
                        return Response(status=status.HTTP_200_OK)
                    else:
                        return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 12


class ImagesViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.annotate(num_likes=Count('likes'))
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
    filter_backends = (filters.OrderingFilter,)
    pagination_class = StandardResultsSetPagination
    ordering = ['-num_likes']

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == 'POST':
            return InputImageSerializer
        return ImageSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        latitude = self.request.query_params.get('latitude')
        longitude = self.request.query_params.get('longitude')
        qs = super().get_queryset()
        if latitude and longitude:
            return qs.within(lat=latitude, long=longitude).order_by('distance')
        return qs

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user.profile)
        return serializer


class GenericImageView(APIView):
    def _get_object(self, image_id):
        try:
            return Image.objects.get(id=image_id)
        except Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class LikeImage(GenericImageView):
    def get(self, request, image_id, format=None):
        likes = Like.objects.filter(image__id=image_id)
        like_creator_ids = likes.values("creator_id")
        users = Profile.objects.filter(id__in=like_creator_ids)
        serializer = ListUserSerializer(users, many=True, context={"request": request})
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request, image_id, format=None):
        user = request.user.profile
        found_image = self._get_object(image_id)
        like, created = Like.objects.get_or_create(creator=user, image=found_image)
        if created:
            create_notification(user, found_image.creator, "like", found_image)
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_202_ACCEPTED)


class UnlikeImage(GenericImageView):
    def delete(self, request, image_id, format=None):
        user = request.user.profile
        found_image = self._get_object(image_id)
        try:
            preexisting_like = Like.objects.get(creator=user, image=found_image)
            preexisting_like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Like.DoesNotExist:
            return Response(status=status.HTTP_202_ACCEPTED)


class CommentOnImage(GenericImageView):
    """ post a comment """

    def post(self, request, image_id, format=None):
        user = request.user.profile
        found_image = self._get_object(image_id)
        serializer = CommentSerializer(data=request.data, context={"request:": request})

        if serializer.is_valid(raise_exception=True):
            serializer.save(creator=user, image=found_image)
            """ create notification for comment """
            create_notification(
                user, found_image.creator, "comment", found_image, serializer.data["message"]
            )
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class CommentView(APIView):
    """ delete a comment """

    def delete(self, request, comment_id, format=None):
        user = request.user.profile
        try:
            comment = Comment.objects.get(id=comment_id, creator=user)
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ModerateComments(APIView):
    """ delete a comment on current user's images """

    def delete(self, request, image_id, comment_id, format=None):
        user = request.user.profile

        try:
            comment_to_delete = Comment.objects.get(
                id=comment_id, image__id=image_id, image__creator=user
            )
            comment_to_delete.delete()
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SearchByHashtag(APIView):
    """ search for a hastag """

    def get(self, request, format=None):
        hashtags = request.query_params.get("hashtags", None)
        if hashtags is not None:
            hashtags = hashtags.split(",")
            images = Image.objects.filter(tags__name__in=hashtags).distinct()
            serializer = ImageSerializer(images, many=True, context={"request": request})
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            images = Image.objects.all()[:30]
            serializer = ImageSerializer(images, many=True, context={"request": request})
            return Response(data=serializer.data, status=status.HTTP_200_OK)


class ImageDetail(APIView):
    def found_own_image(self, image_id, user):
        try:
            image = Image.objects.get(id=image_id, creator=user)
            return image
        except Image.DoesNotExist:
            return None

    def get(self, request, image_id, format=None):
        try:
            image = Image.objects.get(id=image_id)
        except Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ImageSerializer(image, context={"request": request})
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request, image_id, format=None):
        user = request.user.profile
        image = self.found_own_image(image_id, user)

        if image is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = InputImageSerializer(image, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save(creator=user)
            return Response(data=serializer.data, status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, image_id, format=None):
        user = request.user.profile
        image = self.found_own_image(image_id, user)
        if image is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        image.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
