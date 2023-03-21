from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    def save(self, *args, **kwargs):
        # Save the user to the database
        super().save(*args, **kwargs)

        # Create profile if it doesn't exist
        if not hasattr(self, 'profile'):
            Profile.objects.create(user=self)

class Chat(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    child_name = models.CharField(max_length=50, blank=False, null=False)
    robot_name = models.CharField(max_length=50, blank=False, null=False)
    mom_name = models.CharField(max_length=50, blank=True)
    dad_name = models.CharField(max_length=50, blank=True)
    pet_name = models.CharField(max_length=50, blank=True)

    # Adding this property makes it easy to check if a profile is complete.
    # So the view can redirect to the profile page if it's not complete.
    @property
    def is_complete(self):
        # Modify this condition as needed, depending on which fields are required for a complete profile.
        return all([self.child_name, self.robot_name])

