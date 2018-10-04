# Create your views here.
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.instagram.views import InstagramOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from core.accounts.models import Profile
from core.api.serializers import SignupSerializer, NotificationSerializer, ListUserSerializer, UserProfileSerializer, \
    ImageSerializer, InputImageSerializer, CommentSerializer
from core.images.models import Notification, Image, Like, Comment


class SignupViewSet(ModelViewSet):
    serializer_class = SignupSerializer
    http_method_names = ["post"]


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
        last_five_images = Image.objects.all()[:10]

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


class UserProfile(APIView):
    def get_user(self, username):
        try:
            found_user = Profile.objects.get(owner__username=username)
            return found_user
        except Profile.DoesNotExist:
            return None

    def get(self, request, username, format=None):
        found_user = self.get_user(username)
        if found_user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = UserProfileSerializer(found_user, context={"request": request})
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request, username, format=None):
        found_user = self.get_user(username)
        user = request.user
        if found_user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        elif found_user.username != user.username:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = UserProfileSerializer(found_user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


class Images(APIView):
    def get(self, request, format=None):
        user = request.user
        following_users = user.profile.following.all()
        image_list = [following_user.images.all()[:5] for following_user in following_users]
        image_list.extend(user.images.all()[:5])
        sorted_list = sorted(image_list, key=lambda image: image.created_at, reverse=True)
        serializer = ImageSerializer(sorted_list, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request, format=None):
        user = request.user
        serializer = InputImageSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save(creator=user.profile)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)


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
            comment_to_delete = Comment.objects.get(id=comment_id, image__id=image_id, image__creator=user)
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
