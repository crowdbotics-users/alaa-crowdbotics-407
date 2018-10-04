from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from core.abstract_models import TimeStampedModel


class Profile(TimeStampedModel):
    """ Profile Model """

    MALE = "M"
    FEMALE = "F"
    NOT_SPECIFIED = "N"

    GENDER_CHOICES = {
        (MALE, "Male"),
        (FEMALE, "Female"),
        (NOT_SPECIFIED, "Not specified"),
    }

    owner = models.OneToOneField(User, on_delete=models.PROTECT)
    profile_image = models.ImageField(null=True)
    website = models.URLField(null=True)
    bio = models.TextField(null=True)
    phone = models.CharField(max_length=140, null=True)
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, default=NOT_SPECIFIED
    )
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

    # @property
    # def post_count(self):
    #     return self.images.all().count()

    @property
    def followers_count(self):
        return self.followers.all().count()

    @property
    def following_count(self):
        return self.following.all().count()
