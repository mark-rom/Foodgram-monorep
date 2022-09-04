from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ['pk', 'username',
                    'first_name', 'last_name',
                    'email', 'password'
                    ]
    search_fields = ['username', 'email']
    list_filter = ['username', 'email']
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Subscription)
