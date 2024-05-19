from django.contrib import admin
from authentication.models import CustomUser as User


admin.site.register(User)
