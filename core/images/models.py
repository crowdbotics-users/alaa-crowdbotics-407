from django.db import models
from taggit.managers import TaggableManager
from django.contrib.humanize.templatetags.humanize import naturaltime
from imagekit.models import ProcessedImageField
from imagekit.processors import Transpose

# Create your models here.
from core.abstract_models import TimeStampedModel
from core.accounts.models import Profile


class Image(TimeStampedModel):
    """ Image Model """
    file = ProcessedImageField(processors=[Transpose()], format="JPEG", options={"quality": 50})
    restaurant = models.TextField()
    dish = models.TextField()
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, related_name="images")
    tags = TaggableManager()
    # latitude = models.DecimalField(max_digits=19, decimal_places=16, null=True)
    # longitude = models.DecimalField(max_digits=19, decimal_places=16, null=True)

    @property
    def like_count(self):
        return self.likes.all().count()

    @property
    def comment_count(self):
        return self.comments.all().count()

    @property
    def natural_time(self):
        return naturaltime(self.created_at)

    @property
    def is_vertical(self):
        if self.file.width < self.file.height:
            return True
        else:
            return False

    def __str__(self):
        return "{} - {}".format(self.restaurant, self.dish)

    class Meta:
        ordering = ["-created_at"]


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
