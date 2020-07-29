from django.contrib import admin
from .models import Turn, User, Store

admin.site.register([User, Store, Turn])
