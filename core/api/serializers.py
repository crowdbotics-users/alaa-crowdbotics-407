from django.contrib.auth.models import User
from rest_framework import serializers
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer
from core.accounts.models import Profile
from core.images.models import Image, Comment, Like


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {
                    'input_type': 'password'
                }
            },
            'email': {
                'required': True
            }
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):

    post_count = serializers.ReadOnlyField()
    followers_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    is_self = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            'id',
            'user__username',
            'name',
            'bio',
            'website',
            'post_count',
            'followers_count',
            'following_count',
            'is_self',
        )

    def get_is_self(self, user):
        if 'request' in self.context:
            request = self.context['request']
            return user.id == request.user.id


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
            return Like.objects.filter(creator__id=request.user.id, image__id=obj.id).exists()


class InputImageSerializer(serializers.ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Image
        fields = (
            "file",
            "dish",
            "restaurant",
            "tags"
        )
