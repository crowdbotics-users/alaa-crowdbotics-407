import os

from authy.api import AuthyApiClient
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from core.abstract_models import TimeStampedModel


def get_profile_img_path(instance, filename):
    name, ext = os.path.splitext(filename)
    name = f'{uuid.uuid4()}{ext}'
    return f'images/{instance.username}/{name}'


class Profile(TimeStampedModel):
    """ Profile Model """

    MALE = "M"
    FEMALE = "F"
    NOT_SPECIFIED = "N"

    GENDER_CHOICES = (
        (MALE, "Male"), (FEMALE, "Female"), (NOT_SPECIFIED, "Not specified")
    )

    owner = models.OneToOneField(User, on_delete=models.PROTECT)
    profile_image = models.ImageField(null=True, upload_to=get_profile_img_path)
    website = models.URLField(null=True)
    bio = models.TextField(null=True)
    phone = models.CharField(max_length=140, null=True)
    country_code = models.CharField(max_length=5, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=NOT_SPECIFIED)
    verified = models.BooleanField(default=False)
    verification_metadata = models.TextField(blank=True)
    followers = models.ManyToManyField("self", symmetrical=False, blank=True)
    following = models.ManyToManyField(
        "self", symmetrical=False, blank=True, related_name="profiles"
    )

    def __str__(self):
        return self.owner.username

    @property
    def name(self):
        return f"{self.owner.first_name} {self.owner.last_name}"

    @property
    def username(self):
        return self.owner.username

    def verify(self, token=None):
        authy_api = AuthyApiClient(settings.ACCOUNT_SECURITY_API_KEY)

        verification = authy_api.phones.verification_check(self.phone, self.country_code, token)

        if verification.ok():
            self.verified = True
            self.save()
            return True, None  # verified, error_msg
        else:
            return False, verification.errors()

    def get_images(self, size=5):
        return self.images.all().order_by('-created_at')[:size]

    @classmethod
    def create_profile(cls, user):
        profile = cls.objects.create(owner=user)
        return profile

    @property
    def post_count(self):
        return self.images.count()

    @property
    def followers_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.following.count()
