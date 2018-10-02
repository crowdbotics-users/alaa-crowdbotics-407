from django.db import models

# Create your models here.


class Profile(models.Model):
    """ Profile Model """
    MALE = 'M'
    FEMALE = 'F'
    NOT_SPECIFIED = "N"

    GENDER_CHOICES = {
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (NOT_SPECIFIED, 'Not specified'),
    }

    owner = models.OneToOneField('auth.User', on_delete=models.PROTECT)
    profile_image = models.ImageField(null=True)
    website = models.URLField(null=True)
    bio = models.TextField(null=True)
    phone = models.CharField(max_length=140, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=NOT_SPECIFIED)
    followers = models.ManyToManyField("auth.User", blank=True)
    following = models.ManyToManyField("auth.User", blank=True)

    def __str__(self):
        return self.owner.username

    @property
    def post_count(self):
        return self.images.all().count()

    @property
    def followers_count(self):
        return self.followers.all().count()

    @property
    def following_count(self):
        return self.following.all().count()