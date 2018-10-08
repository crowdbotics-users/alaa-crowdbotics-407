import phonenumbers
from authy.api import AuthyApiClient
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from phonenumbers import NumberParseException
from rest_framework import serializers
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer
from core.accounts.models import Profile
from core.images.models import Image, Comment, Like, Notification


class SignupSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(write_only=True)
    country_code = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
            "phone",
            "country_code",
        )
        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password"}},
            "email": {"required": True},
            "username": {"required": True},
        }

    def validate_country_code(self, country_code):
        if not country_code.startswith("+"):
            country_code = "+" + country_code
        return country_code

    def validate_phone(self, phone_number):
        full_number = self.initial_data["country_code"] + phone_number
        try:
            full_number = phonenumbers.parse(full_number, None)
            if not phonenumbers.is_valid_number(full_number):
                raise serializers.ValidationError("Please input a valid phone number")
        except NumberParseException as e:
            raise serializers.ValidationError(str(e))
        return phone_number

    def _create_user_profile(self, user, profile_data):
        profile = Profile.create_profile(user=user)
        profile.country_code = profile_data["country_code"]
        profile.phone = profile_data["phone"]
        profile.save()

    @staticmethod
    def _start_phone_verification(user):
        authy_api = AuthyApiClient(settings.ACCOUNT_SECURITY_API_KEY)
        request = authy_api.phones.verification_start(
            user.profile.phone, user.profile.country_code, via="sms"
        )
        user.profile.verification_metadata = request.content
        user.profile.save()

    @transaction.atomic
    def create(self, validated_data):
        profile_data = dict(
            country_code=validated_data.pop("country_code"), phone=validated_data.pop("phone")
        )
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        self._create_user_profile(user, profile_data)
        self._start_phone_verification(user)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    post_count = serializers.ReadOnlyField()
    followers_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    is_self = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "id",
            "username",
            "name",
            "bio",
            "website",
            "post_count",
            "followers_count",
            "following_count",
            "verified",
            "is_self",
        )

    def get_is_self(self, profile):
        if "request" in self.context:
            request = self.context["request"]
            return profile.owner.id == request.user.id


class ListUserSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "id",
            "profile_image",
            "username",
            "name",
            "following",
            "followers_count",
            "following_count",
        )

    def get_following(self, obj):
        if "request" in self.context:
            request = self.context["request"]
            return obj in request.user.following.all()


class SmallImageSerializer(serializers.ModelSerializer):
    """ Used for the notifications """

    class Meta:
        model = Image
        fields = ("file",)


class CountImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("id", "file", "comment_count", "like_count")


class FeedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "profile_image",
            "owner__username",
            "name",
            "bio",
            "website",
            "post_count",
            "followers_count",
            "following_count",
        )


class CommentSerializer(serializers.ModelSerializer):
    creator = FeedUserSerializer(read_only=True)
    is_self = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("id", "message", "creator", "is_self")

    def get_is_self(self, image):
        if "request" in self.context:
            request = self.context["request"]
            return image.creator.id == request.user.id


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("creator",)


class ImageSerializer(TaggitSerializer, serializers.ModelSerializer):
    comments = CommentSerializer(many=True)
    creator = FeedUserSerializer()
    tags = TagListSerializerField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = (
            "id",
            "file",
            "restaurant",
            "dish",
            "comments",
            "like_count",
            "comment_count",
            "creator",
            "tags",
            "natural_time",
            "is_liked",
            "is_vertical",
        )

    def get_is_liked(self, obj):
        if "request" in self.context:
            request = self.context["request"]
            return Like.objects.filter(
                creator__id=request.user.profile.id, image__id=obj.id
            ).exists()


class InputImageSerializer(serializers.ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Image
        fields = ("file", "dish", "restaurant", "tags")


class NotificationSerializer(serializers.ModelSerializer):
    creator = UserProfileSerializer()
    image = SmallImageSerializer()

    class Meta:
        model = Notification
        fields = (
            "id",
            "creator",
            "image",
            "comment",
            "notification_type",
            "to",
            "updated_at",
            "natural_time",
        )
