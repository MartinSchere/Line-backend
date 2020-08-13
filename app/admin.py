from django.contrib.gis import admin

from .models import Turn, User, Store


class TurnInline(admin.TabularInline):
    model = Turn


class StoreAdmin(admin.ModelAdmin):
    inlines = [
        TurnInline,
    ]


admin.site.register([User, Turn])
admin.site.register(Store, StoreAdmin)
