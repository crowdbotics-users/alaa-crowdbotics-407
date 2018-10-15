import os
import uuid

from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from taggit.managers import TaggableManager
from django.contrib.humanize.templatetags.humanize import naturaltime
from imagekit.models import ProcessedImageField
from imagekit.processors import Transpose

# Create your models here.
from core.abstract_models import TimeStampedModel
from core.accounts.models import Profile


class ImageQuerySet(models.QuerySet):
    def within(self, lat, long):
        ref_location = Point(float(lat), float(long))
        return self.filter(point__distance_gte=(ref_location, D(m=2000))).annotate(
            distance=Distance("point", ref_location))


def post_image_path(instance, filename):
    name, ext = os.path.splitext(filename)
    name = f'{uuid.uuid4()}{ext}'
    return 'images/{0}/{1}'.format(instance.creator.username, name)


class Image(TimeStampedModel):
    """ Image Model """
    file = ProcessedImageField(
        processors=[Transpose()], format="JPEG", options={"quality": 50},
        upload_to=post_image_path
    )
    restaurant = models.TextField()
    dish = models.TextField()
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, related_name="images")
    tags = TaggableManager()
    latitude = models.CharField(max_length=80, null=True)
    longitude = models.CharField(max_length=80, null=True)
    point = models.PointField(null=True, blank=True)

    objects = ImageQuerySet.as_manager()

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()

    @property
    def natural_time(self):
        return naturaltime(self.created_at)

    @property
    def is_vertical(self):
        return self.file.width < self.file.height

    def __str__(self):
        return f"{self.restaurant} - {self.dish}"


class Comment(TimeStampedModel):
    """ Comment Model """
    message = models.TextField()
    creator = models.ForeignKey(Profile, on_delete=models.PROTECT, null=True)
    image = models.ForeignKey(
        Image, on_delete=models.CASCADE, null=True, related_name="comments"
    )
    tags = TaggableManager()

    def __str__(self):
        return self.message


class Like(TimeStampedModel):
    """ Like Model """
    creator = models.ForeignKey(Profile, on_delete=models.PROTECT, null=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, null=True, related_name="likes")

    def __str__(self):
        return "User: {} - Image Caption: {}".format(
            self.creator.owner.username, self.image.dish
        )


class Notification(TimeStampedModel):
    LIKE = "L"
    COMMENT = "C"
    FOLLOW = "F"

    TYPE_CHOICES = ((LIKE, "Like"), (COMMENT, "Comment"), (FOLLOW, "Follow"))

    creator = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="creator_notifications"
    )
    to = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="to_notifications"
    )
    notification_type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    @property
    def natural_time(self):
        return naturaltime(self.created_at)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return "From: {} - To: {}".format(self.creator, self.to)