from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Post, Comment

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'get_favorite_food', 'get_address', 'is_staff', 'is_active', 'date_joined')

    def get_favorite_food(self, obj):
        return obj.first_name  # Assuming favorite_food is stored in first_name

    def get_address(self, obj):
        return obj.last_name  # Assuming address is stored in last_name

    get_favorite_food.short_description = 'Favorite Food'  # Column header
    get_address.short_description = 'Address'  # Column header

# Unregister the default User admin
admin.site.unregister(User)

# Register the custom User admin
admin.site.register(User, CustomUserAdmin)

# Register the Post model
admin.site.register(Post)

# Register the Comment model
admin.site.register(Comment)
