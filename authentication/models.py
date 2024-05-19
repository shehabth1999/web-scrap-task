from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    # just hold over the default user model

    # add more fields here
    pass


      